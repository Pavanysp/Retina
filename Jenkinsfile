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
                sudo docker build -t ${DOCKER_IMAGE} .
                cd ../prediction-service
                sudo docker build -t ${PREDICTION_IMAGE} .
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
                    echo "${DOCKER_PASS}" | sudo docker login -u "${DOCKER_USER}" --password-stdin

                    echo "Pushing images"
                    sudo docker push ${DOCKER_IMAGE}
                    sudo docker push ${PREDICTION_IMAGE}
                    '''
                }
            }
        }

        stage('Run Docker Compose') {
            steps {
                sh '''
                echo "Running docker-compose"
                sudo docker-compose down || true
                sudo docker-compose up -d
                '''
            }
        }

        stage('Start Minikube') {
            steps {
                sh '''
                echo "Starting Minikube"
                minikube start --driver=docker --wait=none || true
                '''
            }
        }

        stage('Apply Kubernetes Configs') {
            steps {
                sh '''
                echo "Setting KUBECONFIG for kubectl"
                export KUBECONFIG=$(minikube kubeconfig)

                echo "Verifying kubectl connection"
                kubectl get nodes

                echo "Applying Kubernetes manifests"
                kubectl apply -f k8s/ --validate=false
                '''
            }
        }

        stage('Expose via DNS') {
            steps {
                echo 'Make sure minikube tunnel is running: run `minikube tunnel` in background'
                echo 'Then access your app at: https://retina.local'
            }
        }
    }
}
