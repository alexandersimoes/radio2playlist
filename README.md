# radio2playlist

Paste in a WFMU radio station URL and this will transform it into a spotify playlist

## Init

You'll need to create your own Spotify App on the Spotify for Developers webpage. This will then give you a client id and secret (which you'll need to set as ENV vars). You'll also need to make sure whatever you set as your redirect URL matches exactly what you set as your ENV var.

Install all dependencies:

```
pip install -r requirements.txt
```

## Run

```
python run.py
```

First you'll need to authorize in a web browser so copy/paste the URL the script outputs in a new window. Next, paste the redirected URL back in the terminal.

Paste in a WFMU URL like: https://www.wfmu.org/playlists/shows/129175

You'll see an output of which track it was able to find and which it couldn't... in case you want to do some manual digging 😉.

Enjoy!
