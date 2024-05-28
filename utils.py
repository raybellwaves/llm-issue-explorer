# Create a csv file of the issues
import os
import json
import pandas as pd

json_files = []
for file in os.listdir(os.getcwd()):
    if file.endswith(".json"):
        json_files.append(file)
json_files = sorted(json_files)

df = pd.DataFrame()
for file in json_files:
    with open(file, "r") as f:
        data = json.load(f)
        print(data)
    _df = pd.json_normalize(data)
    df = pd.concat([df, _df], axis=0).reset_index(drop=True)

df.to_csv("issue_details.csv")
