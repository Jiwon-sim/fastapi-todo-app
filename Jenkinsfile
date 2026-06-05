pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: python
    image: python:3.11-slim
    command:
    - sleep
    args:
    - infinity
  - name: trivy
    image: aquasec/trivy:latest
    command:
    - sleep
    args:
    - infinity
  - name: docker
    image: docker:24-dind
    securityContext:
      privileged: true
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
'''
        }
    }

    environment {
        IMAGE_NAME = "zziwon/fastapi-todo"
    }

    stages {
        stage('SAST - Bandit') {
            steps {
                container('python') {
                    sh '''
                        pip install bandit -q
                        bandit -r . \
                            -x ./.venv,./tests \
                            -f json \
                            -o bandit-report.json \
                            --exit-zero
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit-report.json'
                }
            }
        }

        stage('SCA - Trivy Filesystem') {
            steps {
                container('trivy') {
                    sh '''
                        trivy fs . \
                            --format json \
                            --output trivy-sca-report.json \
                            --exit-code 0 \
                            --severity CRITICAL,HIGH
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-sca-report.json'
                }
            }
        }

        stage('Docker Build') {
            steps {
                container('docker') {
                    sh "docker build -t ${IMAGE_NAME}:${GIT_COMMIT} ."
                }
            }
        }

        stage('Image Scan - Trivy') {
            steps {
                container('trivy') {
                    sh """
                        trivy image \
                            --format json \
                            --output trivy-image-report.json \
                            --exit-code 0 \
                            --severity CRITICAL,HIGH \
                            ${IMAGE_NAME}:${GIT_COMMIT}
                    """
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-image-report.json'
                }
            }
        }

        stage('Docker Push') {
            steps {
                container('docker') {
                    withCredentials([usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh """
                            echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                            docker push ${IMAGE_NAME}:${GIT_COMMIT}
                            docker tag ${IMAGE_NAME}:${GIT_COMMIT} ${IMAGE_NAME}:latest
                            docker push ${IMAGE_NAME}:latest
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            echo '파이프라인 완료'
        }
        success {
            echo '✅ 성공'
        }
        failure {
            echo '❌ 실패'
        }
    }
}