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
    api = Api(access_token=config['YOUTUBE_OAUTH2_ACCESS_TOKEN'])
    playlists_by_mine = api.get_playlists(mine=True, count=50)
    #TODO: use nextPageToken if playlist exceed 50
    # pretty_print(playlists_by_mine.nextPageToken)
    result = {}
    result.update({x.snippet.title: x.id for x in playlists_by_mine.items})
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
    
def create_playlist(youtube, title):
    request = youtube.playlists().insert(
        part="snippet",
        body={
          "snippet": {
            "title": title
          }
        }
    )
    response = request.execute()

def search(track, artist):
    api = Api(access_token=config['YOUTUBE_OAUTH2_ACCESS_TOKEN'])
    r = api.search_by_keywords(q=f"{track} {artist}", search_type=["video"], count=1, limit=1)
    item = r.items[0]
    print(f"track: {track} artist: {artist}\n{item.snippet.title}: {item.id.videoId} \n https://www.youtube.com/watch?v={item.id.videoId} \n\n")

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

def top_tens_to_playlist(top_tens):
    current_playlists = get_playlist()
    for ten in top_tens:
        iso_date = parser.parse(ten)
        formatted_date = iso_date.strftime("%B %d, %Y")
        title = f'MYX Daily Top 10 - {formatted_date}'
        if title in current_playlists:
            # playlist_id = current_playlists[title]
            # get_playlist_items(playlist_id=playlist_id)
            continue
        else:
            continue
            # create_playlist(youtube,title)
        raise Exception(f"Sorry,")


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
# top_tens_to_playlist(tens)

#use pyyoutube to search
#use raw youtube python to create playlist and add tracks
#TODO: add track function