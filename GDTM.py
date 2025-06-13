from classes import *

class DeadShowPlayer:
    def __init__(self, date_prefix):
        self.fsm = DeadShowFSM()
        self.date_prefix = date_prefix

    def run(self):
        # Load the show and build the MP3 list
        self.fsm.trigger('load', self.date_prefix)

        print("\nTrack list:")
        for i, title in enumerate(self.fsm.mp3_urls, start=1):
            print(f"{i}. {title}")

        # Get input and play
        try:
            selection = int(input("\nSelect a track number to play: "))
            self.fsm.trigger('select', selection)
        except ValueError:
            print("Invalid input.")

# Usage
if __name__ == "__main__":
    mm = '02'
    dd = '03'
    yy = '68'
    
    show = DeadShowPlayer(f'gd{yy}-{mm}-{dd}')
    show.run()
    
