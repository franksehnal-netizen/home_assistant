<#
.SYNOPSIS
Refactor device_id UUID references in automations.yaml to entity_id form.

.DESCRIPTION
Reads automations.yaml, finds all `device_id: <UUID>` blocks (including the legacy
`type: turn_on/turn_off` device action form), looks up the corresponding entity_id
via HA REST API, and rewrites the block as `target: { entity_id: ... }` + matching
action verb.

Default mode is DRY-RUN (prints proposed diff to stdout). Pass -Apply to write.

.PARAMETER Apply
Write the result back to automations.yaml. Without this, only the diff is printed.

.PARAMETER Token
HA long-lived access token. Defaults to env var HA_TOKEN.

.EXAMPLE
  $env:HA_TOKEN = "..."
  .\refactor_device_ids.ps1            # dry-run
  .\refactor_device_ids.ps1 -Apply     # write

#>
param(
    [switch]$Apply,
    [string]$Token = $env:HA_TOKEN
)

if (-not $Token) {
    Write-Error "Set `$env:HA_TOKEN or pass -Token"
    exit 1
}

$YamlPath = "\\192.168.0.42\config\automations.yaml"
$BackupPath = "\\192.168.0.42\config\automations.yaml.bak"
$HaUrl = "http://192.168.0.42:8123"
$Headers = @{Authorization = "Bearer $Token"}

Write-Host "Loading device + entity registry..." -ForegroundColor Cyan

# Pull device registry via WebSocket-equivalent through Python helper, OR via direct HA API
# Simpler: REST API exposes entity registry via /api/config/entity_registry/list — but only via WebSocket.
# Workaround: use template render to map device_id -> entity_id for known domains.

# Get all entities and their device_id via /api/states + attributes is not enough.
# Use template service:
$tplBody = @{
    template = '{% for s in states %}{{ s.entity_id }}|{{ device_id(s.entity_id) }}{{ "\n" }}{% endfor %}'
} | ConvertTo-Json -Compress

$result = Invoke-RestMethod "$HaUrl/api/template" -Method POST -Headers $Headers -Body $tplBody -ContentType "application/json"

# Build device_id -> [entity_ids] map
$deviceToEntities = @{}
foreach ($line in $result -split "`n") {
    if ($line -match '^([^|]+)\|(.+)$') {
        $eid = $matches[1].Trim()
        $did = $matches[2].Trim()
        if ($did -and $did -ne 'None') {
            if (-not $deviceToEntities.ContainsKey($did)) {
                $deviceToEntities[$did] = @()
            }
            $deviceToEntities[$did] += $eid
        }
    }
}

Write-Host "Loaded $($deviceToEntities.Count) devices with mappings" -ForegroundColor Cyan

# Read YAML
$content = Get-Content $YamlPath -Raw -Encoding UTF8
$original = $content

# Pattern 1: `type: turn_on / type: turn_off + device_id + entity_id + domain` (legacy device action form)
# Replace with `action: <domain>.turn_X / target: { entity_id: <entity> }`
$pattern1 = '(?ms)(\s+)- type: (turn_on|turn_off)\s+device_id: ([a-f0-9]+)\s+entity_id: ([a-f0-9]+)\s+domain: (\w+)'

$replacements = @()
$matchCount = 0

# Match-and-collect approach to show user the diff
$regex1 = [regex]::new('(?ms)(\s+)- type: (turn_on|turn_off)\s+device_id: ([a-f0-9]+)\s+entity_id: ([a-f0-9]+)\s+domain: (\w+)')
$matches1 = $regex1.Matches($content)

Write-Host "`nFound $($matches1.Count) legacy device-action blocks (type: turn_on/off + device_id)" -ForegroundColor Yellow

$newContent = $content
foreach ($m in $matches1) {
    $indent = $m.Groups[1].Value
    $verb = $m.Groups[2].Value       # turn_on / turn_off
    $deviceId = $m.Groups[3].Value
    $entityRefHash = $m.Groups[4].Value  # this is registry hash, not entity_id - we need lookup by device_id
    $domain = $m.Groups[5].Value

    # Find an entity_id whose registry entry has this device_id AND matches this domain
    # CRITICAL: wrap @() to force array — PowerShell Where-Object unwraps single results to string
    $candidates = @()
    if ($deviceToEntities.ContainsKey($deviceId)) {
        $candidates = @($deviceToEntities[$deviceId] | Where-Object { $_ -like "$domain.*" })
    }

    # Filter out secondary entities (child-lock, disable-LED toggles) when picking the main switch/light
    if ($candidates.Count -gt 1) {
        $primary = @($candidates | Where-Object { $_ -notmatch '_detsky_zamek$|_zakazat_led$|_identifikovat$' })
        if ($primary.Count -eq 1) {
            $candidates = $primary
        }
    }

    if ($candidates.Count -eq 1) {
        $entityId = $candidates[0]
        $oldBlock = $m.Value
        $newBlock = "$indent- action: $domain.$verb`n$indent  target:`n$indent    entity_id: $entityId"
        $newContent = $newContent.Replace($oldBlock, $newBlock)
        $replacements += [PSCustomObject]@{
            Match = "type: $verb + device_id: $($deviceId.Substring(0,8))..."
            Resolved = "$domain.$verb -> $entityId"
        }
        $matchCount++
    } elseif ($candidates.Count -gt 1) {
        Write-Warning "Device $deviceId has multiple $domain entities: $($candidates -join ', '). Skipping."
    } else {
        Write-Warning "Device $deviceId not found or no $domain entity. Skipping."
    }
}

if ($matchCount -eq 0) {
    Write-Host "`nNo refactorable matches found." -ForegroundColor Green
    exit 0
}

Write-Host "`n=== PROPOSED CHANGES ($matchCount) ===" -ForegroundColor Green
$replacements | Format-Table -AutoSize

if ($Apply) {
    # Backup
    Copy-Item $YamlPath $BackupPath -Force
    Write-Host "Backed up to $BackupPath" -ForegroundColor Cyan
    # Write
    Set-Content -Path $YamlPath -Value $newContent -Encoding UTF8 -NoNewline
    Write-Host "Wrote refactored YAML to $YamlPath" -ForegroundColor Green
    Write-Host "Now reload automations: POST /api/services/automation/reload" -ForegroundColor Yellow
} else {
    Write-Host "`nDRY-RUN. Re-run with -Apply to write changes." -ForegroundColor Yellow
}
