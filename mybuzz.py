# -*- coding: utf-8 -*-
import buzz
import itertools
import json
import pprint
import re
import yaml

# Load settings
f = open('mysettings.yaml')
settings = yaml.load(f)
f.close()

buzz_client = buzz.Client()
buzz_client.use_anonymous_oauth_consumer()
buzz_client.oauth_scopes=[buzz.FULL_ACCESS_SCOPE]
buzz_client.build_oauth_access_token(settings['oauth_token_key'],
                                     settings['oauth_token_secret'])

# Fetching Gowalla posts within 100m of Spotify HQ
results = buzz_client.search(query="gowal.la",
                             longitude="18.073711",
                             latitude="59.335313",
                             radius="100")

# Compiling a list of unique Buzz author names for the Gowalla posts
# API doesn't support searching for user IDs yet, otherwise we would
# be using IDs.
actor_names_with_dups = []
for res in itertools.islice(results, 20):
    actor_names_with_dups.append(res.actor.name.encode("utf-8"))

# Removing duplicates
actor_names = list(set(actor_names_with_dups))

# Fetching the latest Spotify links for the users we've compiled.
spotify_links = []
for name in actor_names:
    # API doesn't support searching for user IDs yet
    query = "\"%s\" open.spotify.com" % (name)
    spotify_links_search = buzz_client.search(query=query)

    for res in itertools.islice(spotify_links_search, 10):
        # res_json = json.loads(res.json)

        # Parse the contents since this might be syndicated from
        # Twitter, last.fm, etc.
        r = re.search('(http://open.spotify.com/track/[0-9A-Za-z]+)',
                      res.content)
        if r:
            spotify_links.append({'uri': r.group(1),
                                 'actor_name': name})
                                 #,'published': res_json.published})

# Present the Spotify links as rudimentary html
print "<ul>"
for link in spotify_links:
    print "<li><a href=\"%s\">%s</a></li>" % (link['uri'], link['actor_name'])
print "</ul>"
