import requests
import json
import os
import time
import vlc
import keyboard
import threading

# Optional: Add VLC to PATH
vlc_path = r"C:\Program Files\VideoLAN\VLC"
if vlc_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + vlc_path


class DeadShowFSM:
    def __init__(self):
        self.state = 'idle'
        self.identifier = None
        self.mp3_urls = {}
        self.player = None
        self.instance = vlc.Instance()
        self.instance = vlc.Instance('--quiet')

        self.transitions = {
            'idle': {
                'load': self.to_loaded
            },
            'loaded': {
                'select': self.to_selected
            },
            'playing': {
                'stop': self.to_idle
            }
        }


    def trigger(self, event, *args):
        state_events = self.transitions.get(self.state, {})
        if event in state_events:
            state_events[event](*args)
        else:
            print(f"No transition from {self.state} on '{event}'")

    def to_loaded(self, date_prefix):
        print(f"Searching for show: {date_prefix}")
        self.identifier = self.find_show(date_prefix)
        self.mp3_urls = self.get_mp3_urls(self.identifier)
        self.state = 'loaded'
        print(f"Loaded show with {len(self.mp3_urls)} tracks.")

    def to_selected(self, track_number):
        try:
            self.play_url(track_number - 1)
        except IndexError:
            print("Invalid track number.")

    def to_idle(self):
        if self.player:
            self.player.stop()
            print("Playback stopped.")
        self.state = 'idle'

    def menu(self):
        def input_loop():
            print("\nControls: [p]ause, [r]esume, [s]top, [q]uit menu")
            while self.state == 'playing':
                if keyboard.is_pressed('p'):
                    print("\nPaused")
                    self.player.pause()
                    time.sleep(0.3)
                elif keyboard.is_pressed('r'):
                    print("\nResumed")
                    self.player.play()
                    time.sleep(0.3)
                elif keyboard.is_pressed('s'):
                    print("\nStopped")
                    self.player.stop()
                    self.state = 'idle'
                    break
                elif keyboard.is_pressed('q'):
                    print("\nExited control menu (playback continues)")
                    break
                time.sleep(0.1)

        menu_thread = threading.Thread(target=input_loop)
        menu_thread.start()
        menu_thread.join()  # Block until user exits the menu


    def find_show(self, prefix):
        params = {
            'q': f'collection:GratefulDead AND identifier:{prefix}*',
            'fl[]': 'identifier,num_favorites',
            'sort[]': 'num_favorites desc',
            'rows': 1,
            'output': 'json'
        }
        response = requests.get('https://archive.org/advancedsearch.php', params=params)
        data = response.json()
        docs = data.get('response', {}).get('docs', [])
        if not docs:
            raise ValueError("No recordings found for that date.")
        return docs[0]['identifier']

    def get_mp3_urls(self, identifier):
        url = f"https://archive.org/metadata/{identifier}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch metadata for {identifier}")
        data = response.json()
        base_url = f"https://archive.org/download/{identifier}/"
        mp3_urls = {}
        for file in data.get("files", []):
            if file.get("format") in ["VBR MP3", "128Kbps MP3"] and file.get("name", "").endswith(".mp3"):
                title = file.get("title", file.get("name"))
                mp3_urls[title] = base_url + file["name"]
        return mp3_urls

    def play_url(self, index):
        titles = list(self.mp3_urls.keys())
        urls = list(self.mp3_urls.values())

        if index < 0 or index >= len(urls):
            print("Track index out of range.")
            return

        self.current_track_index = index

        while 0 <= self.current_track_index < len(urls):
            title = titles[self.current_track_index]
            url = urls[self.current_track_index]

            self.player = self.instance.media_player_new()
            media = self.instance.media_new(url)
            self.player.set_media(media)
            self.player.play()

            # Wait for playback to start
            for _ in range(50):
                if self.player.is_playing():
                    break
                time.sleep(0.1)

            self.state = 'playing'
            print(f"\nNow playing: {title}")
            print("Controls: [p]ause, [r]esume, [n]ext, [b]ack, [s]top")

            while self.state == 'playing':
                try:
                    if keyboard.is_pressed('p'):
                        self.player.pause()
                        print('Paused')
                        time.sleep(0.3)
                    elif keyboard.is_pressed('r'):
                        self.player.play()
                        print('Resumed')
                        time.sleep(0.3)
                    elif keyboard.is_pressed('n'):
                        self.player.stop()
                        print('Next Track')
                        self.current_track_index += 1
                        break  # move to next track
                    elif keyboard.is_pressed('b'):
                        self.player.stop()
                        print('Last Track')
                        self.current_track_index -= 1
                        break  # move to previous track
                    elif keyboard.is_pressed('s'):
                        self.player.stop()
                        print('Stopped Playback')
                        self.state = 'idle'
                        return  # return to menu
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    self.player.stop()
                    self.state = 'idle'
                    return
                
    
