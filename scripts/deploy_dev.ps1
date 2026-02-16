param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

$rootDir = "C:\Users\adam\IdeaProjects\wos-optimizer"
$samCli = "C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd"
$awsCli = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$pythonDir = "C:\Users\adam\AppData\Local\Programs\Python\Python313"

# Ensure Python is on PATH for SAM
$env:PATH = "$pythonDir;$pythonDir\Scripts;$env:PATH"

if (-not $FrontendOnly) {
    Write-Host "=== Building Backend (SAM) ===" -ForegroundColor Cyan
    Set-Location "$rootDir\infra"
    & $samCli build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "SAM build failed!" -ForegroundColor Red
        exit 1
    }

    Write-Host "`n=== Deploying Backend (SAM) ===" -ForegroundColor Cyan
    & $samCli deploy --no-confirm-changeset
    if ($LASTEXITCODE -ne 0) {
        Write-Host "SAM deploy failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "Backend deployed successfully!" -ForegroundColor Green
}

if (-not $BackendOnly) {
    Write-Host "`n=== Syncing Frontend to S3 ===" -ForegroundColor Cyan
    & $awsCli s3 sync "$rootDir\frontend\out" "s3://wos-frontend-dev-561893854848" --delete --no-progress
    if ($LASTEXITCODE -ne 0) {
        Write-Host "S3 sync failed!" -ForegroundColor Red
        exit 1
    }

    Write-Host "`n=== Invalidating CloudFront ===" -ForegroundColor Cyan
    & $awsCli cloudfront create-invalidation --distribution-id EWE2LGBUHCEI1 --paths "/*"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "CloudFront invalidation failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "Frontend deployed successfully!" -ForegroundColor Green
}

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
