pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "pavan020504/web-service"
        PREDICTION_IMAGE = "pavan020504/prediction-service"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git url: 'https://github.com/Pavanysp/Retina', branch: 'main'
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                echo "Building Docker images"
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
                    echo "Logging in to Docker Hub"
                    echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin

                    echo "Pushing images"
                    docker push ${DOCKER_IMAGE}
                    docker push ${PREDICTION_IMAGE}
                    '''
                }
            }
        }

        stage('Run Docker Compose Playbook') {
            steps {
                sh '''
                echo "Running Docker Compose Playbook"
                ansible-playbook -i hosts.ini deploy.yml
                '''
            }
        }

        stage('Run Kubernetes Minikube Playbook') {
            steps {
                sh '''
                echo "Running Kubernetes Playbook via Ansible"
                ansible-playbook -i hosts.ini k8s-deploy.yml
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline execution complete."
        }
    }
}
