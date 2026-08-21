# %%
from time import sleep
import annolab
import os
from requests.exceptions import HTTPError
# %%
api_key='DH5NXRA-2M3MRE5-JS86ZT3-G0MZ2V8'

lab = annolab.AnnoLab(api_key=api_key)
# %%
import os
abstractId = 33166
folder = 'Montmorency County'
pdf_folder = f"/Users/lukesimkins/Downloads/{folder}"
pdf_files = []

for root, dirs, files in os.walk(pdf_folder):
    for file in files:
        if file.lower().endswith(".pdf"):
            pdf_files.append(os.path.join(root, file))

for pdf_file in pdf_files:
    print(pdf_file)
# %%
project = lab.find_project('Easements', 'Western Land')
# %%
def upload_file(file, name, directory, abstractId):
  return project.create_pdf_source(
      file=file,
      name=name,
      directory=directory,
      metadata={
          'path': os.path.relpath(file, f"/Users/lukesimkins/Downloads"),
      },
      ocr=True,
      preprocessor='none',
      timeout=60.0,
      abstractId=abstractId,
      workflow='easements',
  )
# %%
global resp
def start_uploads():
  process_files = pdf_files.copy()
  for i, file in enumerate(process_files):
    print(f"Processing file {i+1}/{len(process_files)}, path: {file}")

    global resp
    try:
      resp = upload_file(file, os.path.basename(file), folder, abstractId)
    except HTTPError as e:
        # Check for 409 Conflict (duplicate)
        if hasattr(e, "response") and getattr(e.response, "status_code", None) == 409:
            print('Handling 409 Conflict')
            if hasattr(e.response, "text"):
                print("Response body:", e.response.text)

            # Convert the full pdf path to a safe name by replacing "/" with "-"
            safe_name = os.path.relpath(file, f"/Users/lukesimkins/Downloads/{folder}").replace("/", " ")
            new_file = safe_name

            resp = upload_file(file, os.path.basename(new_file), folder, abstractId)
        else:
            raise
    pdf_files.remove(file)
    sleep(0.2)
# %%
from requests.exceptions import ReadTimeout
while True:
    try:
        start_uploads()
        break
    except (ReadTimeout, HTTPError) as e:
        if isinstance(e, ReadTimeout) or (
            isinstance(e, HTTPError)
            and hasattr(e, "response")
            and getattr(e.response, "status_code", None) == 502
        ):
            # Handle ReadTimeout or 502 Bad Gateway, retry
            print("ReadTimeout or HTTP 502 occurred, restarting upload process...")
            sleep(10)
            continue
        else:
            raise
        print("ReadTimeout occurred, restarting upload process...")
        sleep(10)
        continue
# %%

# %%
print('test')
# %%
len(pdf_files)
# %%

# %%
