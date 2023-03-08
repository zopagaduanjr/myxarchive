import spotipy
import pprint
import csv
import time
import string
from dotenv import dotenv_values
from spotipy.oauth2 import SpotifyOAuth
from dateutil import parser
from csv_helper import scrape_to_input

# TODO:
# potential problems in youtube: cueshe, beyonce uses weird letter é - solution use unidecode
# potential future problem: equivalent_track_name with same name
# continue until 2014
# youtube api time


# function station


def pretty_print(val):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(val)


def get_artist_name(artist):
    return artist['name']


def get_artist_link(artist):
    return artist['external_urls']['spotify']


def get_playlist_name(playlist):
    return playlist['name']


def search_item(track, artist, stop=False):
    if spotify_track_unsupported.get(track.lower()) == artist.lower():
        return None
    edge_case_correct_track = spotify_correct_track.get((track.lower(), artist.lower()))
    if edge_case_correct_track:
        return edge_case_correct_track

    equivalent_track, equivalent_artist = spotify_track_equivalent.get(
        track.lower()) or (track, artist)

    cleaned_track = equivalent_track.replace("\'", "").replace("\"", "")
    search_q = f'track:{cleaned_track} artist:{equivalent_artist}'
    url_encoded_search_q = search_q
    limit = 10
    while True:
        results = sp.search(q=url_encoded_search_q, limit=limit, market="PH")
        correct_track_id = None
        album_oldest_year = None
        for idx, track_result in enumerate(results['tracks']['items']):
            track_name = track_result['name']
            track_id = track_result['id']
            url = track_result['external_urls']['spotify']
            artists = list(map(get_artist_name, track_result['artists']))
            print(
                f"{(idx)+1}. track={track_name} artist={artists} track_id={track_id} url={url}")
            if equivalent_track.lower() == track_name.lower() and equivalent_artist.lower() == artists[0].lower():
                album_release_date = int(
                    track_result['album']['release_date'][:4])
                if album_oldest_year is None or album_release_date < album_oldest_year:
                    album_oldest_year = album_release_date
                    correct_track_id = track_id
                time.sleep(1)
        if correct_track_id is not None:
            print(f'\neureka! id: {correct_track_id}\n')
            return correct_track_id
        if stop:
            raise Exception(f"Sorry, can't search {search_q}")


def get_track(track_id):
    return sp.track(track_id=track_id, market="PH")


def get_track_features(track_id):
    return sp.audio_features([track_id])


def get_stats(data_list):
    track_id = search_item(data_list[2], data_list[3])

    if track_id is None:
        return data_list

    track = get_track(track_id)
    track_name = track['name']
    artists = ', '.join(list(map(get_artist_name, track['artists'])))
    if data_list[2].lower() in spotify_track_equivalent:
        track_name = string.capwords(data_list[2])
        artists = string.capwords(data_list[3])
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


def input_to_spotified_input_write(mode="w"):
    spotified_input = open('../raw_data/spotified_input.csv', mode)
    writer = csv.writer(spotified_input)
    with open('../raw_data/input.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for idx, row in enumerate(csv_reader):
            if idx != 0:
                track_date_exist = is_track_date_in_spotified_input(row[2], row[0])
                if not track_date_exist:
                    track_exist = is_track_in_spotified_input(row[2],row[3])
                    if track_exist is not None:
                        print(f"AMDG reusing track {row[2]}")
                        reuse_track = list(track_exist)
                        reuse_track[0] = row[0]
                        reuse_track[1] = row[1]
                        writer.writerow(tuple(reuse_track))
                    else:
                        new_data = get_stats(row)
                        writer.writerow(new_data)
            elif mode == "w" and idx == 0:
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


def group_spotified_input():
    daily_top_tens = {}
    with open('../raw_data/spotified_input.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for idx, row in enumerate(csv_reader):
            track_id = row[24] if 24 < len(row) else None
            if idx != 0 and track_id is not None:
                data = (row[0], row[1], row[2], track_id)
                if row[0] not in daily_top_tens:
                    daily_top_tens[row[0]] = [data]
                else:
                    daily_top_tens[row[0]].append(data)
    return daily_top_tens


def create_playlists(top_tens, delete=False, skip=False):
    user_id = sp.me()['id']
    offset = 0
    current_playlists = sp.current_user_playlists(offset=offset)
    playlist_names = {}
    while len(current_playlists['items']) > 0:
        playlist_names.update({x['name']: x['id'] for x in current_playlists['items']})
        offset += 50
        current_playlists = sp.current_user_playlists(offset=offset)
    for ten in top_tens:
        tracks = list(map(lambda n: n[3], top_tens[ten]))
        tracks.reverse()
        iso_date = parser.parse(ten)
        formatted_date = iso_date.strftime("%B %d, %Y")
        title = f'MYX Daily Top 10 - {formatted_date}'
        if title not in playlist_names:
            response = sp.user_playlist_create(user=user_id, name=title)
            playlist_id = response['id']
            sp.user_playlist_add_tracks(user_id, playlist_id, tracks)
        elif not skip:
            playlist_id = playlist_names[title]
            add_tracks_to_existing_playlist(user_id, playlist_id, tracks, delete=delete)


def add_tracks_to_existing_playlist(user_id, playlist_id, tracks, delete=False):
    current_tracks = sp.playlist_items(playlist_id, market="PH")
    current_track_ids = list(
        map(lambda n: n['track']['id'], current_tracks['items']))
    if delete:
        sp.user_playlist_remove_all_occurrences_of_tracks(user_id,playlist_id,current_track_ids)
        sp.user_playlist_add_tracks(user_id, playlist_id, tracks)
    else:
        for idx, track in enumerate(tracks):
            if track not in current_track_ids:
                if track is not None:
                    sp.user_playlist_add_tracks(
                        user_id, playlist_id, [track], idx)


def check_input_searchability():
    with open('../raw_data/input.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for idx, row in enumerate(csv_reader):
            if idx != 0:
                if not is_track_date_in_spotified_input(row[2], row[0]):
                    result = search_item(row[2], row[3], stop=True)
                    if result == "break":
                        break


def is_track_date_in_spotified_input(track, date):
    with open('../raw_data/spotified_input.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[2].lower() == track.lower() and row[0] == date:
                return True
    return False

def is_track_in_spotified_input(track, artist):
    equivalent_track, equivalent_artist = spotify_track_equivalent.get(track.lower()) or (track, artist)
    with open('../raw_data/spotified_input.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[2].lower() == equivalent_track.lower() and equivalent_artist.lower() in row[3].lower().split(","):
                return row
    return None


def get_current_playlist():
    offset = 0
    current_playlists = sp.current_user_playlists(offset=offset)
    playlist_names = {}
    while len(current_playlists['items']) > 0:
        playlist_names.update({x['name']: x['id'] for x in current_playlists['items']})
        offset += 50
        current_playlists = sp.current_user_playlists(offset=offset)
    print(f'current user playlist length {len(playlist_names)}')
    print(playlist_names)

# initialization station
config = dotenv_values(".env")
scope = "user-read-private,playlist-modify-public,ugc-image-upload"
# lazy way of searching, keys should be lower case

spotify_track_equivalent = {
    "make it good": ("Make It Good - Radio Edit", "a1"),
    "i don't want to be your friend": ("I Don't Want to Be Your Friend - Live", "nina"),
    "tilt ya head back": ("Tilt Ya Head Back - Album Version / Explicit", "nelly"),
    "love moves in mysterious ways": ("Love Moves in Mysterious Ways - Live", "nina"),
    "check on it": ("Check On It (feat. Bun B & Slim Thug)", "Beyoncé"),
    "i'll never get over you getting over me": ("I'll Never Get Over You Getting Over Me - Live", "mymp"),
    "carry my love": ("Carry My Love - Amor Cobarde", "sarah geronimo"),
    "i'm coming": ("I′m Coming (Feat. Tablo)", "rain"),
    "you are the music in me": ("you are the music in me", "troy"),
    "no air": ("No Air (feat. Chris Brown)", "jordin sparks"),
    "honesty": ("Honestly - Live", "rachelle ann go"),
    "4 minutes": ("4 Minutes (feat. Justin Timberlake & Timbaland)", "madonna"),
    "all i have": ("All I Have (feat. LL Cool J)", "jennifer lopez"),
    "how do you sleep?": ("How Do You Sleep? - Radio Edit Remix", "jesse mccartney"),
    "diamond shotgun": ("Diamond Shotgun (Lock & Load)", "chicosci"),
    "higante": ("Higante (feat. Hardware Syndrome)", "francism"),
    "hurricanes and suns": ("Hurricanes And Suns - New Track 2009", "tokio hotel"),
    "walang natira": ("Walang Natira (feat. Sheng Belmonte)", "gloc 9"),
    "next to you": ("Next To You (feat. Justin Bieber)","chris brown")
}

spotify_track_unsupported = {
    "bright lights": "billy crawford",
    "steamy nights": "billy crawford",
    "jeepney": "kala",
    "dale candela": "gerald anderson",
    "7 black roses": "chicosci",
    "radio": "amber davis",
    "gotta go my own way": "nikki gil",
    "last look": "chicosci",
    "hear my heart": "nikki gil",
    "the search is over": "rachelle ann go",
    "just stand up!": "artists stand up to cancer",
    "blue tomorrow": "super junior-m",
    "bata": "bbs",
    "wala na tayo": "bbs",
    "pawiin": "bbs",
}

spotify_correct_track = {
    ("a very special love", "sarah geronimo"): "3eAM3mpO1Up7TPNDcrGU5y",
    ("that should be me (remix)", "justin bieber"): "42wmRq3kfUUuyszlkWQbPS"
    
}
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(
    client_id=config['SPOTIFY_CLIENT_ID'],
    client_secret=config['SPOTIFY_CLIENT_SECRET'], scope=scope,
    redirect_uri="http://127.0.0.1:9090"))

# testing station
print("AMDG")

# scrape_to_input()
# check_input_searchability()

# search_item("walang natira", "gloc 9", True)

# input_to_spotified_input_write("w")
# input_to_spotified_input_write("a")

# tens = group_spotified_input()
# create_playlists(tens, delete=False, skip=True)

# get_current_playlist()
