#!/bin/bash

echo "Checking services status..."
echo "---------------------------"

services=(api redis redisinsight prometheus grafana)
fail=0

for svc in "${services[@]}"; do
    echo -n "$svc: "
    id=$(docker-compose ps -q "$svc")
    if [ -z "$id" ]; then
        echo "NOT FOUND"
        ((fail++))
    elif [ "$(docker inspect -f '{{.State.Running}}' "$id")" = "true" ]; then
        echo "RUNNING"
    else
        echo "STOPPED"
        ((fail++))
    fi
done

echo "---------------------------"
ok=$(( ${#services[@]} - fail ))
echo "$ok of ${#services[@]} services are running."

[ $fail -eq 0 ] && echo "All good!" && exit 0 || echo "$fail issue(s) found." && exit 1
