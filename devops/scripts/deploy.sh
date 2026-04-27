CLUSTER_NAME="ai-search-engine-cluster"
AWS_REGION="ap-south-1"

echo "Connecting to EKS: $CLUSTER_NAME..."
aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME

echo "Applying Manifests from infrastructure/kubernetes/..."


kubectl apply -f infrastructure/kubernetes/deployment.yaml
kubectl apply -f infrastructure/kubernetes/service.yaml



DEPLOY_NAME=$(kubectl get -f infrastructure/kubernetes/deployment.yaml -o jsonpath='{.metadata.name}')

echo "Rolling out update for deployment: $DEPLOY_NAME..."
kubectl rollout restart deployment/$DEPLOY_NAME

echo "Waiting for status..."
kubectl rollout status deployment/$DEPLOY_NAME

echo "MISSION ACCOMPLISHED!"