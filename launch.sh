#!/bin/bash

DB=networks_quiz_bot_convo_db
DOC="Raccolta_quiz.txt"
WORKDIR=/bot

docker run --restart unless-stopped \
           -v "$PWD"/$DB:$WORKDIR/$DB \
           -v "$PWD"/$DOC:$WORKDIR/$DOC \
           -v "$PWD"/$DOC.bak:$WORKDIR/$DOC.bak \
           -e TOKEN="" \
           -e CST_CID="" \
           -e LINK="" \
           -itd netbot:latest