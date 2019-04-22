import os
import spotipy
import time
from spotipy.oauth2 import SpotifyClientCredentials
import datetime
import pandas as pd
import json
from tqdm import tqdm

key_file = '../keys.json'
with open(key_file) as f:
    keys = json.load(f)

client_credentials_manager = SpotifyClientCredentials(client_id=keys['spotify_client_id'],
                                                      client_secret=keys['spotify_client_secret'])
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
username = 'thesoundsofspotify'
now = datetime.datetime.now()
playlists = spotify.user_playlists(username, 50, 0)
script_dir = os.path.dirname(__file__)


def get_playlist_songs(playlists_df):
    filename = ("../data/songs/songs_%s-%s-%s.txt"
                % (now.year, now.month, now.day))
    abs_file_path = os.path.join(script_dir, filename)
    print("Writing songs to %s" % abs_file_path)

    with open(abs_file_path, "a", encoding='utf-8') as file:
        file.write('location,playlist_id,song_id,artist,title\n')

        pbar = tqdm(total=len(playlists_df))
        for index, playlist in playlists_df.iterrows():
            user_results = spotify.user_playlist(username, str(playlist['id']))
            # print(user_results)
            tracks = user_results['tracks']
            # print(user_results['tracks'])
            location = playlist['name']
            # if location.startswith("The Sound of "):
            #     location = location[13:]
            # print(location)
            # print(str(index) + " " + location + "... ", end="")
            write_tracks(file, location, playlist['id'], tracks)
            # print("done")
            pbar.update(1)
            time.sleep(.5)
        pbar.close()


def write_tracks(file, location, playlist_id, tracks):
    try:
        for i, item in enumerate(tracks['items']):
            track = item['track']
            if track is not None:
                file.write("%s,%s,%s,\"%s\",\"%s\"\n"
                           % (location, playlist_id, track['id'], track['artists'][0]['name'].replace('"', ''), track['name'].replace('"', '')))
    except (RuntimeError, TypeError, NameError):
        print('\n' + str(location) + ' ' + str(playlist_id))
        print(item)
        pass


def main():
    playlists_df = pd.read_csv("../data/playlists/playlists.csv", skipinitialspace=True)

    # offset if needed
    # playlists_df = playlists_df[1933:]
    # print(playlists_df.head())

    get_playlist_songs(playlists_df)


main()
# user_results = spotify.user_playlist(username, playlist['id'])
# # print(user_results)
# tracks = user_results['tracks']
# # print(user_results['tracks'])
# show_tracks(tracks)
# while tracks['next']:
#     tracks = sp.next(tracks)
#     show_tracks(tracks)

# with open(filename, "a") as file:
#     file.write('name, id\n')
#     while True:
#         print('offset = ' + str(offset))
#         playlists = spotify.user_playlists(username, 50, offset)
#         returned = len(playlists['items'])
#
#         for playlist in playlists['items']:
#             if playlist['owner']['id'] == username:
#                 if playlist['name'].startswith('The Sound of'):
#                     file.write(playlist['name'] + ", " + playlist['id'] + '\n')


        # if returned < 50:
        #     break
        # else:
        #     offset += 50
        #     time.sleep(4)
# results = spotify.search('Radiohead',10,0,'artist',None)
# print(results)