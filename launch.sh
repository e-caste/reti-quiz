#!/bin/bash

DB=networks_quiz_bot_convo_db
DOC="Raccolta_quiz.txt"
USAGE_FILE="usage_history.json"
WORKDIR=/bot

docker run --restart unless-stopped \
           -v "$PWD"/$DB:$WORKDIR/$DB \
           -v "$PWD"/$DOC:$WORKDIR/$DOC \
           -v "$PWD"/$DOC.bak:$WORKDIR/$DOC.bak \
           -v "$PWD"/dbs_old:$WORKDIR/dbs_old \
           -v "$PWD"/"$USAGE_FILE":$WORKDIR/$USAGE_FILE \
           -e TOKEN="" \
           -e CST_CID="" \
           -e LINK="" \
           -e USAGE_FILE="$USAGE_FILE" \
           -itd netbot:latest