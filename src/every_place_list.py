from bs4 import BeautifulSoup
import requests
import pandas as pd


def get_everyplace_list():
    page = requests.get("http://everynoise.com/everyplace.cgi")
    soup = BeautifulSoup(page.content, 'html.parser')

    tables = list(soup.find_all('table'))
    cities = tables[1].find_all('tr', {'class': 'datarow'})

    with open("../data/playlists/everyplace_list.txt", "a") as file:
        file.write('name\n')
        for row in cities:
            row_info = row.find_all('a')
            file.write("%s %s\n" % (row_info[1].string, row_info[2].string))


def join_ids():
    print("Joining ids with Every Place list")
    ep_csv = pd.read_csv("../data/playlists/everyplace_list.txt")
    assert(len(ep_csv) > 0)
    print(len(ep_csv))

    ids_csv = pd.read_csv("../data/playlists/raw_playlists.txt")
    assert (len(ids_csv) > 0)
    ids_csv['id'] = ids_csv['id'].astype(str)

    final_list = pd.merge(ep_csv, ids_csv.drop_duplicates('name'), how='left', on='name')
    final_list.dropna(inplace=True)
    print(len(final_list))
    print(final_list.head())
    final_list.to_csv("../data/playlists/playlists.csv", index=False, encoding='utf-8')
