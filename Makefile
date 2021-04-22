IMAGE_NAME?=banzo-acquisition
IMAGE_VERSION?=0.0.1

.PHONY: build-image
build-image:	## build docker image
	docker build -t ${IMAGE_NAME}:${IMAGE_VERSION} .

.PHONY: interactive
interactive:	## run container interactively
	docker run -it ${IMAGE_NAME}:${IMAGE_VERSION} /bin/bash

.PHONY: pull-spotify
pull-spotify:	## recursively pull spotify data via seed playlists
	docker-compose run \
		-e SPOTIPY_CLIENT_ID=${SPOTIPY_CLIENT_ID} \
		-e SPOTIPY_CLIENT_SECRET=${SPOTIPY_CLIENT_SECRET} \
		pull-spotify 
# 		-e IMAGE_VERSION=0.0.1 \
