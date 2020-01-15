#!/bin/bash

python3 ../twarc/utils/wordcloud.py lsu_quote_replies.jsonl > wordcloud.html
python3 ../twarc/utils/geojson.py --centroid --fuzz 0.01 lsu_quote_replies.jsonl  > lsu_quote_replies_centroids.geojson
python3 ../twarc/utils/geojson.py lsu_quote_replies.jsonl  > lsu_quote_replies.geojson
python3 ../twarc/utils/network.py lsu_quote_replies.jsonl network.html
python3 ../twarc/utils/network.py --users lsu_quote_replies.jsonl network_user.html