$ErrorActionPreference = "Stop"

$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$zipPath = "ffmpeg.zip"
$extractPath = "ffmpeg_temp"
$binPath = "bin"

Write-Host "Creating bin directory..."
if (!(Test-Path -Path $binPath)) {
    New-Item -ItemType Directory -Path $binPath | Out-Null
}

Write-Host "Downloading FFmpeg from $ffmpegUrl..."
Invoke-WebRequest -Uri $ffmpegUrl -OutFile $zipPath

Write-Host "Extracting FFmpeg..."
Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

Write-Host "Locating binaries..."
$ffmpegExe = Get-ChildItem -Path $extractPath -Recurse -Filter "ffmpeg.exe" | Select-Object -First 1
$ffprobeExe = Get-ChildItem -Path $extractPath -Recurse -Filter "ffprobe.exe" | Select-Object -First 1

if ($ffmpegExe -and $ffprobeExe) {
    Write-Host "Moving binaries to $binPath..."
    Move-Item -Path $ffmpegExe.FullName -Destination $binPath -Force
    Move-Item -Path $ffprobeExe.FullName -Destination $binPath -Force
    Write-Host "FFmpeg installed successfully to $binPath"
} else {
    Write-Error "Could not find ffmpeg.exe or ffprobe.exe in the downloaded archive."
}

Write-Host "Cleaning up..."
Remove-Item -Path $zipPath -Force
Remove-Item -Path $extractPath -Recurse -Force

Write-Host "Done."
