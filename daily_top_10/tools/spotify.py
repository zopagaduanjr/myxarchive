import spotipy
import pprint
import csv
import time
from dotenv import dotenv_values
from spotipy.oauth2 import SpotifyClientCredentials

# TODOS:
# create playlist based on reading spotified csv file, particularly grouping csv into date
# search if playlist already exists by date == playlist name, if not create it
# check if api handles duplicate add track to playlist


# function station
def pretty_print(val):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(val)


def get_artist_name(artist):
    return artist['name']


def get_artist_link(artist):
    return artist['external_urls']['spotify']


def search_item(track, artist):
    search_q = f'track:{track} artist:{artist}'
    url_encoded_search_q = search_q
    while True:
        results = sp.search(q=url_encoded_search_q, market="PH")
        for idx, track_result in enumerate(results['tracks']['items']):
            track_name = track_result['name']
            track_id = track_result['id']
            artists = list(map(get_artist_name, track_result['artists']))
            print((idx)+1, track_name, artists, track_id)
            if track.lower() == track_name.lower() and artist.lower() == artists[0].lower():
                print(f'\neureka! id: {track_id}\n')
                time.sleep(5)
                return track_id
        time.sleep(5)
        # os.system('clear')


def get_track(track_id):
    return sp.track(track_id=track_id, market="PH")


def get_track_features(track_id):
    return sp.audio_features([track_id])


def get_stats(data_list):
    track_id = search_item(data_list[2], data_list[3])

    track = get_track(track_id)
    track_name = track['name']
    artists = ', '.join(list(map(get_artist_name, track['artists'])))
    track_link = track['external_urls']['spotify']
    artists_link = ', '.join(list(map(get_artist_link, track['artists'])))
    album = track['album']['name']
    album_link = track['album']['external_urls']['spotify']
    album_release_date = track['album']['release_date']
    album_id = track['album']['id']
    duration_ms = track['duration_ms']
    explicit = track['explicit']
    popularity = track['popularity']

    track_features = get_track_features(track_id)[0]
    danceability = track_features['danceability']
    energy = track_features['energy']
    key = track_features['key']
    loudness = track_features['loudness']
    mode = track_features['mode']
    speechiness = track_features['speechiness']
    acousticness = track_features['acousticness']
    instrumentalness = track_features['instrumentalness']
    liveness = track_features['liveness']
    valence = track_features['valence']
    tempo = track_features['tempo']
    time_signature = track_features['time_signature']
    new_data = (data_list[0], data_list[1], track_name,
                artists, album, album_release_date,
                track_link, artists_link, album_link,
                duration_ms, popularity, explicit,
                danceability, energy, key,
                loudness, mode, speechiness,
                acousticness, instrumentalness,
                liveness, valence, tempo, time_signature,
                track_id, album_id)
    return new_data


def input_to_spotified_input():
    spotified_input = open('../raw_data/spotified_input.csv', 'w')
    writer = csv.writer(spotified_input)
    with open('../raw_data/input.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for idx, row in enumerate(csv_reader):
            if idx != 0:
                new_data = get_stats(row)
                writer.writerow(new_data)
            else:
                writer.writerow(["date", "position",
                                 "track_name", "artists_name",
                                "album_name", "album_release_date",
                                 "track_link", "artists_link",
                                 "album_link", "duration_ms",
                                 "popularity", "explicit",
                                 "danceability", "energy",
                                 "key", "loudness",
                                 "mode", "speechiness",
                                 "acousticness", "instrumentalness",
                                 "liveness", "valence",
                                 "tempo", "time_signature",
                                 "track_id", "album_id"])
    spotified_input.close()


    # initialization station
config = dotenv_values(".env")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=config['SPOTIFY_CLIENT_ID'],
    client_secret=config['SPOTIFY_CLIENT_SECRET']))
print("AMDG, initialization success")


# testing station
input_to_spotified_input()
