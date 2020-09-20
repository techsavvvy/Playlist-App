import flask
from app import app
import os
import flask_whooshalchemyplus

from flask import Blueprint
from flask import request
from flask import Flask, render_template, redirect, url_for, flash, Response
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from flask_sqlalchemy  import SQLAlchemy
from flask_login import current_user, login_required
from flask import jsonify

from app import db
from app.playlist.forms import PlaylistCreateForm, CollectionsCreateForm, CollectionSearchForm
from app.playlist.models import Playlist
from app.playlist.models import Collection
from app.playlist.serializer import get_playlist_serialized, get_collection_serialized
from app.playlist.functions import is_valid_file, get_modified_file_name, check_file_name_already_exist, delete_file_from_audio_directory
from app import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from marshmallow import Serializer, fields, pprint

from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.utils import secure_filename

playlist=Blueprint('playlist', __name__, url_prefix='/')
flask_whooshalchemyplus.whoosh_index(app, Collection)

@playlist.route('/dashboard')
@login_required
def dashboard():
    form=PlaylistCreateForm()
    queryset = Playlist.query.filter_by(user_id=current_user.id)
    serialized = [get_playlist_serialized(item) for item in queryset]
    # res = jsonify(res=serialized)
    return render_template('dashboard.html', dict=serialized, form=form)

@playlist.route('/playlist', methods=['GET', 'POST', 'DELETE'])
@login_required
def playlistcreate():
    form=PlaylistCreateForm()
    if flask.request.method == 'POST':
        form=PlaylistCreateForm()
        if form.validate_on_submit():
            new_playlist = Playlist(
                genre=form.genre.data, playlist_name=form.name.data, 
                description=form.description.data, user_id=current_user.id
            ) 
            db.session.add(new_playlist)
            db.session.commit()

    return redirect(url_for('playlist.dashboard'))

@playlist.route('/playlist/delete', methods=['POST'])
@login_required
def playlist_delete():
    coll_queryset = Collection.query.filter_by(playlist_id=request.form['id'])
    print(coll_queryset.count())
    try:
        if coll_queryset.count() > 1:
            for quer in coll_queryset:
                db.session.delete(quer)
                db.session.commit()
                delete_file_from_audio_directory(quer)
        else:
                db.session.delete(coll_queryset[0])
                db.session.commit()
                delete_file_from_audio_directory(coll_queryset[0])
    except Exception as e:
        flash("Oops unable to delete at the moment. Please try again later")
    queryset = Playlist.query.get(request.form['id'])
    db.session.delete(queryset)
    db.session.commit()

    return redirect(url_for('playlist.dashboard'))

@playlist.route('/playlist/<id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def collection(id):
    form=CollectionsCreateForm(csrf_enabled=False)
    formc=CollectionSearchForm(csrf_enabled=False)
    if flask.request.method == 'POST':

        if form.validate_on_submit():
            if check_file_name_already_exist(form.file.data.filename,id):
                flash("Oops! You have already uploaded a music with same filename in this playlist. Please rename the file and try again.")
            else:     
                new_collection = Collection(
                    title=form.title.data, artist=form.artist.data, 
                    album=form.album.data, playlist_id=id, file=get_modified_file_name(form.file.data.filename,id)
                )
                file=form.file.data
                if(form.file.data and is_valid_file(form.file.data.filename)):
                    filename = secure_filename(get_modified_file_name(file.filename,id))
                    file.save(os.path.join('app/audio', filename))
                    
                    db.session.add(new_collection)
                    db.session.commit()
                else:
                    flash("Oops! we allow only mp3 files to be uploaded") 

            return redirect(url_for('playlist.collection', id=id))

    if flask.request.method == 'GET':
        collection_queryset = Collection.query.filter_by(playlist_id=id)
        if(request.args and request.args['search']):
            search_queryset = Collection.query.filter_by(playlist_id=id).whoosh_search(request.args['search'])
            if search_queryset.count() > 0:
                collection_queryset = Collection.query.whoosh_search(request.args['search'])
            else:
                flash("Oops! Song not found. Try again with different keyword")
        collection_serialized = [item.__dict__ for item in collection_queryset]
        playlist_queryset = Playlist.query.get(id)
        playlist_serialized = get_playlist_serialized(playlist_queryset)
        if playlist_queryset and (playlist_queryset.user_id==current_user.id):
            return render_template(
                'playlist-view.html', coll_dict=collection_serialized, 
                play_dict=playlist_serialized, form=form, formc=formc
            )
        else:
            return redirect(url_for('playlist.dashboard'))

@playlist.route('/search/<id>')
@login_required
def search_collection(id):
    formc=CollectionSearchForm(csrf_enabled=False)
    form=CollectionsCreateForm(csrf_enabled=False)
    collection_queryset = Collection.query.filter_by(playlist_id=id)
    collection_serialized = [item.__dict__ for item in collection_queryset]
    playlist_queryset = Playlist.query.get(id)
    playlist_serialized = get_playlist_serialized(playlist_queryset)
    return render_template(
        'playlist-view.html', coll_dict=collection_serialized, 
        play_dict=playlist_serialized, form=form, formc=formc
    )

@playlist.route('/collection/delete',methods=['POST'])
@login_required
def collection_delete():
    queryset = Collection.query.get(request.form['id'])
    db.session.delete(queryset)
    db.session.commit()
    os.remove(os.path.join('app/audio/', str(queryset.file)))
    return redirect(url_for('playlist.collection', id=queryset.playlist_id))

@playlist.route('playlist/<pid>/stream/<sid>', methods=['POST', 'GET'])
@login_required
def stream(pid, sid):
    collection_queryset = Collection.query.get(sid)
    collection_serialized = get_collection_serialized(collection_queryset)
    playlist_queryset = Playlist.query.get(pid)
    playlist_serialized = get_playlist_serialized(playlist_queryset)
    return render_template(
        'stream.html', coll_dict=collection_queryset.__dict__, 
        play_dict=playlist_serialized
    )

@playlist.route("col/mp3/<file>")
@login_required
def streammp3(file):
    def generate():
        with open(os.path.join('app/audio/', str(file)), "rb") as mp3:
            data = mp3.read(1024)
            while data:
                yield data
                data = mp3.read(1024)
    return Response(generate(), mimetype="audio/mp3")