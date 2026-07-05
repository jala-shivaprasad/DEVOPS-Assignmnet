* Deployment Guide *
1. Launch EC2 Instance
Launch an Ubuntu EC2 instance (Free Tier).
Configure the Security Group to allow ports 22, 80, 5000, and 8080.
Attach an IAM Role with least-privilege permissions.
2. Install Docker
sudo apt update
sudo apt install docker.io -y
sudo systemctl enable docker
sudo systemctl start docker
3. Install Jenkins
sudo apt install openjdk-21-jdk -y

Install Jenkins and start the service.

4. Clone Repository
git clone https://github.com/jala-shivaprasad/DEVOPS-Assignmnet.git

cd DEVOPS-Assignmnet
5. Build Docker Image
docker build -t devops-app .
6. Run Container
docker run -d --name devops-app -p 5000:5000 devops-app
7. Configure Jenkins
Create a Pipeline Job.
Connect the GitHub repository.
Configure GitHub Webhook.
Add Docker Hub credentials.
Build automatically after every GitHub push.
8. Configure CloudWatch
Create Dashboard.
Create CPU Alarm.
Monitor EC2 metrics.
9. Perform Load Testing
k6 run test.js
10. Verify

Open:

http://<EC2-Public-IP>:5000

Application should display:

DevOps Assignment

Application Successfully Deployed
