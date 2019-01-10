pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building..'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
    }
    post {
        success {
            script {
                echo ${env.CHANGE_ID}
            }
        }
    }
}
