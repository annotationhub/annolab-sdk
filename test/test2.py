# %%
import requests

api_key='DH5NXRA-2M3MRE5-JS86ZT3-G0MZ2V8'

headers = {
    'Authorization': f'Api-Key {api_key}'  # According to the SDK, the API key should be set as 'X-API-KEY'
}
# %%
import csv

csv_path = '/Users/lukesimkins/Documents/Crossfold/rerun_refs2.csv'
all_source_ids = []

with open(csv_path, newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        # Flatten each row and attempt to convert all entries to integers
        for item in row:
            item = item.strip()
            if item:
                all_source_ids.append(int(item))




# %%

def run_model(source_ids):
  url = 'https://api.annolab.ai/v1/model/infer/batch'
  group_name = 'Western Land'
  project_id = 3235
  modelIdentifier = 39
  layerIdentifier = 3632

  data = {
    "groupName": group_name,
    "modelIdentifier": modelIdentifier,
    "outputLayerIdentifier": layerIdentifier,
    "sourceIds": source_ids,
    "projectIdentifier": project_id
  }

  response = requests.post(url, json=data, headers=headers)
  print("Status code:", response.status_code)
  print("Response body:", response.text)

  return response
# %%
run_source_ids = all_source_ids.copy()

# %%
import time

batch_size = 5
i = 0

run_source_ids = list(set(run_source_ids))

while run_source_ids:
    batch = run_source_ids[:batch_size]
    response = run_model(batch)
    if 200 <= response.status_code < 300:
        # Remove these IDs from run_source_ids
        run_source_ids = list(filter(lambda x: x not in batch, run_source_ids))
    else:
        print("Error response - will retry this batch")
    time.sleep(0.5)

# %%
print(len(run_source_ids))
# %%
