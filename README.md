# data-acquisition 

Python library to collect artist and track data by leveraging networkx and spotipy.

```
# install dependencies
pip3 install -r requirements.txt

# configure
export PLAYLISTS_PATH=acquisitions/playlists.txt
export SPOTIPY_CLIENT_ID=<spotify-client-id>
export SPOTIPY_CLIENT_SECRET=<spotify-client-secret>

# run library
python3 -m acquisition
```
