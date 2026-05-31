#!/usr/bin/env python3
# /// script
# dependencies = ["websockets"]
# ///
"""List HA device registry entries, optionally filtered by name pattern.

Usage:
  $env:HA_TOKEN = "<token>"
  uv run ha_list_devices.py [pattern]
"""
import asyncio
import json
import os
import re
import sys
import websockets

HA_URL = os.environ.get("HA_URL", "ws://192.168.0.42:8123/api/websocket")
HA_TOKEN = os.environ.get("HA_TOKEN")


async def list_devices(pattern: str | None) -> None:
    if not HA_TOKEN:
        sys.exit("ERROR: set HA_TOKEN env var")

    async with websockets.connect(HA_URL) as ws:
        await ws.recv()  # auth_required
        await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
        if json.loads(await ws.recv())["type"] != "auth_ok":
            sys.exit("AUTH FAILED")

        await ws.send(json.dumps({"id": 1, "type": "config/device_registry/list"}))
        resp = json.loads(await ws.recv())
        devices = resp.get("result", [])

        rx = re.compile(pattern, re.IGNORECASE) if pattern else None
        for d in devices:
            name = d.get("name_by_user") or d.get("name") or ""
            model = d.get("model") or ""
            mfr = d.get("manufacturer") or ""
            haystack = f"{name} {model} {mfr} {d.get('id')}"
            if rx and not rx.search(haystack):
                continue
            disabled = " [DISABLED]" if d.get("disabled_by") else ""
            print(f"{d['id']}  {name!r}  ({mfr} / {model}){disabled}")
            if d.get("identifiers"):
                print(f"    identifiers: {d['identifiers']}")
            if d.get("config_entries"):
                print(f"    config_entries: {d['config_entries']}")


if __name__ == "__main__":
    pattern = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(list_devices(pattern))
