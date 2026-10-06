pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
    }

    parameters {
        choice(
            name: 'RUN_MODE',
            choices: ['validate', 'collect'],
            description: 'validate — scheduled live check; collect — manual snapshot and baseline update'
        )
        choice(
            name: 'SITE',
            choices: ['auto', '101', 'mol', 'pol'],
            description: 'Site label, or auto-detect from URL hostname'
        )
    }

    triggers {
        // Replace with the agreed client timezone and schedule before enabling in production.
        cron('TZ=Europe/Moscow\n0 6 * * *')
    }

    stages {
        stage('Run TASKDEV-3188') {
            steps {
                dir('taskdev_3188') {
                    sh '''
                        set -eu
                        if [ "${RUN_MODE}" = "collect" ]; then
                            python3 -m taskdev_3188.cli --urls urls.txt --state-dir state collect
                        else
                            python3 -m taskdev_3188.cli --urls urls.txt --state-dir state --site "${SITE}" --allure-dir allure-results validate
                        fi
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'taskdev_3188/state/*.json', allowEmptyArchive: true, fingerprint: true
            allure includeProperties: false, jdk: '', results: [[path: 'taskdev_3188/allure-results']]
            // Do not clean the workspace until state is moved to a persistent Jenkins volume.
        }
    }
}
