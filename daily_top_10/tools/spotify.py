import spotipy
import urllib
import pprint
from dotenv import dotenv_values
from spotipy.oauth2 import SpotifyClientCredentials

# TODOS:
# search track id of track + artist query
# search for audio analysis and audio features of the said track
# return it as tuple


# function station
def pretty_print(val):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(val)


def get_artist_name(artist):
    return artist['name']


def search_item(track, artist):
    search_q = f'track:{track} artist:{artist}'
    url_encoded_search_q = urllib.parse.quote(search_q)
    results = sp.search(q=url_encoded_search_q, limit=24, market="ph")
    for idx, track_result in enumerate(results['tracks']['items']):
        track_name = track_result['name']
        track_id = track_result['id']
        artists = list(map(get_artist_name, track_result['artists']))
        print(idx, track_name, artists, track_id)
        if track.lower() == track_name.lower() and artist.lower() == artists[0].lower():
            print(f'\neureka! id: {track_id}\n')
            return track_id
    return False


def get_track(track_id):
    return sp.track(track_id=track_id, market="ph")


# initialization station
config = dotenv_values(".env")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=config['SPOTIFY_CLIENT_ID'],
    client_secret=config['SPOTIFY_CLIENT_SECRET']))
print("AMDG, initialization success")


# testing station
track_id = search_item("Ikaw", "Sarah Geronimo")

# track = get_track(track_id)

result = sp.audio_features([track_id])
print("AMDG search track features")
pretty_print(result)
