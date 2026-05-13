$outDir = "output"
$workspaceRoot = ".."

$targetDirs = @(
    "$workspaceRoot\static\static",
    "$workspaceRoot\backend\open_webui\static",
    "$workspaceRoot\backend\open_webui\static\swagger-ui",
    "$workspaceRoot\static"
)

Write-Host "Ersetze die Bilder in den Open WebUI Ordnern..." -ForegroundColor Cyan

foreach ($dir in $targetDirs) {
    if (Test-Path $dir) {
        Write-Host "Kopiere Dateien nach $dir..." -ForegroundColor Yellow
        
        # Array von Dateinamen, die ersetzt werden sollen
        $filesToCopy = @(
            "logo.png",
            "splash.png",
            "favicon.svg",
            "favicon.png",
            "favicon.ico",
            "favicon-96x96.png",
            "favicon-dark.png",
            "apple-touch-icon.png"
        )

        foreach ($file in $filesToCopy) {
            $sourceFile = Join-Path $outDir $file
            $targetFile = Join-Path $dir $file
            
            # Kopiere die Datei, auch wenn sie noch nicht existiert
            if (Test-Path $sourceFile) {
                # Testen ob die zieldatei da ist um nur dort zu überschreiben wo sie schon waren
                if (Test-Path $targetFile) {
                    Write-Host "  -> Ersetze $file"
                    Copy-Item $sourceFile $targetFile -Force
                }
            }
        }
    } else {
        Write-Host "Verzeichnis nicht gefunden: $dir" -ForegroundColor Red
    }
}

# Zusätzliches Fallback (falls etwas direkt im /static root fehlt)
Copy-Item "$outDir\favicon.png" "$workspaceRoot\static\favicon.png" -Force
Copy-Item "$outDir\splash.png" "$workspaceRoot\static\splash.png" -Force
Copy-Item "$outDir\logo.png" "$workspaceRoot\static\logo.png" -Force

Write-Host "Fertig! Alle Logos wurden erfolgreich ersetzt." -ForegroundColor Green
