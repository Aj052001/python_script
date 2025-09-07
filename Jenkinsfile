pipeline {
  agent any

  parameters {
    string(name: 'PROMETHEUS_URL', defaultValue: 'http://localhost:9090', description: 'Prometheus URL')
    base64File(name: 'DEPLOYMENTS_EXCEL', description: 'Upload deployments xlsx (e.g. deployments.xlsx)')
    string(name: 'NAMESPACE', defaultValue: 'default', description: 'K8s namespace (optional)')
    string(name: 'STEP', defaultValue: '60s', description: 'Prometheus step (optional)')
  }

  stages {
    stage('Checkout') {
      steps {
        // if this Jenkinsfile is in the repo and job is Pipeline from SCM / Multibranch,
        // checkout scm will pull the code automatically
        checkout scm
      }
    }

    stage('Prepare Python') {
      steps {
        sh '''
          python3 -m venv .venv || true
          . .venv/bin/activate
          pip install -r requirements.txt || true
        '''
      }
    }

    stage('Run pod stats') {
      steps {
        // withFileParameter binds the uploaded file to an env var with path to temp file
        withFileParameter(name: 'DEPLOYMENTS_EXCEL', allowNoFile: false) {
          // pass params as env vars so your script (that reads os.getenv) can use them
          withEnv(["PROMETHEUS_URL=${params.PROMETHEUS_URL}",
                   "NAMESPACE=${params.NAMESPACE}",
                   "STEP=${params.STEP}"]) {
            sh '''
              . .venv/bin/activate
              echo "Using PROMETHEUS_URL=$PROMETHEUS_URL"
              python3 run.py "$DEPLOYMENTS_EXCEL"
            '''
          }
        }
      }
    }
  }

  post {
    always {
      // archive the generated xlsx so you can download it from Jenkins UI
      archiveArtifacts artifacts: 'pod_summary_with_memory.xlsx', allowEmptyArchive: true
    }
  }
}
