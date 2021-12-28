import socket
import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
import time
import pickle

HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('LAPTOP-F2H66TI1', 1243))

username = 'Yatharth Bhargava'
scope = 'user-read-private user-read-playback-state user-modify-playback-state'

try:
    token = util.prompt_for_user_token(username, scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI)

spotifyObject = spotipy.Spotify(auth=token)

spotifyObjectMessage = pickle.dumps(spotifyObject)
spotifyObjectMessage = bytes(f"{len(spotifyObjectMessage):<{10}}", 'utf-8') + spotifyObjectMessage

s.send(spotifyObjectMessage)

while True:
    full_msg = b''
    new_msg = True
    while True:
        msg = s.recv(16)
        if new_msg:
            msglen = int(msg[:HEADERSIZE])
            new_msg = False

        full_msg += msg

        if len(full_msg)-HEADERSIZE == msglen:
            print(full_msg[HEADERSIZE:])
            new_msg = True
            full_msg = b""