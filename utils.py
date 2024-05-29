# Create a csv file of the issues
#
# python utils.py
import ast
import os
import json
import subprocess
import pandas as pd


def pull_issues():
    subprocess.run(["./pull_issues.zsh"], capture_output=True, text=True)


def pull_posters():
    subprocess.run(["./pull_posters.zsh"], capture_output=True, text=True)


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

    df.to_csv("all_poster_details.csv")


def join_csvs():
    df = pd.read_csv("issue_details.csv")
    df2 = pd.read_csv("all_poster_details.csv").rename(
        columns={"login": "author.login"}
    )
    df = df.merge(df2, on="author.login")

    # Helper columns to steer the LLM
    def extract_reaction_counts(reaction_groups):
        reactions = {
            "THUMBS_UP": 0,
            "THUMBS_DOWN": 0,
            "LAUGH": 0,
            "HOORAY": 0,
            "CONFUSED": 0,
            "HEART": 0,
            "ROCKET": 0,
            "EYES": 0,
        }

        if reaction_groups != "[]":
            reaction_list = ast.literal_eval(reaction_groups)
            for reaction in reaction_list:
                content = reaction["content"]
                count = reaction["users"]["totalCount"]
                if content in reactions:
                    reactions[content] += count

        return pd.Series(
            [
                reactions["THUMBS_UP"],
                reactions["THUMBS_DOWN"],
                reactions["LAUGH"],
                reactions["HOORAY"],
                reactions["CONFUSED"],
                reactions["HEART"],
                reactions["ROCKET"],
                reactions["EYES"],
            ]
        )

    df[
        [
            "n_body_reactions_thumbs_up",
            "n_body_reactions_thumbs_down",
            "n_body_reactions_laugh",
            "n_body_reactions_hooray",
            "n_body_reactions_confused",
            "n_body_reactions_heart",
            "n_body_reactions_rocket",
            "n_body_reactions_eyes",
        ]
    ] = df["reactionGroups"].apply(extract_reaction_counts)

    def extract_commenters(comments):
        if comments == "[]":
            return "[]"

        commenters = set()
        comment_list = ast.literal_eval(comments)
        for comment in comment_list:
            commenters.add(comment["author"]["login"])

        return str(list(commenters))

    df["commenters"] = df["comments"].apply(extract_commenters)

    df.to_csv("issue_details_with_posters.csv")


def upload_csv_to_hugging_face_hub():
    from huggingface_hub import HfApi, HfFolder

    token = os.environ["HF_WRITE_TOKEN"]
    HfFolder.save_token(token)
    username = "raybellwaves"
    repo_name = "raybellwaves-llm-issue-explorer-issues"
    file_path = "issue_details_with_posters.csv"

    api = HfApi()
    api.upload_file(
        path_or_fileobj=file_path,
        path_in_repo=file_path,
        repo_id=f"{username}/{repo_name}",
        repo_type="dataset",
        token=token,
    )


def read_csv_from_hugging_face_hub():
    from datasets import load_dataset

    dataset = load_dataset("raybellwaves/raybellwaves-llm-issue-explorer-issues")
    df = dataset["train"].to_pandas()
    return df


def chat_to_dataset_using_langchain():
    from langchain_experimental.agents.agent_toolkits import (
        create_pandas_dataframe_agent,
    )
    from langchain_openai import OpenAI

    df = read_csv_from_hugging_face_hub()
    agent = create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=True)
    agent.invoke("how many rows are there?")["output"]
    # agent.invoke("How many different companies created an issue?")["output"]
    # agent.invoke("Which user created the most issues?")["output"]
    # agent.invoke(
    #     "Using the reactionGroups column, which issue has the most THUMBS_UP?"
    # )["output"]


def chat_to_dataset_using_pandasai():
    from pandasai import SmartDataframe
    from pandasai.llm import OpenAI

    llm = OpenAI(api_token=os.environ["OPENAI_API_KEY"])
    df = read_csv_from_hugging_face_hub()
    smart_df = SmartDataframe(df, config={"llm": llm})
    smart_df.chat("How many rows are there?")
    smart_df.chat("How many different companies created an issue?")
    smart_df.chat("Which user created the most issues?")
    smart_df.chat(
        "Using the reactionGroups column, which issue has the most THUMBS_UP?"
    )


if __name__ == "__main__":
    # python utils.py
    #
    pull_issues()
    concat_issues()
    pull_posters()
    concat_posters()
    join_csvs()
    # upload_csv_to_hugging_face_hub()
    # chat_to_dataset_using_langchain()
    # pass
