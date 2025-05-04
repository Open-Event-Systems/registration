#!/bin/sh
event_id="$HEALTHCHECK_EVENT_ID"
curl \
    --fail \
    -X POST \
    -H 'Content-Type: application/json' \
    --data-raw "{
        \"currency\": \"USD\",
        \"cart_data\": {
            \"event_id\": \"$event_id\",
            \"registrations\": []
        }
    }" \
    http://localhost:8000/price-cart
res=$?
if [ ! "$res" -eq "0" ]; then
    exit 1
fi
echo "$res"
