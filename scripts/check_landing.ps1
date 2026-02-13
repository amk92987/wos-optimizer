$resp = Invoke-WebRequest -Uri 'https://wosdev.randomchaoslabs.com/landing' -UseBasicParsing
$content = $resp.Content

if ($content -match 'animate-spin') { Write-Host "HAS SPINNER (home page)" } else { Write-Host "NO SPINNER" }
if ($content -match 'Stop Guessing') { Write-Host "HAS LANDING CONTENT" } else { Write-Host "NO LANDING CONTENT" }
if ($content -match 'backgroundAttachment') { Write-Host "HAS BG-FIXED (inline)" } else { Write-Host "NO BG-FIXED inline" }
if ($content -match 'bg-gradient-landing') { Write-Host "HAS bg-gradient-landing class" } else { Write-Host "NO bg-gradient-landing class" }

Write-Host "`nContent length: $($content.Length)"
