from functions import *

## GET THE ENTIRE GRATEFUL DEAD LIBRARY
search = ia.search_items('collection:GratefulDead')

## DETERMINE THE SHOW WE WANT **CHANGE THIS**
desired_show_prefix = 'gd76-06-11'     # must follow form gdyy-mm-dd

# get and display show identifier
selected_show_identifier = findShow(desired_show_prefix, search)

# retrieve metadata from the show
mp3_urls = get_mp3_urls(selected_show_identifier)   # type list

for i, (title, url) in enumerate(mp3_urls.items(), start=1):
    # print(f"{i}. {title}   {url}") #print url too
    print(f"{i}. {title}") #print url too

# get input to ask what show to play
show_selection = int(input('Track Number: '))

# play show
song = list(mp3_urls.values())[show_selection-1]
play_url_with_loop(song)
