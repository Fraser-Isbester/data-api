#!/bin/bash
STAGE=${1:-"Dev"}
STACKNAME=${2:-"data-api"}
S3_BUCKET=${3:-"fraycorp-deployment-artifacts"}
API_LOG_GROUP=${4:-"/aws/apigateway/${STAGE}-${STACKNAME}-Api"}
SWAGGER_FILEPATH=${5:-"/Users/fraser/Documents/Dev/personal/data-api/api.yaml"}

# Useful variables
BUILD_ID=`uuidgen`

# # Build resources
SWAGGER_LOCATION="s3://$S3_BUCKET/$STACKNAME/$STAGE/$BUILD_ID/swagger.yaml"
aws2 s3 mb s3://$S3_BUCKET
aws2 s3 cp "$SWAGGER_FILEPATH" "$SWAGGER_LOCATION"

# build deploy
sam deploy \
    --stack-name $STACKNAME \
    --s3-bucket $S3_BUCKET \
    --s3-prefix $STACKNAME/$STAGE/$BUILD_ID \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        ParameterKey=Stage,ParameterValue=${STAGE} \
        ParameterKey=Stackname,ParameterValue=${STACKNAME} \
        ParameterKey=S3Bucket,ParameterValue=${S3_BUCKET} \
        ParameterKey=SwaggerFile,ParameterValue=${SWAGGER_LOCATION}
