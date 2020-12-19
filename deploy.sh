#!/bin/bash
STAGE=${1:-"Dev"}
STACKNAME=${2:-"data-api"}
S3_BUCKET=${3:-"fraycorp-deployment-artifacts"}
API_LOG_GROUP=${5:-"/aws/apigateway/${STAGE}-${STACKNAME}-Api"}

# Usefuls
CURRENTDATE=`date +"%Y-%m-%dT%T"`

# # Build resources

# Creates your deployment
aws2 s3 mb s3://$S3_BUCKET

# build deploy
sam deploy \
    --stack-name $STACKNAME \
    --s3-bucket $S3_BUCKET \
    --s3-prefix $STACKNAME/$STAGE \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        ParameterKey=Stage,ParameterValue=${STAGE} \
        ParameterKey=Stackname,ParameterValue=${STACKNAME} \
        ParameterKey=S3Bucket,ParameterValue=${S3_BUCKET}