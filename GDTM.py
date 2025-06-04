from functions import *

## GET THE ENTIRE GRATEFUL DEAD LIBRARY
search = ia.search_items('collection:GratefulDead')

## DETERMINE THE SHOW WE WANT **CHANGE THIS**
desired_show_prefix = 'gd77-05-08'     # must follow form gdyy-mm-dd

selected_show_identifier = findShow(desired_show_prefix, search)

retrieved_metadata = retrieveMetadata(selected_show_identifier)

