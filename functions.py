"""
File:        functions.py
Author:      Tanner Casto
Date:        2025-06-03
Description: Contains all external functions for the GDTM script

Change Log:
    6/3/25: Initial creation
"""

import internetarchive as ia
import requests
import json
import time
import os
import sys

# Replace this with the actual path where VLC is installed
vlc_path = r"C:\Program Files\VideoLAN\VLC"

if vlc_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + vlc_path

import vlc
import time


"""
Function:       findShow()
Arguments:      desired_show_prefix -- show date of form 'gdyy-mm-dd'
                search -- class of the full grateful dead IA collection
Description:    based on the shows date (desired_show_prefix), this function will 
                find the shows on that date and find the show with the highest number 
                of favorites indicating, likely, the highest quality recording.
                
Return:         Returns the show identifier of type string

Change Log:
    6/3/25:     Initial creation
"""
def findShow(desired_show_prefix, search):
    filtered_search = [entry for entry in search if entry['identifier'].startswith(desired_show_prefix)]
    selected_show_identifier = ''
    for result in filtered_search:
        max_num_favorites = 0
        # IF ONLY ONE RECORDING, 
        if (len(filtered_search) == 1):        
            selected_show_identifier = result['identifier']
            break

        ## IF THERE ARE MULTIPLE RECORDINGS, FIND THE RECORDING WITH THE HIGHEST NUMBER OF FAVORITES 
        params = {
            'q': result['identifier'],                      # Query
            'fl[]': 'identifier,num_favorites',             # What to search for 
            'output': 'json'                                # Output type
        }
        response = requests.get('https://archive.org/advancedsearch.php', params=params)
        response_dict = response.json() # weird, yes but it returns a dictionary

        ## **UNCOMMENT IF WANTING TO SEE THE .JSON DATA
        # print(json.dumps(response_dict, indent=2))
    
        
        # pull the number of favorites
        # num_favorites = response_dict['response']['docs'][0]['num_favorites']
        docs = response_dict.get('response', {}).get('docs', [])
        num_favorites = None
        for doc in docs:
            if 'num_favorites' in doc:
                num_favorites = doc['num_favorites']
                break  # stop after finding the first one

        if num_favorites is not None:
            if num_favorites > max_num_favorites:
                max_num_favorites = num_favorites
                selected_show_identifier = result['identifier']
            

    print(f'Selected show: {selected_show_identifier}')
    return selected_show_identifier

"""
Function:       retrieveMetadata()
Arguments:      selected_show_identifier -- selected show based on number of favorites (quality)
Description:    returns the metadata for the selected show 
Return:         <class 'internetarchive.item.Item'>

Change Log:
    6/3/25:     Initial creation
"""
## DISPLAY METADATA FOR SELECTED SHOW
def get_mp3_urls(identifier):

    url = f"https://archive.org/metadata/{identifier}"
    response = requests.get(url)

    # Check for a successful response
    if response.status_code != 200:
        raise Exception(f"Failed to fetch metadata for {identifier} (status code {response.status_code})")

    data = response.json()
    # to print the json:
    # print(json.dumps(data, indent=4))

    mp3_urls = {}
    base_url = f"https://archive.org/download/{identifier}/"

    for file in data.get("files", []):
        if file.get("format") in ["VBR MP3", "128Kbps MP3"] and file.get("name", "").endswith(".mp3"):
            title = file.get("title", file.get("name"))
            mp3_urls[title] = base_url + file["name"]
        
    return mp3_urls


def play_url_with_loop(url):
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new(url)
    player.set_media(media)
    player.play()

    # Wait for VLC to actually start playing
    for _ in range(50):
        if player.is_playing():
            break
        time.sleep(0.1)
    else:
        print("Failed to start playback.")
        return

    print("Playing... Press Ctrl+C to stop manually.")
    try:
        while player.is_playing():
            current_time = player.get_time() / 1000  # seconds
            print(f"Playing at {current_time:.1f}s", end="\r")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        player.stop()