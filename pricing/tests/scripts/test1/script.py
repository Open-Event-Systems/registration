#!/usr/bin/env python3
import json
import sys

request = json.load(sys.stdin)

result_registrations = []

cart = request["cart"]
registrations = cart["registrations"]
for reg in registrations:
    result_registrations.append(
        {
            "id": reg["id"],
            "line_items": [
                {
                    "name": "Test",
                    "price": 100,
                    "total_price": 100,
                }
            ],
            "total_price": 100,
        }
    )

result = {"total_price": 100, "currency": "USD", "registrations": result_registrations}

output = {
    **request,
    "results": [
        *request["results"],
        result,
    ],
}

json.dump(output, sys.stdout)
