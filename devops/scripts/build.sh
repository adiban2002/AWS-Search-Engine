AWS_REGION="ap-south-1"
AWS_ACCOUNT_ID="800557028391"
REPO_NAME="ai-search-backend"
IMAGE_TAG="latest"
echo " Starting Docker Build for Codec Technologies Project..."


aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
echo " Building image: $REPO_NAME..."
docker build -t $REPO_NAME .


echo " Tagging image..."
docker tag $REPO_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG

echo " Pushing image to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG
echo " Pushing image to ECR..."

echo "Success! Image is now in ECR: $REPO_NAME"