pipeline {
    agent any

    environment {
        // Using the credentials ID for GitHub authentication
        GIT_CREDENTIALS = credentials('bd9bd0e3-6d95-49c7-8dc2-077de0cc7e72') // GitHub token credentials
        DOCKER_IMAGE = 'pavan020504/web-service' // Web service image name
        PREDICTION_IMAGE = 'pavan020504/prediction-service' // Prediction service image name
    }

    stages {
        stage('Checkout') {
            steps {
                // Cloning the repository from GitHub using the stored credentials
                git url: 'https://github.com/Pavanysp/Retina.git', credentialsId: 'bd9bd0e3-6d95-49c7-8dc2-077de0cc7e72'
            }
        }

        stage('Build Docker Images') {
            steps {
                // Building Docker images for both services
                script {
                    echo "Building Docker images..."
                    sh 'docker build -t ${DOCKER_IMAGE} ./web-service'
                    sh 'docker build -t ${PREDICTION_IMAGE} ./prediction-service'
                }
            }
        }

        stage('Docker Compose Up') {
            steps {
                // Running docker-compose to start the services
                script {
                    echo "Starting services using Docker Compose..."
                    sh 'docker-compose -f docker-compose.yml up -d'
                }
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
                    sudo docker push ${DOCKER_IMAGE}
                    sudo docker push ${PREDICTION_IMAGE}
                    '''
                }
            }
        }

        stage('Start Minikube and Apply Kubernetes Resources') {
            steps {
                script {
                    // Starting Minikube if not already started
                    echo "Starting Minikube..."
                    sh 'minikube start --driver=docker'

                    // Applying Kubernetes resources (deployment, service, etc.)
                    echo "Applying Kubernetes resources..."
                    sh 'kubectl apply -f kubernetes/'
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // Deploying the services to Kubernetes using the latest Docker images
                    echo "Deploying to Kubernetes..."
                    sh 'kubectl set image deployment/web-service web-service=${DOCKER_IMAGE}'
                    sh 'kubectl set image deployment/prediction-service prediction-service=${PREDICTION_IMAGE}'
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    // Verifying the deployment on Kubernetes
                    echo "Verifying the Kubernetes deployments..."
                    sh 'kubectl get pods'
                    sh 'kubectl get services'
                }
            }
        }
    }

    post {
        always {
            // Clean up Docker containers and volumes after pipeline runs
            echo "Cleaning up Docker containers..."
            sh 'docker-compose down'
            sh 'docker system prune -af'
        }
    }
}

