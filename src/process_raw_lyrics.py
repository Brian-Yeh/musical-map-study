import pandas as pd
import langid
from textblob import TextBlob
import time
bad_string = '          \r\n            Lyrics for this song have yet to be released. Please check back once the song has been released.\r\n          \r\n        '
chunk_size = 200


def get_language(lyrics):
    # b = TextBlob(str(lyrics))
    # return b.detect_language()
    return langid.classify(lyrics)[0]


def stats():
    df = pd.read_csv('../data/lyrics_with_lang.txt')
    lang_grouped = df.groupby('lang').size().reset_index(name='count')
    lang_grouped = lang_grouped.sort_values(by='count', ascending=False)
    lang_grouped.to_csv('../data/language_stats.txt', index=False, header=True)


def main():
    lyrics_file = ''
    raw = pd.read_csv(lyrics_file)
    raw['lyrics'].astype(str)
    raw.dropna(subset=['lyrics'], inplace=True)

    cleaned = raw[~raw.lyrics.str.contains(bad_string)]
    cleaned = cleaned[(cleaned['lyrics'] != '')
              & (cleaned['lyrics'] != 'This music does not contain words')
              & (cleaned['lyrics'] != 'Instrumental')
              & (cleaned['lyrics'] != '[Instrumental]')
              & (cleaned['lyrics'] != '[Non-Lyrical Vocals]')]
    cleaned.to_csv(path_or_buf='../data/lyrics_cleaned.txt', index=False, encoding='utf-8')

    # get lyrics language
    cleaned = pd.read_csv('../data/lyrics_cleaned.txt', chunksize=chunk_size)
    count = 0
    write_header = True

    for chunk in cleaned:
        chunk['lang'] = chunk['lyrics'].apply(get_language)
        chunk.to_csv(path_or_buf='../data/lyrics_with_lang.txt', mode='a',
                     header=write_header, index=False, encoding='utf-8')
        write_header = False
        count += chunk_size
        print('==== %s songs processed ====' % str(count))


main()
# stats()