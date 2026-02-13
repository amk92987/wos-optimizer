@echo off
REM Prepend real Python to PATH before Windows Store stubs
set PATH=C:\Users\adam\AppData\Local\Programs\Python\Python313;C:\Users\adam\AppData\Local\Programs\Python\Python313\Scripts;%PATH%
cd /d C:\Users\adam\IdeaProjects\wos-optimizer
"C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd" build --build-dir infra\.aws-sam\build --template-file infra\template.yaml
