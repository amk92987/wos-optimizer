& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb query --table-name wos-admin-dev --key-condition-expression "PK = :pk" --expression-attribute-values '{\":pk\":{\"S\":\"ERRORS\"}}' --output json
