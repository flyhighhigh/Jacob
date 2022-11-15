#!/bin/sh
while true; do
    inotifywait -q -m -e CLOSE_WRITE --format="git add . && git commit -m 'auto commit on change (reports.json)' && git push origin main" ./reports.json | bash
done
