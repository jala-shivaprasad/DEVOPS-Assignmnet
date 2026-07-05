# 🚀 Deployment Guide

This document describes the complete deployment process for the **DevOps Assignment** project on **AWS EC2** using **Docker, Jenkins, Docker Hub, GitHub Webhook, and Amazon CloudWatch**.

---

# 📋 Prerequisites

Before deployment, ensure the following resources are available:

- AWS Free Tier Account
- Ubuntu EC2 Instance
- GitHub Repository
- Docker Hub Account
- Jenkins Installed
- Docker Installed
- IAM Role with Least Privilege
- Amazon S3 Bucket
- CloudWatch Dashboard & Alarm

---

# 🏗️ Step 1: Launch AWS EC2 Instance

1. Launch an Ubuntu EC2 instance.
2. Attach an IAM Role with least-privilege permissions.
3. Configure the Security Group.

### Inbound Rules

| Port | Service |
|------|----------|
| 22 | SSH |
| 80 | HTTP (Optional) |
| 5000 | Flask Application |
| 8080 | Jenkins |

---

# 🔐 Step 2: Connect to EC2

```bash
ssh -i your-key.pem ubuntu@<EC2-Public-IP>
```

---

# 🐳 Step 3: Install Docker

```bash
sudo apt update

sudo apt install docker.io -y

sudo systemctl enable docker

sudo systemctl start docker

sudo usermod -aG docker ubuntu
```

Verify Docker:

```bash
docker --version
```

---

# ☕ Step 4: Install Jenkins

Install Java

```bash
sudo apt install openjdk-21-jdk -y
```

Install Jenkins

```bash
sudo systemctl enable jenkins

sudo systemctl start jenkins
```

Access Jenkins:

```
http://<EC2-Public-IP>:8080
```

---

# 📂 Step 5: Clone GitHub Repository

```bash
git clone https://github.com/jala-shivaprasad/DEVOPS-Assignmnet.git

cd DEVOPS-Assignmnet
```

---

# 🐳 Step 6: Build Docker Image

```bash
docker build -t devops-app .
```

---

# ▶️ Step 7: Run Docker Container

```bash
docker run -d \
--name devops-app \
-p 5000:5000 \
devops-app
```

Verify Container:

```bash
docker ps
```

---

# 🔄 Step 8: Configure Jenkins CI/CD

The Jenkins Pipeline performs the following tasks automatically:

- Checkout source code from GitHub
- Build Docker Image
- Login to Docker Hub
- Push Docker Image
- Pull Latest Image
- Stop Previous Container
- Deploy New Container
- Verify Deployment

---

# 🔗 Step 9: Configure GitHub Webhook

Repository Settings

```
Settings
→ Webhooks
→ Add Webhook
```

Payload URL

```
http://<EC2-Public-IP>:8080/github-webhook/
```

Content Type

```
application/json
```

Events

```
Just the push event
```

Now every Git push automatically triggers Jenkins.

---

# 🐋 Step 10: Docker Hub Integration

The pipeline automatically:

- Builds Docker Image
- Pushes Image to Docker Hub
- Pulls Latest Image
- Deploys Updated Container

---

# ☁️ Step 11: Configure Amazon CloudWatch

Monitoring includes:

- CPU Utilization
- Network In
- Network Out
- Status Check
- CPU Alarm (70%)

---

# 📦 Step 12: Amazon S3

Amazon S3 is used for storing:

- Application Backups
- Static Files
- Deployment Artifacts

---

# ⚡ Step 13: Load Testing

Execute the following command:

```bash
k6 run test.js
```

Collected Metrics:

- Response Time
- Throughput
- CPU Utilization
- Error Rate
- Latency

---

# 🌐 Step 14: Verify Deployment

Open the application in your browser:

```
http://<EC2-Public-IP>:5000
```

Expected Output

```
DevOps Assignment

Application Successfully Deployed

AWS EC2 + Docker + Jenkins
```

---

# 📊 Deployment Workflow

```
Developer
     │
Git Push
     │
GitHub Repository
     │
GitHub Webhook
     │
Jenkins Pipeline
     │
Docker Build
     │
Docker Hub
     │
AWS EC2
     │
Docker Container
     │
Flask Application
     │
CloudWatch Monitoring
```

---

# ✅ Deployment Status

| Component | Status |
|-----------|--------|
| AWS EC2 | ✅ Completed |
| Docker | ✅ Completed |
| Jenkins | ✅ Completed |
| GitHub Webhook | ✅ Completed |
| Docker Hub | ✅ Completed |
| CloudWatch | ✅ Completed |
| Amazon S3 | ✅ Completed |
| Load Testing | ✅ Completed |

---

# 🎯 Conclusion

The application was successfully deployed on **AWS EC2** using **Docker** with a fully automated **Jenkins CI/CD Pipeline**. GitHub Webhooks trigger automatic deployments, Docker Hub stores container images, Amazon CloudWatch provides monitoring and alerts, Amazon S3 is used for storage, and k6 validates application performance under load.
