# CLAUDE.md — Home Assistant Config

Instructions for Claude Code when working with this repository.

---

## Efficiency Rules — Read First

**Priority order for all operations — always use the highest available:**

1. **HA MCP tools** — device state, service calls, announcements (zero browser)
2. **Samba + PowerShell** — read/write config files directly (`\\192.168.0.42\config`)
3. **Browser (Studio Code Server)** — last resort only (costs tokens via screenshots)

**Never open the browser just to read or write a YAML file.**
**Never take a screenshot to check file content — use PowerShell `Get-Content`.**

---

## Instance

| Parameter | Value |
|---|---|
| Local address | `192.168.0.42:8123` |
| Tailscale IP | `100.69.125.67` |
| HA version | HAOS 2026.5.0 |
| Studio Code Server | `http://192.168.0.42:8123/a0d7b954_vscode` (open from HA sidebar only) |
| Samba share | `\\192.168.0.42\config` user: `fandaborec_NAS` |

---

## Git Workflow — No Browser Needed

Git is handled via `shell_command.git_commit_push` callable through HA MCP:

```
service: shell_command.git_commit_push
data:
  message: "fix: description of change"
```

Or via PowerShell to read/write, then HA MCP to commit:
```powershell
# Read file
Get-Content "\\192.168.0.42\config\automations.yaml" -Encoding UTF8

# Write file
$content | Set-Content "\\192.168.0.42\config\automations.yaml" -Encoding UTF8 -NoNewline
```

Then call `shell_command.git_commit_push` via HA MCP with a message.

Credentials stored in `~/.git-credentials` on the HA server — no interactive auth needed.

---

## Editing Config Files

**Correct workflow (token-efficient):**
1. Read via `Get-Content "\\192.168.0.42\config\<file>.yaml"`
2. Edit via PowerShell string manipulation
3. Write back via `Set-Content "\\192.168.0.42\config\<file>.yaml" -Encoding UTF8 -NoNewline`
4. Reload via HA MCP `homeassistant.reload_all` (or specific: `automation.reload`)
5. Commit via HA MCP `shell_command.git_commit_push`

**Avoid:** opening Studio Code Server, taking screenshots of files, typing in browser terminal.

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

---

## Entities — Lights

| Entity ID | Friendly name | Type |
|---|---|---|
| `light.bulb_e27_cws_globe_806lm_kitchen` | kitchen light 1 | RGB+W (CWS) |
| `light.bulb_e27_cws_globe_806lm_sporak` | kitchen light 2 | RGB+W (CWS) |
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

| ID | Alias | Trigger |
|---|---|---|
| `1759085159743` | Notify when Phone Battery is Low (Fanda) | battery < 20 % |
| `pohybove_svetlo_chodba_casova_intenzita` | Hallway motion light | Motion in hallway, day/night intensity |
| `1759594437459` | Turn off Lights with Remote Button (GUESTS) | ZHA button 1 |
| `1759653938353` | Turn off Lights on Departure | NFC odchod ⚠️ duplicate — disable |
| `1759660818887` | Notify when Prusa MK4 finishes (old) | sensor.prusa_mk4 → finished ⚠️ superseded |
| `1759769689469` | Arrival lights (Fanda) | device enters zone.home |
| `1760463399375` | Studio Desk NFC — Start Work Session | NFC studio stul |
| `1760636015542` | Welcome and Market Update on Arrival | person → home |
| `1760638473413` | Daily Smart Home Summary | 21:05 daily |
| `1760977920980` | Control Bedroom Lights with Remote Button | ZHA button 2 |
| `1761582140338` | Turn on 3D Printer with Tag Scan | NFC tag |
| `1762973628996` | Prusa finish — AI summary (old) | sensor.prusa_mk4 → finished ⚠️ superseded |
| `1764498752529` | Lights on when PS4 turns off | PS4 off |
| `1764499575822` | Arrival lights (Simonka) | device enters zone.home |
| `1767439659694` | Media Time | PS4 on |
| `1767440741561` | Turn off Lights on Departure 2 (with battery warn) | NFC odchod ✅ keep this one |
| `1767441268976` | Battery Low (Simonka) | battery < 20 % |
| `1767804978532` | Light Off for High Phone Battery (Fanda) | battery > 20 % |
| `1771772142584` | AE Print — MK4S Finished (Smart v2) | sensor.prusa_mk4 → finished ✅ |
| `1771787973375` | AE Print — MK4S Capture + Notify | sensor.prusa_mk4 start/finish |
| `1774210332085` | Kitchen Light with Vibration (IKEA fix) | vibration 2s, PS4 off |
| `tmp_write_config` | _tmp_write_config | ⚠️ dead — delete |

---

## ZHA — Removed Services

`zha.reconfigure_device` byl odstraněn v HA 2024.10+. Žádná přímá náhrada neexistuje.

Dostupné ZHA služby (2026-06): `permit`, `remove`, `set_zigbee_cluster_attribute`, `issue_zigbee_cluster_command`, `issue_zigbee_group_command`, `warning_device_squawk`, `warning_device_warn`, lock-related services.

**ZHA config_entry_id** (Sonoff Zigbee 3.0 USB Dongle Plus V2): `01K5W85DD9P58XRMKZE9DBASXK`

Pokud je potřeba reload celého ZHA: `homeassistant.reload_config_entry` s tímto ID (pozor — odpojí všechna Zigbee zařízení na chvíli).

---

## Known Issues (pending cleanup)

| Issue | Action |
|---|---|
| ~~`notify.mobile_app_samsung_galaxy_a54` in 3 automations~~ | ✅ Sjednoceno na `_a546b` (2026-05-07) |
| ~~Automation `1759653938353` (old departure)~~ | ✅ Smazána (2026-05-08) |
| ~~Automation `1759660818887` (old Prusa notify)~~ | ✅ Smazána (2026-05-08) |
| ~~Automation `1762973628996` (Prusa AI old)~~ | ✅ Smazána (2026-05-08) |
| ~~`tmp_write_config`~~ | ✅ Smazána (2026-05-07) |
| ~~`input_text.ae_last_print_file`~~ | ✅ Vytvořen (2026-05-07) |
| ~~`1774210332088` Nightly Reconfigure — zha.reconfigure_device removed~~ | ✅ Smazána (2026-06-02) |
| ~~`1774210332087` Reconfigure on Recovery — zha.reconfigure_device removed~~ | ✅ Nahrazena notify akcí (2026-06-02) |

---

## Assist Pipeline

- **Preferred pipeline:** Nabu (Claude conversation, claude-haiku-4-5) — must be default for HA MCP tools to work
- STT: faster-whisper (local) | TTS: piper/amy/en_US (local)
- Voice aliases: `3D printer` → `switch.smart_plug_prusa_mk4s`, `hruska` → living room light

---

## IKEA Bulb Quirks

- CWS bulbs: RGB + color temp. WS bulbs: color temp only (no RGB).
- 3-step fix: `rgb_color [255,255,255]` → delay 0.7s → set `color_temp_kelvin` + `brightness`
- Double turn-off: some automations send `light.turn_off` twice with 0.7s delay to ensure bulb responds

---

## Reload vs. Restart — Decision Matrix

**Reload stačí (rychlé, preferované):**
- ✅ Automations → `POST /api/services/automation/reload`
- ✅ Scripts → `POST /api/services/script/reload`
- ✅ Scenes → `POST /api/services/scene/reload`
- ✅ Template entities → `POST /api/services/template/reload`
- ✅ Groups → `POST /api/services/group/reload`
- ✅ Themes → `POST /api/services/frontend/reload_themes`

**Vyžaduje restart (`homeassistant/restart`):**
- ❌ Min/Max senzory a platform-based senzory
- ❌ Nové integrace v `configuration.yaml`
- ❌ Změny core konfigurace
- ❌ MQTT sensor/binary_sensor platformy
- ❌ `shell_command` sekce (!)

---

## Dashboard — Vytvoření nového (Lovelace)

Nový dashboard vyžaduje **2 soubory** v `.storage/`:

1. **Samotný dashboard** — zkopírovat z existujícího:
   ```
   \\192.168.0.42\config\.storage\lovelace.my_dash → lovelace.novy_dashboard
   ```

2. **Registrace** v `\\192.168.0.42\config\.storage\lovelace_dashboards` — přidat záznam:
   ```json
   {
     "id": "novy_dashboard",
     "show_in_sidebar": true,
     "icon": "mdi:tablet-dashboard",
     "title": "Název dashboardu",
     "require_admin": false,
     "mode": "storage",
     "url_path": "novy-dashboard"
   }
   ```

3. Po uložení obou souborů — **restart HA** (reload nestačí pro nový dashboard).

---

## Jinja2 — Časté vzory

**Počet otevřených dveří/senzorů:**
```jinja2
{% set sensors = ['binary_sensor.front_door', 'binary_sensor.window_sensor'] %}
{% set open = sensors | select('is_state', 'on') | list | length %}
{{ open }} / {{ sensors | length }} otevřeno
```

**Barevné kódování dle hodnoty:**
```jinja2
{% set val = states('sensor.nejaky_sensor') | int %}
{% if val <= 1 %}red
{% elif val <= 3 %}amber
{% elif val <= 7 %}yellow
{% else %}green
{% endif %}
```

**Podmíněný seznam (append pattern):**
```jinja2
{% set items = [] %}
{% if condition_a %}{% set items = items + ['Položka A'] %}{% endif %}
{% if condition_b %}{% set items = items + ['Položka B'] %}{% endif %}
{% if items %}{{ items | join(', ') }}{% else %}Žádné položky{% endif %}
```