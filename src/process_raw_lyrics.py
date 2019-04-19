import pandas as pd
import langid
import json
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
chunk_size = 200


def get_language(lyrics):
    return langid.classify(lyrics)[0]


def stats():
    df = pd.read_csv('../data/lyrics_with_lang.txt')
    lang_grouped = df.groupby('lang').size().reset_index(name='count')
    lang_grouped = lang_grouped.sort_values(by='count', ascending=False)
    lang_grouped.to_csv('../data/language_stats.txt', index=False, header=True)


def main():
    lyrics_file = 'lyrics_for_2019-4-5_14-17-22.txt'
    raw = pd.read_csv('../data/lyrics/raw/'+lyrics_file)
    raw['lyrics'].astype(str)

    raw.dropna(subset=['lyrics'], inplace=True)
    cleaned = raw[~raw.lyrics.str.contains(bad_string)]
    cleaned = cleaned[(cleaned['lyrics'] != '')
              & (cleaned['lyrics'] != 'This music does not contain words')
              & (cleaned['lyrics'] != 'Instrumental')
              & (cleaned['lyrics'] != '[Instrumental]')
              & (cleaned['lyrics'] != '[Non-Lyrical Vocals]')]
    cleaned.reset_index(drop=True, inplace=True)


    cleaned['lang'] = cleaned['lyrics'].progress_apply(get_language)
    cleaned.to_csv(path_or_buf='../data/lyrics/processed/1'+lyrics_file, header=True, index=False, encoding='utf-8')
    # print(spotify.audio_features(cleaned.loc[0:50, 'song_id']))
    # pbar.close()

    # Get Audio features by chunks of 50
    i = 0
    chunk = 50
    pbar = tqdm(total=len(cleaned))

    while i < len(cleaned):
        if (len(cleaned) - i) < 50:
            chunk = len(cleaned) - i + 1
        cleaned.loc[i:i + chunk, 'audio_features'] = spotify.audio_features(cleaned.loc[i:i + chunk, 'song_id'])
        i += 50
        pbar.update(50)
    pbar.close()

    # Add lyrics to song_info.txt
    song_info = pd.read_csv('../data/song_info.txt')
    song_info = pd.concat([song_info, cleaned], axis=0, sort=False, ignore_index=True)
    song_info.drop_duplicates(subset='song_id', inplace=True)
    song_info.to_csv(path_or_buf='../data/lyrics/song_info.txt', index=False, encoding='utf-8')



main()
# stats()