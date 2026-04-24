apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: ai-search-engine-cluster
  region: ap-south-1
  version: "1.33"  # Latest and Greatest

iam:
  withOIDC: true # OIDC and IRSA for S3/OpenSearch connectivity

vpc:
  clusterEndpoints:
    publicAccess: true
    privateAccess: true

managedNodeGroups:
  - name: search-engine-nodes-v1-33
    instanceType: t3.medium
    minSize: 1
    maxSize: 4
    desiredCapacity: 2
    volumeSize: 30 # For Docker images and local cache
    amiFamily: AmazonLinux2023 # Modern OS for K8s 1.33
    iam:
      withAddonPolicies:
        imageBuilder: true
        autoScaler: true
        cloudWatch: true
        albIngress: true
        ebs: true # Persistent volumes এর জন্য দরকার


iamServiceAccounts:
  - metadata:
      name: ai-search-sa
      namespace: default
    attachPolicyARNs:
      - "arn:aws:iam::800557028391:policy/LLMOpsRuntimePolicy" 