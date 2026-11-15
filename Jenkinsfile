
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        DOCKER = 'C:\\Users\\Famory Toure\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        IMAGE_NAME = 'biwex-store'
        CONTAINER_NAME = 'biwex-store-jenkins-test'
        SMOKE_STATUS = 'NOT_RUN'
    }

    stages {

        stage('1 - Checkout') {
            steps {
                echo 'Recuperation du projet depuis GitHub'
                checkout scm
            }
        }

        stage('2 - Setup') {
            steps {
                echo 'Verification de l environnement'
                bat '''
                    if not exist app.py exit /b 1
                    if not exist requirements.txt exit /b 1
                    if not exist scripts\\smoke_test.py exit /b 1
                    if not exist artifacts mkdir artifacts
                    "%DOCKER%" version
                '''
            }
        }

        stage('3 - Build Docker') {
            steps {
                echo 'Construction de l image Docker'
                bat '''
                    "%DOCKER%" build -t "%IMAGE_NAME%:dev-%BUILD_NUMBER%" . > artifacts\\docker-build.log 2>&1
                    set "BUILD_EXIT=%ERRORLEVEL%"
                    type artifacts\\docker-build.log
                    exit /b %BUILD_EXIT%
                '''
            }
        }

        stage('4 - Run Docker') {
            steps {
                echo 'Demarrage du conteneur de test'
                bat '''
                    "%DOCKER%" rm -f "%CONTAINER_NAME%" 2>NUL
                    "%DOCKER%" run -d --name "%CONTAINER_NAME%" -e SECRET_KEY=jenkins-ci-test-secret "%IMAGE_NAME%:dev-%BUILD_NUMBER%"
                    if errorlevel 1 exit /b 1
                '''
            }
        }


        stage('5 - Smoke Test') {
            steps {
                echo 'Verification HTTP avec plusieurs tentatives'

                script {
                    try {
                        bat '''
                            for /L %%i in (1,1,15) do (
                                echo Tentative %%i sur 15

                                "%DOCKER%" exec "%CONTAINER_NAME%" python /app/scripts/smoke_test.py http://127.0.0.1:5000/ > artifacts\\smoke-test.txt 2>&1

                                if not errorlevel 1 goto smoke_passed

                                timeout /t 2 /nobreak >NUL
                            )

                            type artifacts\\smoke-test.txt
                            exit /b 1

                            :smoke_passed
                            type artifacts\\smoke-test.txt
                            exit /b 0
                        '''

                        writeFile file: 'artifacts/smoke-status.txt', text: 'PASSED'
                    } catch (err) {
                        writeFile file: 'artifacts/smoke-status.txt', text: 'FAILED'
                        throw err
                    }
                }
            }
        }




        stage('6 - Archive Artifacts') {
            steps {
                echo 'Generation du rapport et archivage'

                script {
                    def smokeResult = readFile('artifacts/smoke-status.txt').trim()

                    writeFile file: 'artifacts/pipeline-report.txt',
                        text: """Pipeline: Biwex-Store-Pipeline
Build: ${env.BUILD_NUMBER}
Branch: dev
Image: ${env.IMAGE_NAME}:dev-${env.BUILD_NUMBER}
Smoke Test: ${smokeResult}
Result: ${currentBuild.currentResult}
"""
                }

                archiveArtifacts artifacts: 'artifacts/**', fingerprint: true
            }
        }


    post {
        always {
            echo 'Nettoyage du conteneur de test'

            bat '''
                "%DOCKER%" rm -f "%CONTAINER_NAME%" 2>NUL
                exit /b 0
            '''
        }

        success {
            echo 'BIWEX STORE : Pipeline execute avec succes.'
        }

        failure {
            echo 'BIWEX STORE : Le pipeline a echoue.'
        }
    }
}
