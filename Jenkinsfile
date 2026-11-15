
pipeline {
    agent any

    options { 
        skipDefaultCheckout(true)
        timestamps()
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Recuperation du projet depuis GitHub'
                checkout scm
            }
        }

        stage('Verification des fichiers') {
            steps {
                echo 'Verification de la structure du projet'

                bat '''
                    if not exist app.py exit /b 1
                    if not exist requirements.txt exit /b 1
                    if not exist README.md exit /b 1

                    echo Tous les fichiers necessaires sont presents.
                '''
            }
        }
    }

    post {
        success {
            echo 'BIWEX STORE : Pipeline execute avec succes.'
        }

        failure {
            echo 'BIWEX STORE : Le pipeline a echoue.'
        }
    }
}
