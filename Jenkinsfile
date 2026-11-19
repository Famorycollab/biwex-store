// ============================================================
//  PIPELINE 2 : BUILD COMPLET SUR PUSH (branche dev)
//  Déclencheur : chaque push sur la branche "dev"
//  But          : Construire, tester et archiver l'image Docker
//                 en mode parallèle (Python 3.11 et 3.12)
// ============================================================

pipeline {
    agent any

    // ── OPTIONS GLOBALES ────────────────────────────────────────
    options {
        skipDefaultCheckout(true)          // On contrôle le checkout manuellement
        timestamps()                        // Affiche l'heure devant chaque ligne de log
        disableConcurrentBuilds()           // Interdit deux builds simultanés (évite les conflits Docker)
        buildDiscarder(logRotator(numToKeepStr: '10'))  // Garde les 10 derniers builds
    }

    // ── VARIABLES D'ENVIRONNEMENT ───────────────────────────────
    environment {
        // Chemin complet vers l'exécutable Docker Desktop sur Windows
        DOCKER       = 'C:\\Users\\Famory Toure\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        // Nom de base de l'image Docker (sera suffixé par la version Python)
        IMAGE_BASE   = 'biwex-store'
        // Statut global du smoke test (mis à jour dans le stage 5)
        SMOKE_STATUS = 'NOT_RUN'
    }

    // ── DÉCLENCHEURS ────────────────────────────────────────────
    // Note : le trigger réel (push sur dev) est configuré dans Jenkins
    // via "GitHub hook trigger for GITScm polling" ou un Webhook GitHub

    stages {

        // ══════════════════════════════════════════════════════
        // STAGE 1 - CHECKOUT
        // Récupère le code source depuis GitHub (branche dev)
        // ══════════════════════════════════════════════════════
        stage('1 - Checkout') {
            steps {
                echo '╔══════════════════════════════════════╗'
                echo '║  STAGE 1 : Checkout du code source  ║'
                echo '╚══════════════════════════════════════╝'
                echo "Branche : ${env.BRANCH_NAME}"
                echo "Commit  : ${env.GIT_COMMIT}"

                // Télécharge le code depuis le dépôt GitHub configuré dans Jenkins
                checkout scm
            }
        }

        // ══════════════════════════════════════════════════════
        // STAGE 2 - SETUP
        // Vérifie que tous les fichiers nécessaires sont présents
        // et que Docker est accessible depuis Jenkins
        // ══════════════════════════════════════════════════════
        stage('2 - Setup') {
            steps {
                echo '╔══════════════════════════════════════╗'
                echo '║  STAGE 2 : Vérification environnement║'
                echo '╚══════════════════════════════════════╝'

                bat '''
                    @echo off
                    echo [Setup] Verification des fichiers obligatoires...

                    REM -- Vérification fichier application principal
                    if not exist app.py (
                        echo ERREUR : app.py manquant !
                        exit /b 1
                    )

                    REM -- Vérification des dépendances Python
                    if not exist requirements.txt (
                        echo ERREUR : requirements.txt manquant !
                        exit /b 1
                    )

                    REM -- Vérification de la recette Docker
                    if not exist Dockerfile (
                        echo ERREUR : Dockerfile manquant !
                        exit /b 1
                    )

                    REM -- Vérification du script de smoke test
                    if not exist scripts\\smoke_test.py (
                        echo ERREUR : scripts\\smoke_test.py manquant !
                        exit /b 1
                    )

                    REM -- Création du répertoire d'artefacts si inexistant
                    if not exist artifacts mkdir artifacts

                    echo [Setup] Tous les fichiers sont presents. OK
                    echo.

                    echo [Docker] Version de Docker :
                    "%DOCKER%" version

                    echo.
                    echo [Docker] Images existantes sur le systeme :
                    "%DOCKER%" images --format "table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}"
                '''
            }
        }

        // ══════════════════════════════════════════════════════
        // STAGE 3 - BUILD PARALLÈLE
        // Construit l'image Docker en PARALLÈLE pour :
        //   - Python 3.11 (version stable LTS)
        //   - Python 3.12 (version récente)
        // La parallélisation réduit le temps total de CI/CD
        // ══════════════════════════════════════════════════════
        stage('3 - Build Docker (Parallèle)') {
            parallel {

                // ── Build avec Python 3.11 ──────────────────
                stage('Build Python 3.11') {
                    steps {
                        echo '╔═══════════════════════════════════════╗'
                        echo '║  Build Docker - Python 3.11           ║'
                        echo '╚═══════════════════════════════════════╝'

                        bat '''
                            @echo off
                            echo [Build 3.11] Construction de l image Docker avec Python 3.11...

                            REM -- Construction de l'image avec l'ARG PYTHON_VERSION
                            REM -- Le tag inclut le numéro de build Jenkins pour traçabilité
                            "%DOCKER%" build ^
                                --build-arg PYTHON_VERSION=3.11 ^
                                -t biwex-store:dev-%BUILD_NUMBER%-py311 ^
                                . ^
                                > artifacts\\docker-build-py311.log 2>&1

                            set "EXIT_CODE=%ERRORLEVEL%"

                            REM -- Affiche le log pour les archives Jenkins
                            type artifacts\\docker-build-py311.log

                            REM -- Propage le code d'erreur si le build a échoué
                            exit /b %EXIT_CODE%
                        '''
                    }
                }

                // ── Build avec Python 3.12 ──────────────────
                stage('Build Python 3.12') {
                    steps {
                        echo '╔═══════════════════════════════════════╗'
                        echo '║  Build Docker - Python 3.12           ║'
                        echo '╚═══════════════════════════════════════╝'

                        bat '''
                            @echo off
                            echo [Build 3.12] Construction de l image Docker avec Python 3.12...

                            "%DOCKER%" build ^
                                --build-arg PYTHON_VERSION=3.12 ^
                                -t biwex-store:dev-%BUILD_NUMBER%-py312 ^
                                . ^
                                > artifacts\\docker-build-py312.log 2>&1

                            set "EXIT_CODE=%ERRORLEVEL%"

                            type artifacts\\docker-build-py312.log

                            exit /b %EXIT_CODE%
                        '''
                    }
                }
            }
        }

        // ══════════════════════════════════════════════════════
        // STAGE 4 - RUN DOCKER
        // Démarre un conteneur de test temporaire basé sur
        // l'image Python 3.11 (image principale de référence)
        // Le conteneur tourne en arrière-plan (-d)
        // ══════════════════════════════════════════════════════
        stage('4 - Run Docker') {
            steps {
                echo '╔══════════════════════════════════════╗'
                echo '║  STAGE 4 : Démarrage du conteneur   ║'
                echo '╚══════════════════════════════════════╝'

                bat '''
                    @echo off
                    set "CONTAINER=biwex-store-dev-test-%BUILD_NUMBER%"

                    echo [Run] Suppression de tout conteneur residuel avec le meme nom...
                    "%DOCKER%" rm -f %CONTAINER% 2>NUL

                    echo [Run] Demarrage du conteneur de test...
                    REM -- SECRET_KEY : clé secrète Flask injectée en variable d'environnement
                    REM -- -d : mode détaché (conteneur en arrière-plan)
                    "%DOCKER%" run -d ^
                        --name %CONTAINER% ^
                        -e SECRET_KEY=jenkins-dev-ci-secret-key ^
                        biwex-store:dev-%BUILD_NUMBER%-py311

                    if errorlevel 1 (
                        echo ERREUR : Echec du demarrage du conteneur !
                        exit /b 1
                    )

                    echo [Run] Conteneur demarre avec succes : %CONTAINER%
                    echo [Run] Attente de 5 secondes pour l initialisation de l application...
                    timeout /t 5 /nobreak >NUL

                    echo [Run] Etat du conteneur :
                    "%DOCKER%" ps --filter name=%CONTAINER% --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"
                '''
            }
        }

        // ══════════════════════════════════════════════════════
        // STAGE 5 - SMOKE TEST
        // Test rapide "go/no-go" : vérifie que l'application
        // répond sur HTTP 200 après démarrage.
        // - Jusqu'à 15 tentatives avec 2 sec d'attente entre chaque
        // - Résultat PASSED ou FAILED enregistré dans un fichier
        // - En cas d'échec, le pipeline est marqué FAILED
        // ══════════════════════════════════════════════════════
        stage('5 - Smoke Test') {
            steps {
                echo '╔══════════════════════════════════════╗'
                echo '║  STAGE 5 : Smoke Test HTTP           ║'
                echo '╚══════════════════════════════════════╝'

                script {
                    // On utilise un try/catch pour capturer le statut (PASSED/FAILED)
                    // même si le test échoue, pour l'écrire dans le rapport final
                    try {
                        bat '''
                            @echo off
                            set "CONTAINER=biwex-store-dev-test-%BUILD_NUMBER%"

                            echo [Smoke] Lancement du smoke test sur http://127.0.0.1:5000/
                            echo [Smoke] Maximum 15 tentatives, 2 secondes entre chaque...
                            echo.

                            REM -- Boucle de retry : attend que l'appli soit prête
                            for /L %%i in (1,1,15) do (
                                echo [Smoke] Tentative %%i sur 15...

                                REM -- Exécute le script Python DANS le conteneur Docker
                                "%DOCKER%" exec %CONTAINER% python /app/scripts/smoke_test.py http://127.0.0.1:5000/ > artifacts\\smoke-test.txt 2>&1

                                REM -- Si le code de retour est 0, le test est passé
                                if not errorlevel 1 goto :smoke_ok

                                REM -- Sinon, attendre avant de réessayer
                                timeout /t 2 /nobreak >NUL
                            )

                            REM -- Après 15 tentatives sans succès → FAILED
                            type artifacts\\smoke-test.txt
                            echo.
                            echo [Smoke] RESULTAT FINAL : FAILED apres 15 tentatives
                            exit /b 1

                            :smoke_ok
                            type artifacts\\smoke-test.txt
                            echo.
                            echo [Smoke] RESULTAT FINAL : PASSED
                            exit /b 0
                        '''

                        // Mise à jour de la variable d'environnement Jenkins
                        env.SMOKE_STATUS = 'PASSED'

                        // Écriture du fichier de statut pour le rapport
                        writeFile(file: 'artifacts/smoke-status.txt', text: 'PASSED')

                    } catch (err) {
                        // Le test a échoué après toutes les tentatives
                        env.SMOKE_STATUS = 'FAILED'
                        writeFile(file: 'artifacts/smoke-status.txt', text: 'FAILED')

                        // On relance l'exception pour marquer le build FAILED
                        throw err
                    }
                }
            }
        }

        // ══════════════════════════════════════════════════════
        // STAGE 6 - ARCHIVE ARTIFACTS
        // Génère un rapport de pipeline synthétique et archive
        // tous les artefacts dans Jenkins pour traçabilité :
        //   - docker-build-py311.log
        //   - docker-build-py312.log
        //   - smoke-test.txt
        //   - smoke-status.txt
        //   - pipeline-report.txt
        // ══════════════════════════════════════════════════════
        stage('6 - Archive Artifacts') {
            steps {
                echo '╔══════════════════════════════════════╗'
                echo '║  STAGE 6 : Archivage des artefacts  ║'
                echo '╚══════════════════════════════════════╝'

                script {
                    // Lecture du résultat du smoke test
                    def smokeResult = 'UNKNOWN'
                    if (fileExists('artifacts/smoke-status.txt')) {
                        smokeResult = readFile('artifacts/smoke-status.txt').trim()
                    }

                    // Génération d'un rapport de pipeline lisible
                    def report = """\
╔══════════════════════════════════════════════════════╗
║          RAPPORT DE PIPELINE - BIWEX STORE          ║
╚══════════════════════════════════════════════════════╝

PIPELINE      : Biwex-Store-Dev (Build complet sur push)
BUILD N°      : ${env.BUILD_NUMBER}
BRANCHE       : ${env.BRANCH_NAME ?: 'dev'}
COMMIT        : ${env.GIT_COMMIT ?: 'N/A'}
DATE          : ${new Date().format('dd/MM/yyyy HH:mm:ss')}

IMAGES DOCKER :
  - biwex-store:dev-${env.BUILD_NUMBER}-py311  (Python 3.11)
  - biwex-store:dev-${env.BUILD_NUMBER}-py312  (Python 3.12)

RÉSULTATS DES STAGES :
  Stage 1 - Checkout          : OK
  Stage 2 - Setup             : OK
  Stage 3 - Build Parallèle   : OK (Python 3.11 + 3.12)
  Stage 4 - Run Docker        : OK
  Stage 5 - Smoke Test        : ${smokeResult}
  Stage 6 - Archive           : OK

RÉSULTAT GLOBAL : ${currentBuild.currentResult}

ÉQUIPE : Famory TOURE & Abdoul TRAORE
MODULE : Introduction au DevOps - 3LIG
══════════════════════════════════════════════════════
"""
                    writeFile(file: 'artifacts/pipeline-report.txt', text: report)
                    echo report
                }

                // Archive tous les fichiers du dossier artifacts/
                archiveArtifacts(
                    artifacts: 'artifacts/**',
                    fingerprint: true,
                    allowEmptyArchive: true
                )

                echo '[Archive] Artefacts archivés avec succès dans Jenkins.'
            }
        }

    } // fin stages

    // ── POST-ACTIONS ────────────────────────────────────────────
    // Ces actions s'exécutent TOUJOURS après les stages, peu importe
    // si le build a réussi ou échoué
    post {

        // Nettoyage systématique : supprime les conteneurs de test
        // et les images temporaires pour libérer de l'espace disque
        always {
            echo '╔══════════════════════════════════════╗'
            echo '║  POST : Nettoyage des ressources     ║'
            echo '╚══════════════════════════════════════╝'

            bat '''
                @echo off
                set "CONTAINER=biwex-store-dev-test-%BUILD_NUMBER%"

                echo [Cleanup] Suppression du conteneur de test...
                "%DOCKER%" rm -f %CONTAINER% 2>NUL

                echo [Cleanup] Suppression des images temporaires de ce build...
                "%DOCKER%" rmi biwex-store:dev-%BUILD_NUMBER%-py311 2>NUL
                "%DOCKER%" rmi biwex-store:dev-%BUILD_NUMBER%-py312 2>NUL

                echo [Cleanup] Nettoyage termine.
                exit /b 0
            '''
        }

        success {
            echo '✅ ════════════════════════════════════════════════════'
            echo '✅  BIWEX STORE [DEV] : Pipeline exécuté avec SUCCÈS !'
            echo '✅  Toutes les vérifications ont passé.'
            echo '✅ ════════════════════════════════════════════════════'
        }

        failure {
            echo '❌ ════════════════════════════════════════════════════'
            echo '❌  BIWEX STORE [DEV] : Le pipeline a ÉCHOUÉ.'
            echo '❌  Vérifiez les logs des stages en rouge ci-dessus.'
            echo '❌ ════════════════════════════════════════════════════'
        }

        unstable {
            echo '⚠️  BIWEX STORE [DEV] : Pipeline INSTABLE. Vérifiez les tests.'
        }
    }
}
