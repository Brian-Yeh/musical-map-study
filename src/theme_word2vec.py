import pandas as pd
import numpy as np
import sys
import spacy
import os.path
from tqdm import tqdm
tqdm.pandas()
sim_score_path = '../data/similarity_scores.txt'


def theme_similarity(theme, lyrics):
    theme_vec = nlp(theme)
    tokens = nlp(lyrics)
    max_cosine = -1.1

    for token in tokens:
        if token.vector_norm:
            max_cosine = max(theme_vec.similarity(token), max_cosine)

    if max_cosine == -1.1:  # no valid similarities found
        return np.nan
    return max_cosine


def get_similarity_scores(theme):
    # Retrieve lyrics and clean them
    song_info = pd.read_csv('../data/lyrics/song_info.txt')
    song_info = song_info[song_info['lang'] == 'en']
    reg = "[\(\[].*?[\)\]]"
    song_info['lyrics'] = song_info['lyrics'].replace(reg, '', regex=True)
    song_info['lyrics'] = song_info['lyrics'].str.replace('\r', ' ').str.replace('\n', ' ').str.replace('\t', ' ')
    song_info['lyrics'] = song_info['lyrics'].str.replace(r"\s\s+", ' ')

    cos_df = song_info[['song_id', 'lyrics']].drop_duplicates(subset='song_id')

    if os.path.exists(sim_score_path):
        print('Existing similarity_scores file found, will join new scores to existing file.')
        old_cos_df = pd.read_csv(sim_score_path)
        cos_df = cos_df.merge(right=old_cos_df, on='song_id', how='left')
    print('Retrieving cosine similarity scores for', len(cos_df), 'songs:')
    new_col_name = theme + '_cos'
    cos_df[new_col_name] = cos_df['lyrics'].progress_apply(lambda x: theme_similarity(theme, x))
    cos_df.drop(columns='lyrics', inplace=True)
    cos_df.to_csv(sim_score_path, index=False)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR: Need to provide theme as argument")
        exit(1)
    print("Loading en_core_web_lg model into spaCy...", end="")
    try:
        nlp = spacy.load('en_core_web_lg')
        print(' Done.')
    except OSError:
        print('Error: Need to download en_core_web_lg first!')
        exit(1)
    get_similarity_scores(sys.argv[1])
    exit(0)
