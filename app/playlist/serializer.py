from marshmallow import Serializer, fields, pprint
from app.playlist.models import Playlist, Collection

class PlaylistSerializer(Serializer):
    class Meta:
        fields=('id', 'playlist_name', 'genre', 'description', 'user_id')
        model=Playlist

def CollectionSerializer(Serializer):
    class Meta:
        fields=('title', 'album', 'artist','id','playlist_id')
        model=Collection

def get_playlist_serialized(playlist):
    return PlaylistSerializer(playlist).data

def get_collection_serialized(collection):
    if CollectionSerializer(collection):
        return CollectionSerializer(collection).data