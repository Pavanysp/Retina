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
                withCredentials([usernamePassword(credentialsId: '1cb7dcef-4311-43a3-a0c6-e1bee0229828',
                                                  usernameVariable: 'DOCKER_USER',
                                                  passwordVariable: 'DOCKER_PASS')]) {
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

        stage('Run Ansible Playbook') {
            steps {
                sh '''
                echo "Running Ansible Playbook using existing files"
                ansible-playbook -i hosts.ini deploy.yml
                '''
            }
        }

        stage('Start Minikube') {
            steps {
                sh '''
                echo "Starting Minikube locally without SSH or VM"
                minikube delete || true
                minikube start --wait=none
                '''
            }
        }

        stage('Apply Kubernetes Configs') {
            steps {
                sh '''
                echo "Applying Kubernetes manifests"
                kubectl apply -f k8s/ --validate=false
                '''
            }
        }

        stage('Expose via DNS') {
            steps {
                echo 'Ensure minikube tunnel is running: open a terminal and run `minikube tunnel`'
                echo 'Then visit your app at: https://retina.local'
            }
        }
    }
}
