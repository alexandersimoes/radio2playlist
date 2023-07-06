import spotipy
import requests
import os
from spotipy import oauth2
from spotipy.exceptions import SpotifyException
from bs4 import BeautifulSoup

# Define the required environment variables
required_vars = ['SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET']

# Check if all required variables are present
for var in required_vars:
  if var not in os.environ:
    print(f"Required environment variable '{var}' is not found.")
    exit(1)

SPOTIPY_CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET']
SPOTIPY_REDIRECT_URI = os.environ['SPOTIPY_REDIRECT_URI']
SCOPE = 'playlist-modify-private'
CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth(
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SCOPE, cache_path=CACHE)

# Try using cached token... if not request a new one
token_info = sp_oauth.get_cached_token()
if not token_info:
  auth_url = sp_oauth.get_authorize_url()
  print(f'Please visit this URL to authorize the application: {auth_url}')
  url = input("Paste the redirected URL here: ")
  code = sp_oauth.parse_response_code(url)
  try:
    token_info = sp_oauth.get_access_token(code)
  except Exception as e:
    if 'Invalid authorization code' in str(e):
      print(
          f"Invalid authorization code. Unable to parse auth token in url provided '{url}'.")
    else:
      print("An error occurred during Spotify authorization:", e)
    exit(1)

access_token = token_info['access_token']
sp = spotipy.Spotify(auth=access_token)

songs = []
track_ids = []
found = []
missing = []

# Define the URL you want to scrape
playlist_url = input("Enter a Playlist URL: ")

# Send a GET request to the URL
response = requests.get(playlist_url)

# Create a BeautifulSoup object from the response content
soup = BeautifulSoup(response.content, 'html.parser')

# Find the <span> element with the ID 'playlist_show_drops_section'
page_title_span_element = soup.find('h2').get_text().strip().replace('\n', ' ')
playlist_description = page_title_span_element
show_title = page_title_span_element.split(":")[0]

# Find description
description_element = soup.find(
    'p', id='date_desc_archive_section').get_text().strip().split('\n')[0]
date, *show_title_pt2 = description_element.split(":")
playlist_title = f"{show_title}:{' '.join(show_title_pt2)} ({date})"
print(playlist_title)

# Find the <span> element with the ID 'playlist_show_drops_section'
playlist_span_element = soup.find('span', id='playlist_show_drops_section')

# Find the <table> element within the <span> element
table_element = playlist_span_element.find('table')

# Find all the rows (<tr>) within the table
rows = table_element.find_all('tr')

# Iterate over each row and print the contents of elements with class 'col_artist'
for row in rows[1:]:
  artist_cell = row.find(class_='col_artist')

  if artist_cell:
    artist = artist_cell.get_text().strip()
    try:
      track = row.find(class_='col_song_title').find(
          'font').get_text().strip()
    except:
      print("Can't find song title...")
      continue
    album = row.find(class_='col_album_title').get_text().strip()
    label = row.find(class_='col_record_label').get_text().strip()
    if album:
      songs.append({"artist": artist, "track": track})

for song in songs:
  artist = song["artist"]
  track = song["track"]
  if artist != "Kit Sebastian":
    continue

  # Sanitize artist name by getting first result via spotify search
  artist_results = sp.search(q=artist, type='artist')
  try:
    artist_name = artist_results["artists"]["items"][0]['name']
  except IndexError:
    print(
        f"Unable to find artist: {artist}, trying to split artist name...")
    if "&" in artist:
      split_artist = artist.split("&")[0]
      artist_results = sp.search(q=split_artist, type='artist')
      try:
        artist_name = artist_results["artists"]["items"][0]['name']
      except IndexError:
        continue
    continue

  track_results = sp.search(
      q='artist:' + artist_name + ' track:' + track, type='track')
  print("track_results:", track_results)
  try:
    track_id = track_results['tracks']['items'][0]['id']
    track_info = sp.track(track_id)
    found.append(song)
  except IndexError:
    print(
        f"Unable to find: {track} by {artist_name}, trying from raw artist name string...")
    track_results = sp.search(q='artist:' + artist + ' track:' + track, type='track')
    try:
      track_id = track_results['tracks']['items'][0]['id']
      track_info = sp.track(track_id)
    except IndexError:
      missing.append(song)
      continue
  song_name = track_info['name']
  artist_name = track_info['artists'][0]['name']
  album_name = track_info['album']['name']
  release_date = track_info['album']['release_date']

  track_ids.append(track_id)

exit(1)
# Get the current user's username
user_info = sp.current_user()
username = user_info['id']

# Create the playlist
playlist = sp.user_playlist_create(
    username, playlist_title, public=False, description=playlist_description)

# Retrieve the playlist ID
playlist_id = playlist['id']

# Add the tracks to the playlist
sp.user_playlist_add_tracks(username, playlist_id, track_ids)

print("Playlist created successfully:")
print("")
for i, song in enumerate(found):
  print(f"{i+1}. {song['artist']} - {song['track']}")
print("")
if len(missing):
  print("-------------")
  print("The following songs could not be found on Spotify:")
  for i, song in enumerate(missing):
    print(f"{i+1}. {song['artist']} - {song['track']}")
