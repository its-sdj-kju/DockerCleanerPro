pipeline {
    agent any

    stages {
        stage('Step 1: Environment Check') {
            steps {
                echo 'Verifying Docker Access...'
                sh 'docker version'
            }
        }

        stage('Step 2: Build Image') {
            steps {
                echo 'Building the Docker Cleaner App image...'
                sh 'docker build -t dockercleanerpro-app .'
            }
        }

        stage('Step 3: Deploy/Restart App') {
            steps {
                echo 'Stopping and removing old container...'
                sh 'docker stop dockercleanerpro-app || true'
                sh 'docker rm dockercleanerpro-app || true'
                
                echo 'Starting the new container with Root privileges...'
                sh '''
                docker run -d \
                --name dockercleanerpro-app \
                --user root \
                --network dockercleanerpro_default \
                -v /var/run/docker.sock:/var/run/docker.sock \
                -p 5000:5000 \
                --restart always \
                dockercleanerpro-app
                '''
            }
        }

        stage('Step 4: Docker Cleanup') {
            steps {
                echo 'Cleaning up old dangling images...'
                sh 'docker image prune -f'
            }
        }
    }
    
    post {
        success {
            echo 'SUCCESS: Deployment Complete!'
        }
    }
}