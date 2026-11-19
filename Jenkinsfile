// ============================================================
//  PIPELINE 2 : BUILD COMPLET SUR PUSH (branche dev)
//  Déclencheur : push sur "dev" ou déclenchement manuel
//  Objectif    : Build multi-version parallèle (Python 3.11 & 3.12),
//                exécution conteneurisée, smoke test et archivage
// ============================================================

pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        // Chemin absolu Docker Desktop (Windows)
        DOCKER_BIN     = 'C:\\Users\\Famory Toure\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        IMAGE_BASE     = 'biwex-store'
        CONTAINER_NAME = "biwex-dev-test-${BUILD_NUMBER}"
        SMOKE_STATUS   = 'NOT_RUN'
    }

    stages {

        // ══════════════════════════════════════════════════════
        // STAGE 1 - CHECKOUT
        // ══════════════════════════════════════════════════════
        stage('1 - Checkout') {
            steps {
                echo '=== STAGE 1 : Récupération du code source (dev) ==='
                checkout scm
                script {
                    echo "Branche active : ${env.BRANCH_NAME ?: 'dev'}"
                    echo "Build Jenkins   : #${env.BUILD_NUMBER}"
                }
            }
        }

        // ══════════════════════════════════════════════════════
        // STAGE 2 - SETUP
        // ══════════════════════════════════════════════════════
        stage('2 - Setup') {
            steps {
                echo '=== STAGE 2 : Vérification de l environnement et des prérequis ==='
                bat '''
                    @echo off
                    echo [Setup] Verification de l arborescence du projet...

                    if not exist app.py (
                        echo ERREUR : app.py manquant !
                        exit /b 1
                    )
                    if not exist requirements.txt (
                        echo ERREUR : requirements.txt manquant !
                        exit /b 1
                    )
                    if not exist Dockerfile (
                        echo ERREUR : Dockerfile manquant !
                        exit /b 1
                    )
                    if not exist scripts\\smoke_test.py (
                        echo ERREUR : scripts\\smoke_test.py manquant !
                        exit /b 1
                    )

                    if not exist artifacts mkdir artifacts
                    echo [Setup] Fichiers requis presents. OK.
                    echo.

                    echo [Setup] Verification de Docker...
                    if exist "%DOCKER_BIN%" (
                        "%DOCKER_BIN%" version
                    ) else (
                        docker version
                    )
                '''
            }
        }

        // ══════════════════════════════════════════════════════
        // STAGE 3 - BUILD PARALLÈLE (Python 3.11 & Python 3.12)
        // ══════════════════════════════════════════════════════
        stage('3 - Build Docker (Parallèle)') {
            parallel {

                stage('Build Python 3.11 (LTS)') {
                    steps {
                        echo '=== Construction image Docker - Python 3.11 ==='
                        bat '''
                            @echo off
                            set "DOCKER_CMD=%DOCKER_BIN%"
                            if not exist "%DOCKER_CMD%" set "DOCKER_CMD=docker"

                            "%DOCKER_CMD%" build ^
                                --build-arg PYTHON_VERSION=3.11 ^
                                -t %IMAGE_BASE%:dev-%BUILD_NUMBER%-py311 ^
                                . > artifacts\\docker-build-py311.log 2>&1

                            set "BUILD_EXIT=%ERRORLEVEL%"
                            type artifacts\\docker-build-py311.log
                            exit /b %BUILD_EXIT%
                        '''
                    }
                }

                stage('Build Python 3.12 (Compatibilité)') {
                    steps {
                        echo '=== Construction image Docker - Python 3.12 ==='
                        bat '''
                            @echo off
                            set "DOCKER_CMD=%DOCKER_BIN%"
                            if not exist "%DOCKER_CMD%" set "DOCKER_CMD=docker"

                            "%DOCKER_CMD%" build ^
                                --build-arg PYTHON_VERSION=3.12 ^
                                -t %IMAGE_BASE%:dev-%BUILD_NUMBER%-py312 ^
                                . > artifacts\\docker-build-py312.log 2>&1

                            set "BUILD_EXIT=%ERRORLEVEL%"
                            type artifacts\\docker-build-py312.log
                            exit /b %BUILD_EXIT%
                        '''
                    }
                }
            }
        }

        // ══════════════════════════════════════════════════════
        // STAGE 4 - RUN DOCKER
        // ══════════════════════════════════════════════════════
        stage('4 - Run Docker') {
            steps {
                echo '=== STAGE 4 : Démarrage du conteneur de test ==='
                bat '''
                    @echo off
                    set "DOCKER_CMD=%DOCKER_BIN%"
                    if not exist "%DOCKER_CMD%" set "DOCKER_CMD=docker"

                    echo [Run] Arret de tout ancien conteneur residuel...
                    "%DOCKER_CMD%" rm -f %CONTAINER_NAME% 2>NUL

                    echo [Run] Lancement du conteneur %CONTAINER_NAME%...
                    "%DOCKER_CMD%" run -d ^
                        --name %CONTAINER_NAME% ^
                        -e SECRET_KEY=jenkins-dev-secret-key ^
                        %IMAGE_BASE%:dev-%BUILD_NUMBER%-py311

                    if errorlevel 1 (
                        echo ERREUR : Echec du lancement du conteneur.
                        exit /b 1
                    )

                    echo [Run] Conteneur demarre avec succes.
                    "%DOCKER_CMD%" ps --filter name=%CONTAINER_NAME%
                '''
                // Pause sécurisée pour laisser le temps à Gunicorn de démarrer
                sleep(time: 5, unit: 'SECONDS')
            }
        }

        // ══════════════════════════════════════════════════════
        // STAGE 5 - SMOKE TEST
        // ══════════════════════════════════════════════════════
        stage('5 - Smoke Test') {
            steps {
                echo '=== STAGE 5 : Smoke Test HTTP (Validation rapide) ==='
                script {
                    try {
                        // 15 tentatives espacées de 2 secondes
                        retry(15) {
                            sleep(time: 2, unit: 'SECONDS')
                            bat '''
                                @echo off
                                set "DOCKER_CMD=%DOCKER_BIN%"
                                if not exist "%DOCKER_CMD%" set "DOCKER_CMD=docker"

                                "%DOCKER_CMD%" exec %CONTAINER_NAME% python /app/scripts/smoke_test.py http://127.0.0.1:5000/ > artifacts\\smoke-test.txt 2>&1
                                type artifacts\\smoke-test.txt
                            '''
                        }

                        env.SMOKE_STATUS = 'PASSED'
                        writeFile(file: 'artifacts/smoke-status.txt', text: 'PASSED')
                        echo '=== SMOKE TEST : PASSED ==='

                    } catch (err) {
                        env.SMOKE_STATUS = 'FAILED'
                        writeFile(file: 'artifacts/smoke-status.txt', text: 'FAILED')
                        echo '=== SMOKE TEST : FAILED ==='
                        throw err
                    }
                }
            }
        }

        // ══════════════════════════════════════════════════════
        // STAGE 6 - ARCHIVE ARTIFACTS
        // ══════════════════════════════════════════════════════
        stage('6 - Archive Artifacts') {
            steps {
                echo '=== STAGE 6 : Génération et archivage des artefacts ==='
                script {
                    def smokeResult = fileExists('artifacts/smoke-status.txt') ? readFile('artifacts/smoke-status.txt').trim() : 'UNKNOWN'

                    def report = """\
==============================================================
 RAPPORT D'EXECUTION PIPELINE - BIWEX STORE [DEV]
==============================================================
Date d'execution : ${new Date().format('dd/MM/yyyy HH:mm:ss')}
Pipeline         : Biwex-Store-Dev (Push sur dev)
Build Numero     : #${env.BUILD_NUMBER}
Branche          : ${env.BRANCH_NAME ?: 'dev'}
Commit           : ${env.GIT_COMMIT ?: 'N/A'}

IMAGES CONSTRUITES :
  - ${env.IMAGE_BASE}:dev-${env.BUILD_NUMBER}-py311 (Python 3.11 - Principal)
  - ${env.IMAGE_BASE}:dev-${env.BUILD_NUMBER}-py312 (Python 3.12 - Parallèle)

VERIFICATIONS EFFECTUEES :
  Stage 1 - Checkout        : PASSED
  Stage 2 - Setup           : PASSED
  Stage 3 - Build Parallèle : PASSED (Python 3.11 & 3.12)
  Stage 4 - Run Docker      : PASSED
  Stage 5 - Smoke Test      : ${smokeResult}
  Stage 6 - Archive         : PASSED

STATUT FINAL     : ${currentBuild.currentResult ?: 'SUCCESS'}

Binôme :
  - Famory TOURE  (feature/famory-toure)
  - Abdoul TRAORE (feature/abdoul-traore)
Projet DevOps 3LIG - ISG Sousse
==============================================================
"""
                    writeFile(file: 'artifacts/pipeline-report.txt', text: report)
                    echo report
                }

                archiveArtifacts(
                    artifacts: 'artifacts/**',
                    fingerprint: true,
                    allowEmptyArchive: true
                )
            }
        }
    }

    // ── POST ACTIONS : NETTOYAGE SYSTÉMATIQUE ───────────────────
    post {
        always {
            echo '=== Nettoyage des conteneurs et ressources temporaires ==='
            bat '''
                @echo off
                set "DOCKER_CMD=%DOCKER_BIN%"
                if not exist "%DOCKER_CMD%" set "DOCKER_CMD=docker"

                "%DOCKER_CMD%" rm -f %CONTAINER_NAME% 2>NUL
                "%DOCKER_CMD%" rmi %IMAGE_BASE%:dev-%BUILD_NUMBER%-py311 2>NUL
                "%DOCKER_CMD%" rmi %IMAGE_BASE%:dev-%BUILD_NUMBER%-py312 2>NUL
                exit /b 0
            '''
        }
        success {
            echo 'BIWEX STORE [DEV] : Pipeline termine avec SUCCES.'
        }
        failure {
            echo 'BIWEX STORE [DEV] : Echec du pipeline. Consultez les artefacts.'
        }
    }
}
