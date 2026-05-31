#!/usr/bin/env python3
# /// script
# dependencies = ["websockets"]
# ///
"""Disable a HA config entry by ID.

Usage:
  $env:HA_TOKEN = "<token>"
  uv run ha_disable_config_entry.py <entry_id>
"""
import asyncio
import json
import os
import sys
import websockets

HA_URL = os.environ.get("HA_URL", "ws://192.168.0.42:8123/api/websocket")
HA_TOKEN = os.environ.get("HA_TOKEN")


async def disable_entry(entry_id: str) -> None:
    if not HA_TOKEN:
        sys.exit("ERROR: set HA_TOKEN env var")
    async with websockets.connect(HA_URL) as ws:
        await ws.recv()
        await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
        if json.loads(await ws.recv())["type"] != "auth_ok":
            sys.exit("AUTH FAILED")
        await ws.send(json.dumps({
            "id": 1,
            "type": "config_entries/disable",
            "entry_id": entry_id,
            "disabled_by": "user",
        }))
        print(json.dumps(json.loads(await ws.recv()), indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: ha_disable_config_entry.py <entry_id>")
    asyncio.run(disable_entry(sys.argv[1]))
