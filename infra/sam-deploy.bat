@echo off
REM Prepend real Python to PATH before Windows Store stubs
set PATH=C:\Users\adam\AppData\Local\Programs\Python\Python313;C:\Users\adam\AppData\Local\Programs\Python\Python313\Scripts;%PATH%
cd /d C:\Users\adam\IdeaProjects\wos-optimizer\infra
"C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd" deploy --template-file .aws-sam\build\template.yaml --stack-name wos-dev --resolve-s3 --s3-prefix wos-dev --region us-east-1 --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND --parameter-overrides Stage=dev --no-confirm-changeset
