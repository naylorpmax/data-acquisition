# data-acquisition 

Python library to collect artist and track data by leveraging networkx, spotipy, and the LastFM API.

```
# install dependencies
pip3 install -r requirements.txt

# configure
export PLAYLISTS_PATH=acquisitions/playlists.txt
export SPOTIPY_CLIENT_ID=<spotify-client-id>
export SPOTIPY_CLIENT_SECRET=<spotify-client-secret>
export LASTFM_CLIENT_ID=<lastfm-client-id>
export LASTFM_CLIENT_SECRET=<lastfm-client-secret>

# run library
python3 -m acquisition

# tag artists
python3 acquisition/tag.py
```
