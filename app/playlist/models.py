from app import db

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_name = db.Column(db.String(50))
    genre = db.Column(db.String(50))
    description = db.Column(db.String(500))
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    artist = db.Column(db.String(50))
    album = db.Column(db.String(50))
    file = db.Column(db.String(99))
    playlist_id = db.Column(db.BigInteger, db.ForeignKey('playlist.id', ondelete='CASCADE'), nullable=False)