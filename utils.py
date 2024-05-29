# Create a csv file of the issues
#
# python utils.py
import os
import json
import pandas as pd


def concat_issues():
    json_files = []
    for file in os.listdir(os.getcwd()):
        if file.startswith("issue_detail_"):
            json_files.append(file)
    json_files = sorted(json_files)

    df = pd.DataFrame()
    for file in json_files:
        print(file)
        with open(file, "r") as f:
            data = json.load(f)
        _df = pd.json_normalize(data)
        df = pd.concat([df, _df], axis=0).reset_index(drop=True)

    df.to_csv("issue_details.csv")
    df["author.login"].drop_duplicates().to_csv("issue_posters.csv")


def concat_posters():
    json_files = []
    for file in os.listdir(os.getcwd()):
        if file.startswith("poster_"):
            json_files.append(file)
    json_files = sorted(json_files)

    df = pd.DataFrame()
    for file in json_files:
        print(file)
        with open(file, "r") as f:
            data = json.load(f)
        _df = pd.json_normalize(data)
        df = pd.concat([df, _df], axis=0).reset_index(drop=True)

    df.to_csv("poster_details.csv")


def join_csvs():
    df = pd.read_csv("issue_details.csv")
    df2 = pd.read_csv("poster_details.csv").rename(columns={"login": "author.login"})
    df = df.merge(df2, on="author.login")
    df.to_csv("issue_details_with_posters.csv")


if __name__ == "__main__":
    # concat_issues()
    # concat_posters()
    join_csvs()
