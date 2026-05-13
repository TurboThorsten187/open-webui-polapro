$sourceSvg = "source_logo.svg"
$outDir = "output"

if (-not (Test-Path $sourceSvg)) {
    Write-Host "Fehler: Die Datei '$sourceSvg' wurde nicht gefunden." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

Write-Host "Generiere Bilder mit extra Padding im Ordner '$outDir'..." -ForegroundColor Cyan

# 1. Padded transparent logo (Basis-Ebene)
# Bild auf 250x250 verkleinern (für deutlich größere Ränder) 
# und zentriert in 512x512 transparent einfügen
magick convert -background none $sourceSvg -resize 250x250 -gravity center -extent 512x512 padded_logo.png

# Farbumgekehrte Version des Logos für den Dark Mode herstellen (Schwarz wird Weiß, Alpha bleibt)
magick convert padded_logo.png -channel RGB -negate padded_logo_white.png

# 2. Splash Screen (nur das schwarze Logo mit großem unsichtbarem Rand)
Copy-Item padded_logo.png "$outDir\splash.png" -Force

# 3. Kreise als Hintergründe erschaffen
magick convert -size 512x512 xc:none -fill white -draw "circle 256,256 256,0" white_circle.png
magick convert -size 512x512 xc:none -fill black -draw "circle 256,256 256,0" black_circle.png

# 4. Favicon (Schwarzes Logo im weißen Kreis)
magick convert white_circle.png padded_logo.png -composite "$outDir\favicon.png"
Copy-Item "$outDir\favicon.png" "$outDir\logo.png" -Force

# 5. Dark Mode Favicon (Weißes Logo im schwarzen Kreis)
magick convert black_circle.png padded_logo_white.png -composite "$outDir\favicon-dark.png"

# 6. Apple Touch Icon (Weißes Quadrat als Hintergrund)
magick convert -size 512x512 xc:white padded_logo.png -composite "$outDir\apple-touch-icon.png"

# 7. Andere Größen ableiten
magick convert "$outDir\favicon.png" -resize 96x96 "$outDir\favicon-96x96.png"
magick convert "$outDir\favicon.png" -define icon:auto-resize=64,48,32,16 "$outDir\favicon.ico"

# 8. SVG Format (PNG eingekapselt in SVG)
magick convert "$outDir\favicon.png" "$outDir\favicon.svg"

# Aufräumen von temporären Dateien, aus dem root Verzeichnis
Remove-Item padded_logo.png, padded_logo_white.png, white_circle.png, black_circle.png -ErrorAction SilentlyContinue

Write-Host "Erfolgreich! Alle Bilder liegen nun neu generiert in 'custom_logo\output'." -ForegroundColor Green
