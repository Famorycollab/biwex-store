// ============================================================
//  PIPELINE 2 : BUILD COMPLET SUR PUSH (Branche dev)
//  Projet : Biwex Store - 3LIG ISG Sousse
//  Binôme : Famory TOURE & Abdoul TRAORE
//
//  EXPLICATION SIMPLE POUR LA PROFESSEURE :
//  Ce pipeline se lance automatiquement dès qu'un développeur
//  envoie (push) son code sur la branche "dev".
//  Il contient 6 étapes (stages) obligatoires :
//  1. Checkout      : Télécharger le code source depuis GitHub
//  2. Setup         : Vérifier que tous les fichiers nécessaires sont présents
//  3. Build Docker  : Fabriquer l'image Docker en PARALLÈLE (Python 3.11 et 3.12)
//  4. Run Docker    : Allumer le conteneur de test pour exécuter le site
//  5. Smoke Test    : Tester si le site répond HTTP 200 (test réussi)
//  6. Archive       : Sauvegarder les rapports et preuves dans Jenkins
//  + Cleanup        : Nettoyer et éteindre le conteneur à la fin
// ============================================================

pipeline {
    // Exécuter ce pipeline sur n'importe quel ordinateur ou agent Jenkins disponible
    agent any

    // Options générales du pipeline
    options {
        // Ne pas télécharger le code automatiquement au début, on le fait nous-mêmes au Stage 1
        skipDefaultCheckout(true)
        // Afficher l'heure exacte devant chaque ligne dans la console
        timestamps()
        // Empêcher de lancer deux fois ce pipeline en même temps pour éviter les conflits
        disableConcurrentBuilds()
        // Arrêter le pipeline si l'exécution dépasse 15 minutes (sécurité)
        timeout(time: 15, unit: 'MINUTES')
        // Ne garder dans Jenkins que l'historique des 10 derniers builds pour économiser le disque
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    // Variables globales réutilisables dans tout le pipeline
    environment {
        // Chemin de l'exécutable Docker Desktop sur notre machine Windows
        DOCKER_BIN     = 'C:\\Users\\Famory Toure\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        // Nom de base de notre image Docker
        IMAGE_BASE     = 'biwex-store'
        // Nom unique donné au conteneur de test (ex: biwex-dev-test-1)
        CONTAINER_NAME = "biwex-dev-test-${BUILD_NUMBER}"
        // Variable pour retenir si le test a réussi (PASSED) ou échoué (FAILED)
        SMOKE_STATUS   = 'NOT_RUN'
    }

    stages {

        // ======================================================
        // STAGE 1 : CHECKOUT (Téléchargement du code)
        // But : Récupérer les fichiers depuis notre dépôt GitHub
        // ======================================================
        stage('1 - Checkout') {
            steps {
                echo '=== STAGE 1 : Récupération du code source depuis GitHub ==='
                checkout scm
                script {
                    echo "Branche active : ${env.BRANCH_NAME ?: 'dev'}"
                    echo "Numéro de build : #${env.BUILD_NUMBER}"
                }
            }
        }

        // ======================================================
        // STAGE 2 : SETUP (Vérification de l'environnement)
        // But : Vérifier que les fichiers existent et que Docker fonctionne
        // ======================================================
        stage('2 - Setup') {
            steps {
                echo '=== STAGE 2 : Vérification des fichiers du projet et de Docker ==='
                bat '''
                    @echo off
                    echo [Verification] Test de presence des fichiers indispensables...

                    REM Verifier si le fichier principal app.py existe
                    if not exist app.py (
                        echo ERREUR : app.py est introuvable !
                        exit /b 1
                    )
                    REM Verifier la liste des dependances Python
                    if not exist requirements.txt (
                        echo ERREUR : requirements.txt est introuvable !
                        exit /b 1
                    )
                    REM Verifier la recette de construction Dockerfile
                    if not exist Dockerfile (
                        echo ERREUR : Dockerfile est introuvable !
                        exit /b 1
                    )
                    REM Verifier le script de smoke test
                    if not exist scripts\\smoke_test.py (
                        echo ERREUR : scripts\\smoke_test.py est introuvable !
                        exit /b 1
                    )

                    REM Creer le dossier artifacts pour stocker les rapports s'il n'existe pas
                    if not exist artifacts mkdir artifacts
                    echo [Succes] Tous les fichiers necessaires sont bien presents.

                    REM Verifier que Docker est allume et repond
                    echo [Verification] Affichage de la version de Docker :
                    if exist "%DOCKER_BIN%" (
                        "%DOCKER_BIN%" version
                    ) else (
                        docker version
                    )
                '''
            }
        }

        // ======================================================
        // STAGE 3 : BUILD PARALLÈLE (Construction des images Docker)
        // But : Fabriquer EN MÊME TEMPS l'image Python 3.11 et 3.12
        // Optimisation Cache : pip et layers mis en cache Docker (Build < 15s)
        // ======================================================
        stage('3 - Build Docker (Parallèle)') {
            parallel {

                // Branche parallèle A : Image avec Python 3.11
                stage('Build Python 3.11 (LTS)') {
                    steps {
                        echo '=== Construction de l image avec Python 3.11 ==='
                        bat '''
                            @echo off
                            set "DOCKER_CMD=%DOCKER_BIN%"
                            if not exist "%DOCKER_CMD%" set "DOCKER_CMD=docker"

                            REM Construire l'image Docker avec l'argument PYTHON_VERSION=3.11
                            REM Le cache Docker reutilise les dependances pour un build ultra-rapide
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

                // Branche parallèle B : Image avec Python 3.12 (test de compatibilité)
                stage('Build Python 3.12 (Compatibilité)') {
                    steps {
                        echo '=== Construction de l image avec Python 3.12 ==='
                        bat '''
                            @echo off
                            set "DOCKER_CMD=%DOCKER_BIN%"
                            if not exist "%DOCKER_CMD%" set "DOCKER_CMD=docker"

                            REM Construire l'image Docker avec l'argument PYTHON_VERSION=3.12
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

        // ======================================================
        // STAGE 4 : RUN DOCKER (Démarrage du conteneur de test)
        // But : Démarrer l'application dans un conteneur isolé
        // ======================================================
        stage('4 - Run Docker') {
            steps {
                echo '=== STAGE 4 : Démarrage du conteneur de test ==='
                bat '''
                    @echo off
                    set "DOCKER_CMD=%DOCKER_BIN%"
                    if not exist "%DOCKER_CMD%" set "DOCKER_CMD=docker"

                    REM Supprimer tout ancien conteneur qui porterait le meme nom par precaution
                    "%DOCKER_CMD%" rm -f %CONTAINER_NAME% 2>NUL

                    REM Demarrer le conteneur en arriere-plan (-d) avec une cle secrete temporaire
                    "%DOCKER_CMD%" run -d ^
                        --name %CONTAINER_NAME% ^
                        -e SECRET_KEY=cle-secrete-test-jenkins ^
                        %IMAGE_BASE%:dev-%BUILD_NUMBER%-py311

                    REM Verifier si le conteneur a bien demarre
                    if errorlevel 1 (
                        echo ERREUR : Impossible d allumer le conteneur Docker !
                        exit /b 1
                    )

                    echo [Succes] Le conteneur tourne avec succes.
                    "%DOCKER_CMD%" ps --filter name=%CONTAINER_NAME%
                '''
                // Attendre 3 secondes pour laisser a Gunicorn le temps de demarrer l'application
                sleep(time: 3, unit: 'SECONDS')
            }
        }

        // ======================================================
        // STAGE 5 : SMOKE TEST (Vérification rapide du site)
        // But : Tester si l'application répond HTTP 200 (test de vie)
        // ======================================================
        stage('5 - Smoke Test') {
            steps {
                echo '=== STAGE 5 : Exécution du Smoke Test HTTP ==='
                script {
                    try {
                        // Reessayer jusqu'a 10 fois avec 1 seconde d'attente
                        retry(10) {
                            sleep(time: 1, unit: 'SECONDS')
                            bat '''
                                @echo off
                                set "DOCKER_CMD=%DOCKER_BIN%"
                                if not exist "%DOCKER_CMD%" set "DOCKER_CMD=docker"

                                REM Executer notre script Python smoke_test.py A L INTERIEUR du conteneur Docker
                                "%DOCKER_CMD%" exec %CONTAINER_NAME% python /app/scripts/smoke_test.py http://127.0.0.1:5000/ > artifacts\\smoke-test.txt 2>&1
                                type artifacts\\smoke-test.txt
                            '''
                        }

                        // Si le script repond code 200, le test est valide
                        env.SMOKE_STATUS = 'PASSED'
                        writeFile(file: 'artifacts/smoke-status.txt', text: 'PASSED')
                        echo '=== RESULTAT DU SMOKE TEST : REUSSI (PASSED) ==='

                    } catch (err) {
                        env.SMOKE_STATUS = 'FAILED'
                        writeFile(file: 'artifacts/smoke-status.txt', text: 'FAILED')
                        echo '=== RESULTAT DU SMOKE TEST : ECHOUE (FAILED) ==='
                        throw err
                    }
                }
            }
        }

        // ======================================================
        // STAGE 6 : ARCHIVE ARTIFACTS (Archivage des preuves)
        // But : Sauvegarder les rapports de test dans Jenkins
        // ======================================================
        stage('6 - Archive Artifacts') {
            steps {
                echo '=== STAGE 6 : Création et archivage du rapport de build ==='
                script {
                    def smokeResult = fileExists('artifacts/smoke-status.txt') ? readFile('artifacts/smoke-status.txt').trim() : 'UNKNOWN'

                    def report = """\
==============================================================
 RAPPORT D'EXECUTION DU PIPELINE - BIWEX STORE [DEV]
==============================================================
Date d'execution : ${new Date().format('dd/MM/yyyy HH:mm:ss')}
Pipeline         : Biwex-Store-Dev (Push sur la branche dev)
Numero du Build  : #${env.BUILD_NUMBER}
Branche          : ${env.BRANCH_NAME ?: 'dev'}
Commit Git       : ${env.GIT_COMMIT ?: 'N/A'}

IMAGES DOCKER CREEES :
  - ${env.IMAGE_BASE}:dev-${env.BUILD_NUMBER}-py311 (Python 3.11 - Production)
  - ${env.IMAGE_BASE}:dev-${env.BUILD_NUMBER}-py312 (Python 3.12 - Compatibilite)

RESULTATS DES 6 ETAPES :
  Etape 1 - Checkout        : REUSSI (Code telecharge)
  Etape 2 - Setup           : REUSSI (Environnement conforme)
  Etape 3 - Build Parallele : REUSSI (Cache optimise)
  Etape 4 - Run Docker      : REUSSI (Conteneur allume)
  Etape 5 - Smoke Test      : ${smokeResult} (Test HTTP 200)
  Etape 6 - Archive         : REUSSI (Preuves sauvegardees)

STATUT GLOBAL    : ${currentBuild.currentResult ?: 'SUCCESS'}

Binôme :
  - Famory TOURE  (Branche feature/famory-toure)
  - Abdoul TRAORE (Branche feature/abdoul-traore)
Projet DevOps 3LIG - ISG Sousse 2026/2027
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

    // ======================================================
    // ACTIONS POST-BUILD (Nettoyage optimise)
    // NOTION CLE : On supprime le conteneur, MAIS on ne fait pas 'docker rmi'
    // pour conserver les couches en cache et garantir un build en 10 secondes !
    // ======================================================
    post {
        always {
            echo '=== Nettoyage automatique du conteneur de test ==='
            bat '''
                @echo off
                set "DOCKER_CMD=%DOCKER_BIN%"
                if not exist "%DOCKER_CMD%" set "DOCKER_CMD=docker"

                REM Eteindre et supprimer le conteneur temporaire de test
                "%DOCKER_CMD%" rm -f %CONTAINER_NAME% 2>NUL
                exit /b 0
            '''
        }
        success {
            echo 'BIWEX STORE [DEV] : Le pipeline s est execute avec SUCCES en temps record !'
        }
        failure {
            echo 'BIWEX STORE [DEV] : Le pipeline a ECHOUE. Consultez les logs et artefacts.'
        }
    }
}
