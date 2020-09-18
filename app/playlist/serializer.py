from marshmallow import Serializer, fields, pprint
from app.playlist.models import Playlist

class PlaylistSerializer(Serializer):
    class Meta:
        fields=('id', 'playlist_name', 'genre', 'description', 'user_id')
        model=Playlist

def get_playlist_serialized(playlist):
    return PlaylistSerializer(playlist).data