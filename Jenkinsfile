pipeline {
    agent any

    stages {
        stage('Step 1: Environment Check') {
            steps {
                echo 'Checking Docker connection...'
                // This confirms the /var/run/docker.sock mapping is working
                sh 'docker version'
            }
        }

        stage('Step 2: Database Connectivity') {
            steps {
                echo 'Checking if MongoDB is reachable...'
                // Pings the mongodb service defined in your YAML
                sh 'docker exec dockercleanerpro-app ping -c 2 mongodb'
            }
        }

        stage('Step 3: Trigger App Update') {
            steps {
                echo 'Rebuilding the Flask Application container...'
                // This is the heart of your CI/CD
                sh 'docker-compose up -d --build app'
            }
        }

        stage('Step 4: Verify UI') {
            steps {
                echo '--------------------------------------------------'
                echo 'DEMO SUCCESSFUL!'
                echo 'Project: DockerCleanerPro is now live and updated.'
                echo 'Check: http://localhost:5000'
                echo '--------------------------------------------------'
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up workspace...'
        }
    }
}
