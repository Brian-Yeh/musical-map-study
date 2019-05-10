import pandas as pd
import langid
import json
import sys
from tqdm import tqdm
tqdm.pandas()
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

key_file = '../keys.json'
with open(key_file) as f:
    keys = json.load(f)

client_credentials_manager = SpotifyClientCredentials(client_id=keys['spotify_client_id'],
                                                      client_secret=keys['spotify_client_secret'])
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

bad_string = '          \r\n            Lyrics for this song have yet to be released. Please check back once the song has been released.\r\n          \r\n        '
bad_string_1 = '"Unfortunately, we are not licensed to display the full lyrics for this song at the moment. Hopefully we will be able to in the future. Until then... how about a random page?"'
chunk_size = 200


def get_language(lyrics):
    return langid.classify(lyrics)[0]


def stats():
    df = pd.read_csv('../data/lyrics_with_lang.txt')
    lang_grouped = df.groupby('lang').size().reset_index(name='count')
    lang_grouped = lang_grouped.sort_values(by='count', ascending=False)
    lang_grouped.to_csv('../data/language_stats.txt', index=False, header=True)


def process_lyrics(lyrics_file):
    raw = pd.read_csv('../data/lyrics/raw/' + lyrics_file)
    raw['lyrics'].astype(str)

    raw.dropna(subset=['lyrics'], inplace=True)
    cleaned = raw[~raw.lyrics.str.contains(bad_string)]
    cleaned = cleaned[(cleaned['lyrics'] != '')
                      & (cleaned['lyrics'] != 'This music does not contain words')
                      & (cleaned['lyrics'] != 'Instrumental')
                      & (cleaned['lyrics'] != '[Instrumental]')
                      & (cleaned['lyrics'] != '\"Instrumental\"')
                      & (cleaned['lyrics'] != '[Non-Lyrical Vocals]')]
    cleaned.reset_index(drop=True, inplace=True)

    # Get language of lyrics and output resulting dataframe to CSV
    cleaned['lang'] = cleaned['lyrics'].progress_apply(get_language)
    cleaned.to_csv(path_or_buf='../data/lyrics/processed/' + lyrics_file, header=True, index=False, encoding='utf-8')

    # Get Audio features by chunks of 50
    print("\n=== Getting Audio Features ===")
    i = 0
    chunk = 50
    pbar = tqdm(total=len(cleaned))

    while i < len(cleaned):
        if (len(cleaned) - i) < 50:
            chunk = len(cleaned) - i + 1
        cleaned.loc[i:i + chunk, 'audio_features'] = spotify.audio_features(cleaned.loc[i:i + chunk, 'song_id'])
        i += 50
        pbar.update(chunk)
    pbar.close()

    # Add lyrics to song_info.txt
    song_info = pd.read_csv('../data/lyrics/song_info.txt')
    song_info = pd.concat([song_info, cleaned], axis=0, sort=False, ignore_index=True)
    song_info.drop_duplicates(subset='song_id', inplace=True)
    song_info.dropna(subset=['lyrics'], inplace=True)
    song_info.to_csv(path_or_buf='../data/lyrics/song_info.txt', index=False, encoding='utf-8')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: Need to provide lyrics file name as argument")
        exit(1)
    process_lyrics(sys.argv[1])
