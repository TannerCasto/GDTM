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
            selected_show = result['identifier']
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
def retrieveMetadata(selected_show_identifier):
    item = ia.get_item(selected_show_identifier)
    return item