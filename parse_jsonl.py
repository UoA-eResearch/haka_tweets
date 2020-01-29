#!/usr/bin/env python3

import pandas as pd

df = pd.read_json("lsu_quote_replies.jsonl", lines=True)
df["screen_name"] = df.user.apply(lambda x: x.get("screen_name"))
df["location"] = df.place.apply(lambda x: x["full_name"] + ", " + x["country"] if x is not None else None)
df["bounding_box"] = df.place.apply(lambda x: x["bounding_box"] if x else None)
df["in_reply_to_status_id"] = df["in_reply_to_status_id"].astype('Int64')
df[["id", "created_at", "screen_name", "full_text", "favorite_count", "retweet_count", "in_reply_to_status_id", "location", "bounding_box"]].to_csv("lsu_quote_replies.csv", index=False)
