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
            tracks = user_results['tracks']
            location = playlist['name']
            write_tracks(file, location, playlist['id'], tracks)

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
    get_playlist_songs(playlists_df)


main()
