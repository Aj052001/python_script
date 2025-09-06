pipeline {
    agent any

    parameters {
        file(name: 'INPUT_FILE', description: 'Upload your Excel file')
        string(name: 'OUTPUT_FILE', defaultValue: 'output_cleaned.xlsx', description: 'Path to save cleaned Excel file')
    }

    stages {
        stage('Setup Python Env') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run Script') {
            steps {
                sh ". venv/bin/activate && python run.py ${params.INPUT_FILE} ${params.OUTPUT_FILE}"
            }
        }
    }

    post {
        success {
            archiveArtifacts artifacts: "${params.OUTPUT_FILE}", fingerprint: true
            echo "✅ Cleaned Excel uploaded as Jenkins artifact."
        }
    }
}
