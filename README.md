# Home Assistant Config — Frank Sehnal

Configuration backup for Home Assistant OS running at home in Prague.

## Instance

| Parameter | Value |
|---|---|
| Version | HAOS 2026.5.0 |
| Local address | `192.168.0.42:8123` |
| Tailscale IP | `100.69.125.67` |
| Mobile dashboard | `/my-dash` |

## Hardware

**Acemagic JK09** mini PC

| Component | Spec |
|---|---|
| CPU | Intel N100, 4-core, 1.7 GHz (Turbo 3.4 GHz) |
| RAM | 16 GB DDR4 |
| Storage | 512 GB SSD |
| Network | LAN 1 Gbps + WiFi |
| USB | 4× USB 3.2 Gen 1 + USB-C |

## Zigbee

Sonoff Zigbee 3.0 USB Dongle Plus V2 — ZHA integration.

## What's Automated

- **Hallway light** — motion-triggered, day/night brightness (100% / 35%), IKEA fade fix
- **Kitchen light** — vibration sensor on counter, turns off after 60 min
- **Departure NFC** — lights off, media pause, battery warning via TTS
- **Arrival** — lights on for Fanda + Simonka separately
- **3D printer** — AE job detection, Discord embed notification, NFC toggle
- **Media Time** — PS4 on/off → TV IR + light scene
- **Daily summary** — AI-generated home report at 21:05 via TTS + notification
- **AI welcome** — personalized greeting on arrival

## Voice Assistant

Nabu pipeline (default): Claude `claude-haiku-4-5` · STT: faster-whisper · TTS: piper/amy

## Tools & Workflow

Config is edited directly via Samba (`\\192.168.0.42\config`) — no SSH needed.  
Services called via REST API. Git commits via `shell_command.git_commit_push`.

See `CLAUDE.md` for full operational instructions (entity IDs, quirks, workflow).

## Key Integrations

`ZHA` · `PrusaLink` · `Anthropic` · `OpenAI` · `Telegram Bot` · `Spotify` · `HACS` · `Tailscale`
