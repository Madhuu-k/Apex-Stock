pipeline {
  agent any

  environment {
    DOCKER_COMPOSE_FILE = 'docker-compose.yml'
  }

  stages {
    stage('Checkout') {
      steps {
        // If your Jenkins credential ID differs, change 'github-creds' below
        git branch: 'main',
            credentialsId: 'github-creds',
            url: 'https://github.com/Madhuu-k/Apex-Stock.git'
      }
    }

    stage('Stop Old') {
      steps {
        sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} down || true'
      }
    }

    stage('Build') {
      steps {
        sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} build --no-cache'
      }
    }

    stage('Deploy') {
      steps {
        sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} up -d'
      }
    }

    stage('Verify') {
      steps {
        sh '''
          sleep 8
          curl -f http://localhost:5000/api/health
          docker-compose -f ${DOCKER_COMPOSE_FILE} ps
        '''
      }
    }
  }

  post {
    failure {
      sh 'docker-compose -f docker-compose.yml logs || true'
    }
  }
}
