import os
import lyricwikia
import lyricsgenius
import requests
import pandas as pd
from tqdm import tqdm
import datetime
from bs4 import BeautifulSoup
from kkbox_developer_sdk.auth_flow import KKBOXOAuth

# KKBOX API setup
auth = KKBOXOAuth('70c7e34eb87791c22919e8022ff8ef2a', '874a427a0829434c423f69e9f364e644')
token = auth.fetch_access_token_by_client_credentials()

from kkbox_developer_sdk.api import KKBOXAPI
kkboxapi = KKBOXAPI(token)

# Genius API setup
genius = lyricsgenius.Genius("s1t9yyg-jOQWjkHZ7nNEEp4iHYlyMMWw7GNtV3xk3t2m8CAC-lDQoZEl4jHCvL-M")
genius.verbose = False
genius.skip_non_songs = True

script_dir = os.path.dirname(__file__)
chunk_size = 50
pbar = 0

def lyric_wikia(artist, song):
    try:
        return "\""+lyricwikia.get_lyrics(artist, song)+"\""
    except Exception as e:
        return ''


def genius_lyrics(artist, song):
    song = genius.search_song(song, artist, get_full_info=False)
    if song is None:
        return ''

    if song.artist == artist:
        return "\""+song.lyrics+"\""

    return ''


def kkbox_lyrics(artist, song, territory):
    search_results = kkboxapi.search_fetcher.search(artist + ' ' + song, types=['track'], terr=territory)
    if search_results is None or len(search_results['tracks']['data']) == 0:
        return ''

    url = search_results['tracks']['data'][0]['url']
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    lyrics = soup.find_all('p', {'class': 'lyrics'})

    if lyrics is None or len(lyrics) == 0:
        return ''

    return "\""+str(lyrics[0])+"\""


def get_lyrics(row):
    # print(row['artist'] + ', ' + row['title'] + ' ... ', end="")
    global pbar
    pbar.update(1)

    lyrics = lyric_wikia(row['artist'], row['title'])
    if lyrics != '':
        # print('Found - lyric wikia')
        return lyrics

    lyrics = genius_lyrics(row['artist'], row['title'])

    if lyrics != '':
        # print('Found - Genius')
        return lyrics

    if row['country'] in ['TW', 'HK', 'SG', 'MY', 'JP']:
        lyrics = kkbox_lyrics(row['artist'], row['title'], row['country'])
        if lyrics != '':
            # print('Found - KKBOX')
            return lyrics

    # print('Not Found.')
    return lyrics


def main():
    now = datetime.datetime.now()

    song_file = 'songs_2019-4-21.txt'
    all_songs = pd.read_csv('../data/songs/'+song_file)
    all_songs.drop_duplicates(subset=['song_id'], inplace=True)
    all_songs['country'] = all_songs['location'].str[-2:]
    all_songs.drop(columns=['location', 'playlist_id'], inplace=True)

    song_info = pd.read_csv('../data/song_info.txt')

    attempt_all_lyrics = False

    if attempt_all_lyrics:
        # Get lyrics for entire song_info database
        all_songs = all_songs.merge(right=song_info[['song_id', 'lyrics']], on='song_id', how='left')
        lyrics_needed = all_songs[all_songs['lyrics'].isnull()]
    else:
        # Get lyrics for just the songs file
        song_info = song_info.merge(right=all_songs[['song_id', 'lyrics']], on='song_id', how='left')
        lyrics_needed = song_info[song_info['lyrics'].isnull()]

    num_needed = len(lyrics_needed)
    lyrics_needed.to_csv(path_or_buf='../data/songs/lyrics_needed_temp.txt', index=False, encoding='utf-8')
    lyrics_needed = pd.read_csv('../data/songs/lyrics_needed_temp.txt', chunksize=chunk_size)

    #################################################
    # lyrics_needed = lyrics_needed.iloc[31100:31200] # Used in case script is interrupted
    write_header = True    # Set False if running partial songs file (i.e. script was interrupted)
    #################################################

    count = 0
    print("Getting lyrics for " + str(num_needed) + " songs")

    global pbar
    pbar = tqdm(total=num_needed)
    lyrics_filename = "../data/lyrics/raw/lyrics_for_"+song_file[6:]
    tqdm.pandas()

    for chunk in lyrics_needed:
        chunk['lyrics'] = chunk.apply(lambda row: get_lyrics(row), axis=1)
        chunk.drop(columns=['country'], inplace=True)
        chunk.to_csv(path_or_buf=lyrics_filename, mode='a',
                     header=write_header, index=False, encoding='utf-8')
        write_header = False
        count += chunk_size
    pbar.close()


main()
