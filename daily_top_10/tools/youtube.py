import time
import pprint
import csv
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from pyyoutube import Api
from dateutil import parser
from dotenv import dotenv_values

def pretty_print(val):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(val)

def pyyoutube_call_oauth2():
    api = Api(client_id=config['YOUTUBE_CLIENT_ID'], client_secret=config['YOUTUBE_CLIENT_SECRET'])
    url = api.get_authorization_url()
    print(url)

def generate_oauth2_token():
    api = Api(client_id=config['YOUTUBE_CLIENT_ID'], client_secret=config['YOUTUBE_CLIENT_SECRET'])
    access_token = api.generate_access_token(authorization_response=config['PYYOUTUBE_RESPONSE_URL'])
    print(access_token)

def get_playlist():
    playlists = []
    api = Api(access_token=config['YOUTUBE_OAUTH2_ACCESS_TOKEN'])
    playlists_by_mine = api.get_playlists(mine=True, count=50)
    playlists.append(playlists_by_mine)
    next_page_token = playlists_by_mine.nextPageToken
    while next_page_token:
        print(f"token {next_page_token}")
        next_playlist = api.get_playlists(mine=True, count=50, page_token=next_page_token)
        next_page_token = next_playlist.nextPageToken
    result = {}
    for pl in playlists:
        result.update({x.snippet.title: x.id for x in pl.items})
    print(len(result))
    # print(result)
    return result

def get_playlist_items(playlist_id):
    api = Api(access_token=config['YOUTUBE_OAUTH2_ACCESS_TOKEN'])
    playlist_items = api.get_playlist_items(playlist_id=playlist_id, count=None)
    for item in playlist_items.items:
        video_title = item.snippet.title
        video_id = item.snippet.resourceId.videoId

def init_oauth2():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server()
    return googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    
def youtube_create_playlist(youtube, title):
    request = youtube.playlists().insert(
        part="snippet",
        body={
          "snippet": {
            "title": title
          }
        }
    )
    response = request.execute()
    return response['id']

def youtube_add_song_to_playlist(youtube, playlist_id,video_id):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
          "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
              "kind": "youtube#video",
              "videoId": video_id
            }
          }
        }
    )
    response = request.execute()

def search(track, artist):
    api = Api(access_token=config['YOUTUBE_OAUTH2_ACCESS_TOKEN'])
    r = api.search_by_keywords(q=f"{track} {artist}", search_type=["video"], count=1, limit=1)
    item = r.items[0]
    # print(f"track: {track} artist: {artist}\n{item.snippet.title}: {item.id.videoId} \n https://www.youtube.com/watch?v={item.id.videoId} \n\n")
    return item.id.videoId

def search_multiple_songs(songs):
    results = []
    songs.reverse()
    for song in songs:
        id = search(song[2],song[3])
        results.append(id)
    return results

def group_spotified_input():
    daily_top_tens = {}
    with open('../raw_data/spotified_input.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for idx, row in enumerate(csv_reader):
            if idx != 0:
                data = (row[0], row[1], row[2], row[3])
                if row[0] not in daily_top_tens:
                    daily_top_tens[row[0]] = [data]
                else:
                    daily_top_tens[row[0]].append(data)
    return daily_top_tens

def top_tens_to_playlist(top_tens, limit = 1):
    current_playlists = get_playlist()
    currently_added = 0
    for ten in top_tens:
        print(f"AMDG currently_added {currently_added}")
        iso_date = parser.parse(ten)
        formatted_date = iso_date.strftime("%B %d, %Y")
        title = f'MYX Daily Top 10 - {formatted_date}'
        if currently_added == limit:
            raise Exception(f"Sorry,")
        if title in current_playlists:
            print(f"AMDG {title} exists already")
            continue
            playlist_id = current_playlists[title]
            song_ids = search_multiple_songs(top_tens[ten])
            for s_id in song_ids:
                youtube_add_song_to_playlist(youtube, playlist_id,s_id)
                time.sleep(2)
            # get_playlist_items(playlist_id=playlist_id)
        else:
            playlist_id = youtube_create_playlist(youtube,title)
            print(f"playlist {title} created")
            time.sleep(3)
            song_ids = search_multiple_songs(top_tens[ten])
            for s_id in song_ids:
                youtube_add_song_to_playlist(youtube, playlist_id,s_id)
                time.sleep(2)
            print("---all songs added to playlist---")
            song_ids.reverse()
            reversed_top_ten = top_tens[ten]
            reversed_top_ten.reverse()
            for index in range(len(reversed_top_ten)):
                youtube_id = song_ids[index]
                song_position = reversed_top_ten[index][1]
                spotified_to_youtubed(ten, song_position, youtube_id)
            currently_added += 1


def spotified_to_youtubed(date, position, youtube_id, mode="a"):
    youtubed_input = open('../raw_data/youtubed_input.csv', mode)
    writer = csv.writer(youtubed_input)
    with open('../raw_data/spotified_input.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for idx, row in enumerate(csv_reader):
            if idx != 0:
                if row[0] == date and row[1] == position:
                    youtubed_row = spotify_to_youtube_row(row, youtube_id)
                    writer.writerow(youtubed_row)
                    youtubed_input.close()
                    return row
            elif mode == "w" and idx == 0:
                writer.writerow(["date", "position",
                                 "track_name", "artists_name",
                                 "track_link", "youtube_link",
                                "album_name", "album_release_date",
                                  "artists_link",
                                 "album_link", "duration_ms",
                                 "popularity", "explicit",
                                 "danceability", "energy",
                                 "key", "loudness",
                                 "mode", "speechiness",
                                 "acousticness", "instrumentalness",
                                 "liveness", "valence",
                                 "tempo", "time_signature",
                                 "track_id", "album_id"])
    youtubed_input.close()
                
def spotify_to_youtube_row(row, youtube_id):
    youtube_link = f"https://www.youtube.com/watch?v={youtube_id}"
    date = row[0]
    position = row[1]
    track_name = row[2]
    artists_name = row[3]
    album_name = row[4]
    album_release_date = row[5]
    track_link = row[6]
    artists_link = row[7]
    album_link = row[8]
    duration_ms = row[9]
    popularity = row[10]
    explicit = row[11]
    danceability = row[12]
    energy = row[13]
    key = row[14]
    loudness = row[15]
    mode = row[16]
    speechiness = row[17]
    acousticness = row[18]
    instrumentalness = row[19]
    liveness = row[20]
    valence = row[21]
    tempo = row[22]
    time_signature = row[23]
    track_id = row[24]
    album_id = row[25]
    return (date,position,
            track_name,artists_name,
            track_link,youtube_link,
            album_name,album_release_date,
            artists_link,
            album_link,duration_ms,
            popularity,explicit,
            danceability,energy,
            key,loudness,
            mode,speechiness,
            acousticness,instrumentalness,
            liveness,valence,
            tempo,time_signature,
            track_id,album_id)

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "secret.json"

config = dotenv_values(".env")

# pyyoutube section
# pyyoutube_call_oauth2()
# generate_oauth2_token()

# youtube section
# youtube = init_oauth2()


print("AMDG")
# tens = group_spotified_input()
# top_tens_to_playlist(tens, limit=6)

#use pyyoutube to search
#use raw youtube python to create playlist and add tracks