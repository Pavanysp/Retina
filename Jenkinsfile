pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "pavan020504/web-service"
        PREDICTION_IMAGE = "pavan020504/prediction-service"
        WORKSPACE_DIR = "/var/lib/jenkins/workspace/retina"
        
    }

    stages {
        stage('Clone Repository') {
            steps {
                deleteDir()
                git url: 'https://github.com/Pavanysp/Retina', branch: 'main'
            }
        }

        stage('Fix Jenkins Docker & Minikube Permissions') {
            steps {
                sh '''
                echo "Fixing Jenkins user permissions..."

                # Add Jenkins to docker group
                sudo usermod -aG docker jenkins

                # Create required directories for minikube & kube if not present
                sudo mkdir -p $WORKSPACE_DIR/.kube
                sudo mkdir -p $WORKSPACE_DIR/.minikube

                # Set ownership and permissions
                sudo chown -R jenkins:docker $WORKSPACE_DIR/.kube
                sudo chown -R jenkins:docker $WORKSPACE_DIR/.minikube

                sudo chmod -R u+wrx $WORKSPACE_DIR/.kube
                sudo chmod -R u+wrx $WORKSPACE_DIR/.minikube
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                echo "Building Docker images..."
                cd web-service
                docker build -t ${DOCKER_IMAGE} .
                cd ../prediction-service
                docker build -t ${PREDICTION_IMAGE} .
                '''
            }
        }

        stage('Push Docker Images to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: '1cb7dcef-4311-43a3-a0c6-e1bee0229828',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo "Logging in to Docker Hub..."
                    echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin

                    echo "Pushing Docker images to Docker Hub..."
                    docker push ${DOCKER_IMAGE}
                    docker push ${PREDICTION_IMAGE}
                    '''
                }
            }
        }

        stage('Run Docker Compose Playbook') {
            steps {
                sh '''
                echo "Running Docker Compose Ansible Playbook"
                ansible-playbook -i hosts.ini deploy.yml
                '''
            }
        }

        stage('Run Kubernetes Minikube Playbook') {
            steps {
                sh '''
                echo "Running Kubernetes Minikube Ansible Playbook"
                ansible-playbook -i hosts.ini k8s-deploy.yml
                '''
            }
        }
    }

    post {
        always {
            echo "✅ Pipeline execution is completed."
        }
    }
}
