$env:CORS_ALLOW_ORIGIN = "*"

# Verwende die Umgebungsvariable PORT, falls gesetzt, ansonsten 8080
$port = if ($env:PORT) { $env:PORT } else { "8081" }

# Verwende die Umgebungsvariable FORWARDED_ALLOW_IPS, falls gesetzt, ansonsten "*"
$forwarded_ips = if ($env:FORWARDED_ALLOW_IPS) { $env:FORWARDED_ALLOW_IPS } else { "*" }

Write-Host "Starte uvicorn Server auf Port $port..." -ForegroundColor Green

# Use --forwarded-allow-ips="$forwarded_ips" to prevent PowerShell from expanding the * glob
uvicorn open_webui.main:app --port $port --host 0.0.0.0 "--forwarded-allow-ips=$forwarded_ips" --reload
