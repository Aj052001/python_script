pipeline {
    agent any

    parameters {
        string(name: 'PROMETHEUS_URL', defaultValue: 'http://localhost:9090', description: 'Prometheus URL')
        file(name: 'DEPLOYMENTS_EXCEL', description: 'Upload deployments excel (xlsx)')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Python') {
            steps {
                // Windows CMD style with full Python path
                bat '''
                C:\\Python311\\python.exe -m venv .venv || exit 0
                call .\\.venv\\Scripts\\activate
                .\\.venv\\Scripts\\pip.exe install -r requirements.txt || exit 0
                '''
            }
        }

        stage('Run pod stats') {
            steps {
                withEnv([
                    "PROMETHEUS_URL=${params.PROMETHEUS_URL}",
                    "DEPLOYMENTS_FILE=${params.DEPLOYMENTS_EXCEL}"
                ]) {
                    bat """
                    call .\\.venv\\Scripts\\activate
                    echo PROMETHEUS_URL=%PROMETHEUS_URL%
                    echo DEPLOYMENTS_FILE=%DEPLOYMENTS_FILE%
                    C:\\Python311\\python.exe run.py "%DEPLOYMENTS_FILE%"
                    """
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'pod_summary_with_memory.xlsx', allowEmptyArchive: true
        }
    }
}
