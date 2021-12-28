import multiprocessing
import socket
import os
import sys
import json
from typing import Collection
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
import time
import pickle
from _thread import *
from threading import Thread
from multiprocessing import Process


is_playing = True
threads_list = []


def sync_skip(objectList):
    print(objectList)
    # current_track_seek = False
    while True:
        host_dict = objectList[0].current_playback()
        for i in objectList[1:]:
            if host_dict['item']['uri'] != i.current_playback()['item']['uri']:
                for i in objectList:
                    i.pause_playback()
                start_playback(start_playback_helper, objectList, [objectList[0].current_playback()['item']['uri']])
                # current_track_seek = False
                i.seek_track(host_dict['progress_ms'] + 10)
                # current_track_seek = False
                break
            
            # time.sleep(1)

            # if not current_track_seek:
            #     progress_list = multiprocessing.Array('i', 2)

            #     progress_p1 = Process(target = get_progress, args = (objectList[0].current_playback(), progress_list, 0))
            #     progress_p2 = Process(target = get_progress, args= (i.current_playback(), progress_list, 1))
                
            #     progress_p1.start()
            #     progress_p2.start()

            #     progress_p1.join()
            #     progress_p2.join()
            #     progress_p1.terminate()
            #     progress_p2.terminate()


            #     if progress_list[0] != progress_list[1]:
            #         i.seek_track(host_dict['progress_ms'] - 1)
            #         current_track_seek = True
            #     else:
            #         current_track_seek = True

            #     progress_list = []

def get_progress(client_dict, progress_list, index):
    #print('getProgress ran')
    progress_list[index] = int(client_dict['progress_ms'])

def clientThread(conn, addr):
    welcome_msg = bytes("welcome", 'utf-8')
    welcome_msg = bytes(f"{len(welcome_msg):<{10}}", 'utf-8') + welcome_msg
    conn.send(welcome_msg)

    spotifyObjectClient = b''
    firstmsg = True
    while True:
        # try:
            message = conn.recv(2048)
            if message:
                if firstmsg:
                    msglen = int(message[:10])
                    firstmsg = False
                
                spotifyObjectClient+=message    
                if len(spotifyObjectClient) - 10 == msglen:
                    print("full object received")
                    spotifyObjectClient = pickle.loads(spotifyObjectClient[10:])
                    spotifyObjectList.append(spotifyObjectClient)
                    length = len(spotifyObjectList)
                    if length > 1:                            
                        start_thread(start_playback_helper, spotifyObjectList, songs)

                        main_process1 = Process(target = sync_skip, args = (spotifyObjectList,))
                        main_process2 = Process(target = sync_pause, args = (spotifyObjectList,))
                        main_process3 = Process(target = sync_play, args = (spotifyObjectList,))

                        main_process1.start()
                        main_process2.start()
                        main_process3.start()
                        
                        #sync_skip(spotifyObjectList)
                        #pause_playback()
                        #start_playback(sync, spotifyObjectList)
                        
        # except Exception as error:
        #     print("Main", error)

def pause_playback_helper(spotifyObject):
    try:
        spotifyObject.pause_playback()
    except:
        pass

def pause_playback(spotifyObjectList):
    start_thread(pause_playback_helper, spotifyObjectList)

def sync_pause(objectList):
    while True:
        if not objectList[0].current_playback()['is_playing']:
            pause_playback(objectList)

def start_playback_helper(spotifyObject, songs = None):
    #print('yes')
    try:
        if songs:
            spotifyObject.start_playback(uris=songs)
        else:
            spotifyObject.start_playback()

    except:
        pass

def sync_play(objectList, songList = None):
    while True:
        if objectList[0].current_playback()['is_playing']:
            start_thread(start_playback_helper, spotifyObjectList, songList)
    

def start_thread(func, spotifyObjectList, songList = None):
    length = len(spotifyObjectList)
    for i in range(length):
        exec(f"thread{i} = Process(target = func, args = (spotifyObjectList[{i}], {songList if songList else ''}))")
        exec(f"threads_list.append(thread{i})")

    command = ""
    for i in range(length):
        command += f'thread{i}.start(); '
    exec(command)

    time.sleep(1)

    for i in range(length):
        exec(f"thread{i}.terminate()")
    
    if func == pause_playback_helper:
        for i in range(length):
            spotifyObjectList[i].seek_track(host_dict['progress_ms'])

if __name__ == "__main__":
    thread_running_list = []

    songfile = open('songs.pickle', 'rb')
    songs = pickle.load(songfile)
    songfile.close()


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), 1243))
    s.listen(5)

    client_list = []
    spotifyObjectList = []

    

    while True:
        clientsocket, address = s.accept()
        print(f"Connection from {address} has been established.")
        client_list.append(clientsocket)
        start_new_thread(clientThread, (clientsocket, address))
        

        # d = {1:"hi", 2: "there"}
        # msg = pickle.dumps(d)
        # msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8')+msg
        # print(msg)
        # clientsocket.send(msg)

