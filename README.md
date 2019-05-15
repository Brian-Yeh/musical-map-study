# Musical Map Study

An independent study project involving textual analysis of lyrics from songs in [Spotify's Musical Map](https://insights.spotify.com/us/2016/12/07/musical-map-of-the-world-2-0/). 

├── data                # Not included in repo, can be downloaded from [Google Drive](https://drive.google.com/open?id=1vUhsu3XWXJSoJHwA1KU2bOt9kw6LXPe0)
│   ├── lyrics          # Stores raw and processed lyrics, the main dataset of lyrics (song_info.txt) is also located here
│   ├── playlists       # Data containing info for Musical Map playlists
│   ├── songs           # CSV files that represent all the songs in the Musical Map and their corresponding playlist for a certain week
├── notebooks           # IPython notebook files (alternatively `doc`)
│   ├── misc_files      # Not included in repo, files for testing or outdated experiments
│   ├── html_versions   # HTML versions of the IPython notebooks
├── src                 # Source files for more intensive scripts such as pulling data
├── report              # Contains the final report and any graphical analyses generated
│   ├── benchmarks      # Graphics that were used in the final report
│   ├── analyses        # Some analyses for certain weekly datasets
├── keys-sample.json    # Spotify client id and secret keys go here, must be renamed to keys.json
└── README.md