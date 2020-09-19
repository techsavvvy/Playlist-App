from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired

class PlaylistCreateForm(FlaskForm):
    name = StringField('Playlist Name', validators=[InputRequired(), Length(max=99)])
    genre = StringField('Genre', validators=[InputRequired(), Length(min=1, max=99)])
    description = StringField('Description', validators=[InputRequired(), Length(min=1, max=99)])

class CollectionsCreateForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(message="dsfgsfas"), Length(min=1, max=99)])
    artist = StringField('Artist', validators=[InputRequired(), Length(min=1, max=99)])
    album = StringField('Album', validators=[InputRequired(), Length(min=1, max=99)])
    file = FileField('Upload mp3', validators=[FileRequired()])
