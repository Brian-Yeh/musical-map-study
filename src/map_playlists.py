import spotipy
import time
import json
from spotipy.oauth2 import SpotifyClientCredentials

key_file = '../keys.json'
with open(key_file) as f:
    keys = json.load(f)

client_credentials_manager = SpotifyClientCredentials(client_id=keys['spotify_client_id'],
                                                      client_secret=keys['spotify_client_secret'])
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

username = 'thesoundsofspotify'
offset = 200

# playlists = spotify.user_playlists(username, 50, 0)

with open("../data/playlists/raw_playlists.txt", "w+") as file:
    file.write('name,id\n')
    while True:
        print('offset = ' + str(offset))
        playlists = spotify.user_playlists(username, 50, offset)
        returned = len(playlists['items'])

        for playlist in playlists['items']:
            if playlist['owner']['id'] == username:
                if playlist['name'].startswith('The Sound of'):
                    # print(playlist['name'][13:] + ", " + playlist['id'])
                    file.write(playlist['name'][13:] + ", " + playlist['id'] + '\n')

        if returned < 50:
            break
        else:
            offset += 50
            time.sleep(2)
# results = spotify.search('Radiohead',10,0,'artist',None)
# print(results)
