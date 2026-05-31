#!/usr/bin/env python3
# /// script
# dependencies = ["websockets"]
# ///
"""Remove a ZHA Zigbee device by IEEE address.

Usage:
  $env:HA_TOKEN = "<token>"
  uv run ha_zha_remove.py <ieee>
"""
import asyncio
import json
import os
import sys
import websockets

HA_URL = os.environ.get("HA_URL", "ws://192.168.0.42:8123/api/websocket")
HA_TOKEN = os.environ.get("HA_TOKEN")


async def remove_zha_device(ieee: str) -> None:
    if not HA_TOKEN:
        sys.exit("ERROR: set HA_TOKEN env var")

    async with websockets.connect(HA_URL) as ws:
        await ws.recv()
        await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
        if json.loads(await ws.recv())["type"] != "auth_ok":
            sys.exit("AUTH FAILED")

        await ws.send(json.dumps({
            "id": 1,
            "type": "zha/devices/remove",
            "ieee": ieee,
        }))
        resp = json.loads(await ws.recv())
        print(json.dumps(resp, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: ha_zha_remove.py <ieee>")
    asyncio.run(remove_zha_device(sys.argv[1]))
