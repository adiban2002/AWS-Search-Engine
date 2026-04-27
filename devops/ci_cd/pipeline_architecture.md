# CI/CD Pipeline Architecture for AI-Powered Cloud Search Engine

## 1. Overview
This document outlines the automated CI/CD workflow for deploying the search engine backend to AWS EKS.

## 2. Pipeline Stages

### Stage 1: Source (GitHub)
- **Trigger**: Any push to the `main` branch.
- **Action**: AWS CodePipeline fetches the latest source code.

### Stage 2: Build (AWS CodeBuild)
- **Environment**: Ubuntu-based Docker container.
- **Process**:
    - Login to Amazon ECR.
    - Build Docker image from `Dockerfile`.
    - Tag image with Git Commit ID and `latest`.
    - Push image to ECR Repository: `800557028391.dkr.ecr.ap-south-1.amazonaws.com/ai-search-backend`.
- **Output**: `imagedefinitions.json` for deployment.

### Stage 3: Deploy (AWS CodeDeploy/Kubectl)
- **Target**: AWS EKS Cluster (`ai-search-engine-cluster`).
- **Action**: 
    - Update `deployment.yaml` with the new image tag.
    - Apply Kubernetes manifests.
    - Rolling update of pods.

## 3. Security & IAM
- **CodeBuild Role**: Must have `ECR:Push` and `EKS:DescribeCluster` permissions.
- **Secrets**: OpenSearch credentials and Gemini API Key are managed via K8s Secrets/Env vars.