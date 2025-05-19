pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "pavan020504/web-service"
        PREDICTION_IMAGE = "pavan020504/prediction-service"
        MINIKUBE_HOME = "${env.WORKSPACE}/.minikube"
        CHANGE_MINIKUBE_NONE_USER = "true"
        KUBECONFIG = "${env.WORKSPACE}/.kube/config"
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

        stage('Run Ansible Playbook') {
            steps {
                sh '''
                echo "Running Ansible Playbook"
                ansible-playbook -i hosts.ini deploy.yml
                '''
            }
        }

        stage('Start Minikube') {
            steps {
                sh '''
                echo "Starting Minikube using Docker driver (no SSH)"
                
                minikube delete || true

                mkdir -p $MINIKUBE_HOME
                mkdir -p $(dirname $KUBECONFIG)

                minikube start --driver=docker \
                    --wait=none \
                    --force \
                    --install-addons=true \
                    --delete-on-failure

                echo "Minikube started successfully"
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
                echo 'To expose services via DNS, run `minikube tunnel` in  a separate terminal.'
                echo 'After that, access the app at: https://retinopathy.local'
            }
        }
    }

    post {
        always {
            echo "Pipeline execution complete."
        }
    }
}
