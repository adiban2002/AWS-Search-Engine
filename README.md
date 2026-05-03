☁️ AWS-Search-Engine
### Intelligent Cloud Search & RAG using AWS + Gemini 2.0 + Kubernetes
Crawl • Ingest • Vectorize • Generate

Enterprise-Grade AI Search using Gemini 2.0 & Amazon EKS

🚀 Project Overview
AWS-Search-Engine is a high-performance, cloud-native LLMOps platform designed to provide intelligent, context-aware answers from massive enterprise documentation sets.

Built during my Cloud Computing Internship at Codec Technologies, the system leverages a Retrieval-Augmented Generation (RAG) architecture powered by Google Gemini 2.0. It is engineered for industrial scalability, utilizing Amazon EKS for orchestration and Cloudflare Tunnel for zero-trust security.

The system provides:

Contextual AI Responses: Utilizing Gemini 2.0's advanced reasoning.

Semantic Document Retrieval: Meaning-based search via vector embeddings.

Zero Trust Connectivity: Secure backend exposure via Cloudflare.

Global Edge Delivery: Low-latency frontend access via CloudFront.

This project demonstrates an end-to-end integration of Cloud + DevOps + LLMOps, bridging the gap between raw data and actionable AI insights.

🎯 Problem It Solves
In modern industrial and enterprise environments:

Information Silos: Critical technical data is buried in thousands of documents.

Inefficient Search: Traditional keyword searches fail to understand complex technical context.

Security Risks: Exposing internal AI backends to the public internet creates massive vulnerabilities.

This platform automates technical knowledge retrieval using Gemini 2.0 and secure cloud-native scaling.

🧠 Key Capabilities
✔ Gemini 2.0 RAG Pipeline
✔ Semantic Vector Search
✔ Kubernetes Orchestration (EKS)
✔ Zero Trust Security (Cloudflare Tunnel)
✔ Multi-Origin CloudFront Routing
✔ Dockerized Microservices
✔ Asynchronous Ingestion Pipeline
✔ Infrastructure as Code (YAML/EKS)
✔ Automated CI/CD Workflows

☁️ System Architecture
The platform utilizes a multi-layered cloud architecture to ensure high availability and military-grade security.
🖥️ Architecture 1 — Enterprise Backend (EKS)
The FastAPI backend runs as a containerized microservice inside Amazon EKS.
User Request
↓
Cloudflare Tunnel (Secure Bridge)
↓
AWS Load Balancer (ALB)
↓
EKS Cluster (Kubernetes)
↓
FastAPI Pods (Backend)
↓
Gemini 2.0 API (LLM Layer)
↓
Vector Store (Semantic Data)

🌍 Architecture 2 — Edge Delivery (CDN)
Frontend assets are delivered via S3 + CloudFront to ensure worldwide low latency.
User
↓
CloudFront CDN (Global Edge)
↓
S3 Static Hosting (Frontend)
↓
Multi-Origin Routing (/api/*)
↓
Secure Backend (Architecture 1)

🤖 LLMOps Layer
The system implements a sophisticated RAG pipeline using Google Gemini 2.0.

Responsibilities
Document Parsing: Ingesting enterprise PDFs and text files.

Embedding Generation: Converting text into semantic vectors.

Contextual Retrieval: Identifying the most relevant data chunks.

Response Generation: Using Gemini 2.0 for high-fidelity technical answers.

📂 Project Structure
AWS-Search-Engine/
├── backend/                # FastAPI Application & Logic
│   ├── app/                # Core Logic (Routes, Models, Services)
│   │   ├── models/         # Pydantic Schemas
│   │   ├── routes/         # API Endpoints (health, search, upload)
│   │   ├── services/       # Gemini 2.0 RAG Logic
│   │   └── utils/          # Data Preprocessing & Ranking
│   ├── tests/              # Pytest Suite (API, S3, Vector tests)
│   └── requirements.txt    # Backend Dependencies
├── data/                   # Documentation Repository
│   ├── documents/          # Ingested technical files (PDF/TXT)
│   ├── processed/          # Cleaned/Chunked data
│   ├── ingestion_pipeline.py
│   └── s3_loader.py        # S3 Data Ingestion Logic
├── devops/                 # CI/CD Automation
│   ├── ci_cd/              # AWS AppSpec & BuildSpec YAMLs
│   ├── scripts/            # Build & Deployment scripts
│   └── pipeline_architecture.md
├── frontend/               # S3-Hosted UI Layer
│   ├── public/             # index.html
│   └── src/                # JavaScript Logic (api.js, app.js)
├── infrastructure/         # IaC & Orchestration Config
│   ├── aws/                # EKS, ALB, & IAM Policies
│   └── kubernetes/         # Deployment & Service Manifests
├── llmops/                 # Gemini 2.0 RAG Pipeline
│   ├── agents/             # Search Agent Logic
│   ├── embeddings/         # Vector Generation
│   ├── rag/                # Retrieval Pipeline
│   └── vector_db/          # Vector Store Management
├── .env                    # Environment Variables
├── cloudflared.deb         # Cloudflare Tunnel Binary
├── docker-compose.yml      # Local Orchestration Config
├── Dockerfile              # Backend Container Manifest
├── LICENSE                 # Project License
└── README.md               # Project Documentation

🛠️ Technologies Used
Cloud & DevOps
AWS: EKS, S3, CloudFront, ALB, IAM

Containerization: Docker

Security: Cloudflare Tunnel

Orchestration: Kubernetes

AI & Backend
LLM: Google Gemini 2.0

Backend: Python, FastAPI

LLMOps: RAG Pipeline, Semantic Search

👨‍💻 Author
Aditya Banerjee

Final Year B.Tech CSE — Cloud & DevOps Intern at Codec Technologies India

Focused on AWS • DevOps • LLMOps • Cloud Security

⭐ This project demonstrates the future of Industrial AI by combining enterprise-grade cloud security, Kubernetes orchestration, and the reasoning power of Gemini 2.0.