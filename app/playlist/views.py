import flask
import os

from flask import Blueprint
from flask import request
from flask import Flask, render_template, redirect, url_for, flash, Response
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from flask_sqlalchemy  import SQLAlchemy
from flask_login import current_user, login_required
from flask import jsonify

from app import db
from app.playlist.forms import PlaylistCreateForm, CollectionsCreateForm
from app.playlist.models import Playlist
from app.playlist.models import Collection
from app.playlist.serializer import get_playlist_serialized, get_collection_serialized
from app.playlist.functions import is_valid_file, modify_file_name, check_file_name_already_exist
from app import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from marshmallow import Serializer, fields, pprint

from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.utils import secure_filename

playlist=Blueprint('playlist', __name__, url_prefix='/')

@playlist.route('/dashboard')
@login_required
def dashboard():
    form=PlaylistCreateForm()
    queryset = Playlist.query.filter_by(user_id=current_user.id)
    serialized = [get_playlist_serialized(item) for item in queryset]
    # res = jsonify(res=serialized)
    return render_template('dashboard.html', dict=serialized, form=form)

@playlist.route('/playlist', methods=['GET', 'POST', 'DELETE'])
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
def playlist_delete():
    queryset = Playlist.query.get(request.form['id'])
    db.session.delete(queryset)
    db.session.commit()

    return redirect(url_for('playlist.dashboard'))

@playlist.route('/playlist/<id>', methods=['GET', 'POST', 'DELETE'])
def collection(id):
    form=CollectionsCreateForm(csrf_enabled=False)
    if flask.request.method == 'POST':

        if form.validate_on_submit():
            print(check_file_name_already_exist(form.file.data.filename,id))
            if check_file_name_already_exist(form.file.data.filename,id):
                flash("Oops! You have already uploaded a music with same filename in this playlist. Please rename the file and try again.")
            else:     
                new_collection = Collection(
                    title=form.title.data, artist=form.artist.data, 
                    album=form.album.data, playlist_id=id, file=modify_file_name(form.file.data.filename,id)
                )
                file=form.file.data
                if(form.file.data and is_valid_file(form.file.data.filename)):
                    filename = secure_filename(modify_file_name(file.filename,id))
                    file.save(os.path.join('app/audio', filename))

                    db.session.add(new_collection)
                    db.session.commit()
                else:
                    flash("Oops! we allow only mp3 files to be uploaded") 

            return redirect(url_for('playlist.collection', id=id))

    if flask.request.method == 'GET':
        collection_queryset = Collection.query.filter_by(playlist_id=id)
        collection_serialized = [item.__dict__ for item in collection_queryset]
        playlist_queryset = Playlist.query.get(id)
        playlist_serialized = get_playlist_serialized(playlist_queryset)
        print(playlist_serialized)
        return render_template(
            'playlist-view.html', coll_dict=collection_serialized, 
            play_dict=playlist_serialized, form=form
        )

@playlist.route('/collection/delete',methods=['POST'])
def collection_delete():
    print(request.form['id'])
    queryset = Collection.query.get(request.form['id'])
    print(queryset.playlist_id)
    db.session.delete(queryset)
    db.session.commit()

    return redirect(url_for('playlist.collection', id=queryset.playlist_id))

@playlist.route('playlist/<pid>/stream/<sid>', methods=['POST', 'GET'])
def stream(pid, sid):
    print(pid,sid)
    collection_queryset = Collection.query.get(sid)
    collection_serialized = get_collection_serialized(collection_queryset)
    playlist_queryset = Playlist.query.get(pid)
    playlist_serialized = get_playlist_serialized(playlist_queryset)
    print(playlist_serialized,collection_queryset)
    return render_template(
        'stream.html', coll_dict=collection_queryset.__dict__, 
        play_dict=playlist_serialized
    )

# For testing purpose, will be modifies once audio retrieve is implemented
@playlist.route("col/mp3")
def streamogg():
    def generate():
        with open(os.path.join('app/audio/', "file_example_MP3_700KB___2___.mp3"), "rb") as fogg:
            print()
            data = fogg.read(1024)
            while data:
                yield data
                data = fogg.read(1024)
    return Response(generate(), mimetype="audio/ogg")