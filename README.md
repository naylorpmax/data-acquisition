# data-acquisition 

Python application to collect artist and track data by leveraging networkx, spotipy, and the LastFM API.

## Prerequisites

- [x] Docker v20.10.2
- [x] docker-compose v1.29.1
- [x] GNU Make v4.2.1
- [x] Spotify API client ID and secret
- [x] Last.FM API client ID and secret

## Setup

To pull artist and track data from Spotify, add your client ID and secret to your environment:

```
export SPOTIPY_CLIENT_ID=<spotify-client-id>
export SPOTIPY_CLIENT_SECRET=<spotify-client-secret>
```

Then, run the application by calling the Make target:

```
make pull-spotify
```

To pull artist tag data from Last.FM, add your client ID and secret to your environment:

```
export LASTFM_CLIENT_ID=<lastfm-client-id>
export LASTFM_CLIENT_SECRET=<lastfm-client-secret>
```

Then, run the application by calling the Make target:

```
make pull-lastfm
```
