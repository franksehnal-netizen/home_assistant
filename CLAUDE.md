# CLAUDE.md — Home Assistant Config

Instructions for Claude Code when working with this repository.

---

## Instance

| Parameter | Value |
|---|---|
| Local address | `192.168.0.42:8123` |
| Tailscale IP | `100.69.125.67` |
| HA version | HAOS 2026.4.x |
| Studio Code Server | `http://192.168.0.42:8123/a0d7b954_vscode` (open from HA sidebar) |

---

## Git Workflow

All git operations run in Studio Code Server terminal (`/config` is the working dir).

```bash
# After making changes:
git add -A
git commit -m "short description"
git push
```

Credentials are stored in `~/.git-credentials` — no token needed interactively.

---

## .gitignore Rules

Excluded (never commit):
- `secrets.yaml` — API tokens, passwords
- `.cloud/` — HA Cloud private keys and certs
- `.storage/` — runtime state
- `home-assistant_v2.db*` — recorder DB
- `zigbee.db*` — ZHA Zigbee DB
- `www/community/` — HACS frontend bundles
- `*.log*`, `.ha_run.lock`, `tts/`, `image/`, `.cache/`

Committed:
- `configuration.yaml`, `automations.yaml`, `scripts.yaml`, `scenes.yaml`
- `blueprints/`, `custom_components/`, `www/` (except community/)
- `.gitignore`, `.HA_VERSION`

---

## Editing Automations

### Preferred: Edit YAML directly in Studio Code Server
1. Open Studio Code Server from HA sidebar
2. Edit `automations.yaml`
3. Reload via top bar button or `git commit && git push`

### Via REST API (from Claude in Chrome on HA page)
```javascript
// Read automation
fetch('/api/config/automation/config/{id}', {
  headers: { Authorization: 'Bearer ' + document.querySelector('home-assistant').hass.auth.data.access_token }
}).then(r => r.json()).then(console.log)

// Call service
document.querySelector('home-assistant').hass.callService('domain', 'service', { entity_id: 'entity.id' })

// Get entity state
document.querySelector('home-assistant').hass.states['entity.id'].state
```

> Note: REST API calls from external servers (outside local network) fail with 403 CORS.

---

## Entities — Lights

| Entity ID | Friendly name | Type |
|---|---|---|
| `light.bulb_e27_cws_globe_806lm_kitchen` | kitchen light 1 | RGB+W |
| `light.bulb_e27_cws_globe_806lm_sporak` | kitchen light 2 | RGB+W |
| `light.kuchyne` | kitchen lights | group |
| `light.obyvak_kuchyne` | main room lights | group (living+kitchen) |
| `light.bulb_e27_cws_globe_806lm_hruska` | living room light | RGB+W; alias: `hruska` |
| `light.bulb_e27_ws_globe_1055lm_chodba` | hall light | WS only (no RGB) |
| `light.led_strip_studio` | LED Strip - studio | ambient, studio desk |
| `light.led_strip_bedroom` | LED Strip - bedroom | |
| `light.bulb_red_bedroom` | Bulb red bedroom | |
| `light.bedroom` | bedroom lights | group |

---

## Entities — Switches (Smart Plugs)

| Entity ID | Friendly name | Controls |
|---|---|---|
| `switch.smart_plug_desktop_pc` | Smart plug - desktop PC | Desktop PC |
| `switch.smart_plug_prusa_mk4s` | Smart plug - Prusa MK4S | Prusa MK4S; alias: `3D printer` |
| `switch.ikea_of_sweden_inspelning_smart_plug` | Smart plug - speakers | Studio audio gear |
| `switch.smart_plug_cognitive_light` | Smart plug - cognitive light | Cognitive light |

---

## Entities — Sensors

| Entity ID | Friendly name |
|---|---|
| `binary_sensor.vibration_sensor_kitchen` | Vibration sensor kitchen |
| `binary_sensor.motion_sensor_chodba` | Motion Sensor - hallway |
| `binary_sensor.motion_sensor_chodba_otevirani` | Motion Sensor - hallway opening |
| `binary_sensor.window_sensor` | Window sensor (on = open) |
| `binary_sensor.studio_is_active` | Studio Is Active |
| `binary_sensor.desktop_pc_is_active` | Desktop PC Is Active |
| `binary_sensor.prusa_mk4s_is_printing` | Prusa MK4S Is Printing |

---

## Entities — Media Players

| Entity ID | Friendly name |
|---|---|
| `media_player.playstation_4` | PlayStation 4 |
| `media_player.living_room_speaker` | Google Nest speaker |
| `media_player.spotify_frank_sehnal` | Spotify Frank Sehnal |
| `media_player.vlc_telnet` | VLC-TELNET |

---

## Entities — Scenes

| Entity ID | Friendly name |
|---|---|
| `scene.movie_night` | Movie time |
| `scene.normalni_stav` | Normal state |
| `scene.main_room_sleep_mode` | Main room sleep mode |
| `scene.bed_time` | Bed time |
| `scene.main_room_after_my_arrival` | Main room after my arrival |

---

## Automations

| ID | Name | Trigger |
|---|---|---|
| `1767439659694` | Media Time | PS4 activation |
| `1774210332085` | Vibration sensor kitchen | Vibration 2s, PS4 off |
| `pohybove_svetlo_chodba_casova_intenzita` | Hallway motion light | Motion in hallway |
| `1760638473413` | Daily Smart Home Summary | 21:05 daily → notify `mobile_app_sm_a546b` |
| — | Start the PC | manual / voice |

---

## Assist Pipeline

- **Preferred pipeline:** Nabu (Claude conversation, claude-haiku-4-5) — must be default for HA MCP tools to work
- STT: faster-whisper (local) | TTS: piper/amy/en_US (local)
- Voice aliases: `3D printer` → `switch.smart_plug_prusa_mk4s`, `hruska` → living room light

---

## Tools & Access

| Tool | Use case |
|---|---|
| HA MCP Server (`192.168.0.42:8123/mcp_server/sse`) | Query state, control devices from Claude Code |
| Claude in Chrome + `hass.callService()` | Direct service calls, fastest |
| Studio Code Server terminal | Git, YAML editing, shell commands |
| Samba share `\\192.168.0.42\config` (user: `fandaborec_NAS`) | Direct file access from Windows |

---

## IKEA Bulb Quirks

- CWS bulbs support RGB+color temp; WS bulbs = color temp only (no RGB)
- Double turn-off fix: if bulb doesn't respond, power cycle
- Mushroom cards: requires v5.1.1+ (older sends deprecated mired)
