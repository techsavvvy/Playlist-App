import flask
import os

from flask import Blueprint
from flask import Flask, render_template
from flask_wtf import FlaskForm
from flask_login import current_user, login_required
# from flask import jsonify

from app import db
from app.playlist.forms import PlaylistCreateForm
from app.playlist.models import Playlist
from app.playlist.serializer import get_playlist_serialized


playlist=Blueprint('playlist', __name__, url_prefix='/')

@playlist.route('/dashboard')
@login_required
def dashboard():
    form=PlaylistCreateForm()
    queryset = Playlist.query.filter_by(user_id=current_user.id)
    serialized = [get_playlist_serialized(item) for item in queryset]
    # res = jsonify(res=serialized)
    return render_template('dashboard.html', dict=serialized, form=form)
