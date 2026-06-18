# Run logo generation in a Docker container using ImageMagick
$workDir = (Get-Item .).FullName
Write-Host "Starting Logo Generation via Docker..." -ForegroundColor Cyan

docker run --rm -v "${workDir}:/work" -w /work alpine sh -c "
  apk add --no-cache imagemagick librsvg ttf-dejavu potrace
  mkdir -p output
  echo 'Generating padded logo...'
  magick convert -background none source_logo.svg -resize 350x350 -gravity center -extent 512x512 padded_logo.png
  echo 'Generating dark mode inverted logo...'
  magick convert padded_logo.png -channel RGB -negate padded_logo_white.png
  echo 'Generating circle backgrounds...'
  magick convert -size 512x512 xc:none -fill white -draw 'circle 256,256 256,0' white_circle.png
  magick convert -size 512x512 xc:none -fill black -draw 'circle 256,256 256,0' black_circle.png
  echo 'Compositing favicons...'
  magick convert white_circle.png padded_logo.png -composite output/favicon.png
  cp output/favicon.png output/logo.png
  magick convert black_circle.png padded_logo_white.png -composite output/favicon-dark.png
  echo 'Generating apple-touch-icon...'
  magick convert -size 512x512 xc:white padded_logo.png -composite output/apple-touch-icon.png
  echo 'Resizing and packaging...'
  magick convert output/favicon.png -resize 96x96 output/favicon-96x96.png
  magick convert output/favicon.png -define icon:auto-resize=64,48,32,16 output/favicon.ico
  magick convert output/favicon.png output/favicon.svg
  echo 'Cleaning up temporary files...'
  rm -f padded_logo.png padded_logo_white.png white_circle.png black_circle.png
"

Write-Host "Docker generation complete!" -ForegroundColor Green
