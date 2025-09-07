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
                // Windows CMD style
                bat '''
                python -m venv .venv || exit 0
                .\\.venv\\Scripts\\activate
                pip install -r requirements.txt || exit 0
                '''
            }
        }

        stage('Run pod stats') {
            steps {
                withEnv(["PROMETHEUS_URL=${params.PROMETHEUS_URL}"]) {
                    bat """
                    .\\.venv\\Scripts\\activate
                    echo PROMETHEUS_URL=%PROMETHEUS_URL%
                    dir %DEPLOYMENTS_EXCEL%
                    python run.py "%DEPLOYMENTS_EXCEL%"
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
