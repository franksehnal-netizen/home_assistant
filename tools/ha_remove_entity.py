#!/usr/bin/env python3
# /// script
# dependencies = ["websockets"]
# ///
"""
HA entity registry remove utility.

Usage:
  $env:HA_TOKEN = "<token>"
  uv run ha_remove_entity.py <entity_id> [<entity_id> ...]

Removes orphan entities from the entity registry via WebSocket API.
Only works on entities that are 'unavailable' or already disabled.
"""
import asyncio
import json
import os
import sys
import websockets

HA_URL = os.environ.get("HA_URL", "ws://192.168.0.42:8123/api/websocket")
HA_TOKEN = os.environ.get("HA_TOKEN")


async def remove_entities(entity_ids: list[str]) -> None:
    if not HA_TOKEN:
        sys.exit("ERROR: set HA_TOKEN env var")

    async with websockets.connect(HA_URL) as ws:
        # auth handshake
        hello = json.loads(await ws.recv())
        assert hello["type"] == "auth_required", hello
        await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
        result = json.loads(await ws.recv())
        if result["type"] != "auth_ok":
            sys.exit(f"AUTH FAILED: {result}")

        msg_id = 1
        for entity_id in entity_ids:
            await ws.send(json.dumps({
                "id": msg_id,
                "type": "config/entity_registry/remove",
                "entity_id": entity_id,
            }))
            resp = json.loads(await ws.recv())
            ok = resp.get("success", False)
            err = resp.get("error", {}).get("message", "")
            print(f"{'OK  ' if ok else 'FAIL'}  {entity_id}  {err}")
            msg_id += 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: ha_remove_entity.py <entity_id> [<entity_id> ...]")
    asyncio.run(remove_entities(sys.argv[1:]))
