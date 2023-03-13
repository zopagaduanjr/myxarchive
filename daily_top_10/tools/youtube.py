import pprint
import csv
from pyyoutube import Api
from dotenv import dotenv_values

def pretty_print(val):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(val)

def search(track, artist):
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

def create_playlist(top_tens):
    for ten in top_tens:
        for item in top_tens[ten]:
            search(item[2],item[3])
        raise Exception("Sorry")


config = dotenv_values(".env")
# api = Api(api_key=config["YOUTUBE_API_KEY"])
api = Api(client_id=config["YOUTUBE_CLIENT_ID"],
                client_secret=config["YOUTUBE_CLIENT_SECRET"])
# response_url = api.get_authorization_url()
# api.generate_access_token(authorization_response=response_url)
print("AMDG")
# tens = group_spotified_input()
# create_playlist(tens)

#use pyyoutube to search and generate access token
#use raw youtube python to create playlist and add tracks