import time, os, string, json

from typing import Dict, List, Any
from collections import defaultdict
from math import log

import pandas as pd
import networkx as nx

from spotifynetwork import Track, Network, Artist
from nltk.stem import PorterStemmer 


def get_stopwords(file_path: str) -> Dict[str, bool]:
	stopwords = {}
	with open(file_path) as f:
		tmp = f.read().split("\n")
		for word in tmp:
			stopwords[word] = True
	return stopwords

def clean_tags(G: nx.Graph, stopwords: Dict[str, bool], ps: PorterStemmer) -> Dict[str, Any]:
	artists = {}
	for node in G.nodes():
		if 'artist' not in G.nodes[node]:
			continue

		artist_name = G.nodes[node]['artist'].name
		tags = G.nodes[node]['artist'].attr['tags']
		if not tags or type(tags) == float:
			continue

		cleaned_tags = {}
		for tag, popularity in json.loads(tags).items():
			cleaned_tag = []

			tag = tag.replace("-", " ")
			tokens = [tag.translate(str.maketrans('', '', string.punctuation)).lower()]
			if " " in tokens[0]:
				tokens = tokens[0].split(" ")

			for token in tokens:
				if token in stopwords or token in artist_name.lower():
					continue
				stemmed_token = ps.stem(token)
				if stemmed_token == "":
					continue
				cleaned_tag.append(stemmed_token)
			cleaned_tag = "|".join(cleaned_tag)

			if cleaned_tag == "" or cleaned_tag == "none":
				continue

			cleaned_tags[cleaned_tag] = popularity

		artists[artist_name] = cleaned_tags
	return artists

class Tag:
	def __init__(self, tag, df):
		self.tag = tag
		self.df = df

class Weight:
	def __init__(self, tf, df):
		self.tf = tf
		self.df = df
		self.tfidf = 1 + log((tf / log(1 + df)), 10)

def get_document_frequencies(artists: Dict[str, Any]) -> Dict[str, float]:
	dfs = defaultdict(lambda: 0)
	for artist_name, artist_tags in artists.items():
		for tag, tf in artist_tags.items():
			if "|" not in tag and tag not in artist_name:
				dfs[tag] += tf
				continue
			tokens = tag.split("|")
			for token in tokens:
				if token == "" and token not in artist_name:
					continue
				dfs[token] += tf / len(tokens)
	return dfs


def set_weights(artists: Dict[str, Any], dfs: Dict[str, float]) -> Dict[str, Weight]:
	for artist_name, tags in artists.items():
		weighted_tags = {}
		for tag, tf in tags.items():
			if "|" not in tag and tag not in artist_name:
				weighted_tags[tag] = Weight(tf, dfs[tag])
				continue
			tokens = tag.split("|")
			for token in tokens:
				if token == "" and token not in artist_name:
					continue
				weighted_tags[token] = Weight(tf, dfs[token])
		artists[artist_name] = weighted_tags
	return artists


def update_nodes(G: nx.Graph, artists: Dict[str, Any]):
	for artist in nx.get_node_attributes(G, 'artist').values():
		tags = artists.get(artist.name, {})
		if not tags:
			continue
		for tag, weight in tags.items():
			if tag not in G.nodes:
				G.add_node(tag, tag=Tag(tag, weight.df))
			G.add_edge(artist.id, tag, tfidf=weight.tfidf, tf=weight.tf, df=weight.df)


def main():
	# load stopwords
	stopwords_path = os.environ.get("BLOCKLIST_PATH")
	if not stopwords_path:
		raise ValueError("No blocklist path provided")
	stopwords = get_stopwords(stopwords_path)

	# load graph
	vertices_path = os.environ.get("VERTICES_PATH")
	edges_path = os.environ.get("EDGES_PATH")
	if not vertices_path or not edges_path:
		raise ValueError("No file paths provided")

	network = Network()
	V = pd.read_csv(vertices_path)
	E = pd.read_csv(edges_path)
	network.from_dataframe(V, E)

	print(f"Loaded {len(network.graph.nodes)} nodes and {len(network.graph.edges)}")

	# clean
	ps = PorterStemmer() 
	artists = clean_tags(network.graph, stopwords, ps)
	dfs = get_document_frequencies(artists)
	artists = set_weights(artists, dfs)

	# update graph
	update_nodes(network.graph, artists)

	V, E = network.to_dataframe()
	V.to_csv("vertices_cleantags.csv", index=False)
	E.to_csv("edges_cleantags.csv", index=False)

if __name__ == '__main__':
	main()


	# # display sample
	# for tag, weight in sorted(artists["Anderson .Paak"].items(), key=lambda x: x[1].tfidf):
	# 	print(tag + ": " + json.dumps(weight.__dict__, indent=3))
