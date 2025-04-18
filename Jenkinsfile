pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = '1cb7dcef-4311-43a3-a0c6-e1bee0229828'
        WEB_IMAGE = 'pavan020504/web-service'
        PREDICTION_IMAGE = 'pavan020504/prediction-service'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/Pavanysp/Retina.git'
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                docker build -t $WEB_IMAGE ./web-service
                docker build -t $PREDICTION_IMAGE ./prediction-service
                '''
            }
        }

        stage('Push Docker Images') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKERHUB_CREDENTIALS}",
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                    docker push $WEB_IMAGE
                    docker push $PREDICTION_IMAGE
                    '''
                }
            }
        }

        stage('Run Docker Compose (Optional Test)') {
            steps {
                sh '''
                docker-compose -f docker-compose.yaml up -d
                sleep 10
                docker-compose ps
                docker-compose down
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                minikube start || true  # Start Minikube if not already running
                kubectl apply -f k8s/web-deployment.yaml
                kubectl apply -f k8s/prediction-deployment.yaml
                kubectl apply -f k8s/web-service.yaml
                kubectl apply -f k8s/prediction-service.yaml
                kubectl apply -f k8s/web-ingress.yaml
                '''
            }
        }
    }
}

