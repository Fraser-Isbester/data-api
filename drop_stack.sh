STACKNAME=${2:-"data-api"}

aws cloudformation delete-stack \
    --stack-name $STACKNAME
