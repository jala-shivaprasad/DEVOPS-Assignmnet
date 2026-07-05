pipeline {
    agent any

    environment {
        IMAGE_NAME = "YOUR_DOCKERHUB_USERNAME/devops-assignment"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
            }
        }

        stage('Push Image') {
            steps {
                sh "docker push ${IMAGE_NAME}:latest"
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                docker stop devops-app || true
                docker rm devops-app || true

                docker pull ${IMAGE_NAME}:latest

                docker run -d \
                    --name devops-app \
                    -p 5000:5000 \
                    ${IMAGE_NAME}:latest
                '''
            }
        }

        stage('Verify') {
            steps {
                sh 'docker ps'
            }
        }
    }

    post {
        success {
            echo 'Deployment Successful!'
        }
        failure {
            echo 'Pipeline Failed!'
        }
    }
}
