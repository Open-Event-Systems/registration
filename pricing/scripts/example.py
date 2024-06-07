#!/usr/bin/env python3

import json
import sys

data = json.load(sys.stdin)
prev_result = data.get("prev_result", {})
registrations = prev_result.get("registrations", [])
for reg in registrations:
    line_items = reg.get("line_items", [])
    for li in line_items:
        modifiers = li.get("modifiers", [])
        modifiers.append({"id": "discount", "name": "Discount", "amount": -100})
        li["modifiers"] = modifiers
        li["total_price"] = li.get("total_price", 0) - 100
    reg["total_price"] = reg.get("total_price", 0) - 100
    prev_result["total_price"] = prev_result.get("total_price", 0) - 100

json.dump(prev_result, sys.stdout)
