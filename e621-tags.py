#!/usr/bin/env python3

import json
import urllib
import re
import requests
import argparse
import unidecode

parens=re.compile(r"\(.*\)")

base = 'https://e621.net'
headers = {"User-Agent": "Sneed's Feed and Seed (Formerly Chuck's)"}

def get_tags(limit, page, order):
	url="%s/tag/index.json?order=%s&limit=%d&page=%d" % (base, order, limit, page)
	return json.loads(requests.get(url, headers=headers).content)

def filter_tag(tag):
	tag=unidecode.unidecode(tag) 
	return parens.sub("", tag) \
		.replace('_',' ') \
		.strip()

current_page=1
page_size=500

parser = argparse.ArgumentParser(description="Make e621 tags into a normalised, delimited list")
parser.add_argument('count', metavar='N', type=int, help="# of tags")

args = parser.parse_args()
desired_tags = args.count

def process_results(results):
        # filter out artist tags
	results=filter(lambda tag: tag["type"] != 1, results)
	# filter out characters nobody has heard of
	results=filter(lambda tag: not (tag["type"] == 4 and tag["count"] < 500), results)
        # filter tag longer than 30 chars
	results=filter(lambda tag: len(tag["name"])<=30,results)
	
        # map to just the name
	return list(map(lambda tag: filter_tag(tag["name"]), results))

tags=[]

while desired_tags > 0:
	slice=min(page_size,desired_tags)
	print("Fetching %d tags from page %d" % (slice, current_page))

	results=get_tags(page_size,current_page,"count")
	results=process_results(results)[:slice]

	tags.extend(results)
	desired_tags -= len(results)
	current_page += 1

with open("e621-tags.txt", 'w') as f:
	f.write(",".join(tags))
	
print("Written to e621-tags.txt")
