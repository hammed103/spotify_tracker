# %%
import requests
import base64
from time import sleep

client_id = '53fb1dbe5f42480ba654fcc3c7e168d6'
client_secret = '5c1da4cce90f410e88966cdfc0785e3a'

auth_str = client_id + ':' + client_secret
b64_auth_str = base64.b64encode(auth_str.encode()).decode()

auth_options = {
    'url': 'https://accounts.spotify.com/api/token',
    'headers': {
        'Authorization': 'Basic ' + b64_auth_str
    },
    'data': {
        'grant_type': 'client_credentials'
    }
}

response = requests.post(**auth_options)
if response.status_code == 200:
    token = response.json()['access_token']


# %%
import subprocess
import json

def vio(track_id) :


    headers = {
        'Authorization': f'Bearer {token}' # Replace with actual token
    }

    response = requests.get(f'https://api.spotify.com/v1/tracks/{track_id}', headers=headers)

    if response.status_code == 200:
        track_data = response.json()
        # Do something with the track data
    else:
        print(f'Error: {response.status_code}')


    album_id = track_data["album"]["id"]
    curl_command = ["curl", f"http://localhost:8080/albumPlayCount?albumid={album_id}"]
    result = subprocess.run(curl_command, capture_output=True, text=True)
    output = result.stdout.strip()

    # Do something with the output variable


    # parse the JSON string to a Python object
    result = json.loads(output)

    # print the result
    try :
        cnt = [i for i in result["data"]["discs"][0]["tracks"] if i["uri"] == track_data["uri"]][0]["playcount"]
    except:
        print(track_id,album_id)
        cnt = 0
    sleep(1.5)
    return cnt

# %%
import pandas as pd
import numpy as np
from tqdm.notebook import tqdm
tqdm.pandas()


# %%


# Define a function to add new data for a given day
def add_data(df):
    # Add the data for the new day as a new column
    new_cols = [f"Day {int(col.split(' ')[-1])+1}" if col.startswith('Day') else col for col in df.columns]


    # Rename the columns using the new list of column names
    df.columns = new_cols
    print(df.columns)
    
    total_streams = df["trackId"].progress_apply(vio) 


    df["Day 1"] = total_streams - df["total_streams"]

    df["total_streams"] = total_streams


    

    # Define the desired column order
    desired_cols = ['title', 'album', 'isrc', 'trackId', 'url', 'total_streams', 'Day 1',
       'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8']

    # Reorder the columns using the reindex method
    df = df.reindex(columns=desired_cols)

    
    # If there are more than 7 columns, delete the 8th column (i.e., the oldest day's data)
    if len(df.columns) > 13:
        oldest_day = df.columns[-1]
        df.drop(columns=[oldest_day], inplace=True)

    return df








# %%
import pygsheets
import pandas as pd

# Authenticate using your Google API credentials
# Obtained freely from googlesheetapi
gc = pygsheets.authorize(service_file="my-project-1515950162194-ea018b910e23.json")

# Open the Excel sheet by its name
sh = gc.open('Track IDs to scrape')

# Select the first worksheet in the Excel sheet
wks = sh[1]

# %%
pt = wks.get_as_df()

base = pd.read_csv("base.csv")
pt = pt.merge(base,how="left")


# %%
df = add_data(pt)

# %%
df.to_csv("base.csv",index=False)

# %%
df["Last 7 days"] = df[['Day 1','Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7',]].sum(axis=1)
df = df.drop(columns=[ 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7',]).rename(columns={"Day 1":"Today","Day 2":"Yesterday",})

# %%
df

# %%
wks.clear()

# %%
wks.set_dataframe(df, start='A1')

# %%



