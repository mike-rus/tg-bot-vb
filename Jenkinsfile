pipeline {
    agent {
        node {
            label 'test'
        }
    }
    parameters {
        string(defaultValue: '-1002013382035', description: 'Enter th chat ID', name: 'CHAT_ID')
        string(defaultValue: '699', description: 'Enter the topic ID', name: 'TOPIC_ID')
    }

    stages {
        stage('Linter check') {
            steps {
                sh 'make lint_python_formatting'            
            }
        }
    }
    post {
        always {
            withCredentials([string(credentialsId: 'MikRusBotToken', variable: 'BOT_TOKEN')]) {
                script {
                    def author = env.CHANGE_AUTHOR
                    def name = determineTgName(author)

                    def shortCommitHash = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()

                    def message = "Message from Jenkins CI commit ${shortCommitHash} build #${env.BUILD_ID} PR ${env.CHANGE_ID} Result ${currentBuild.result} @${name}"
       
                    def apiUrl="https://api.telegram.org/bot${BOT_TOKEN}/sendDocument"
                    writeFile file: "${WORKSPACE}/build.log", text: currentBuild.rawBuild.getLog(1000).join('\n')

                    sh "curl -X POST -F 'document=@${WORKSPACE}/build.log' -F 'chat_id=${params.CHAT_ID}' -F 'reply_to_message_id=${params.TOPIC_ID}' -F 'caption=${message}' '${apiUrl}'"
                }

            }
            sendGitHubStatus(currentBuild.result.toLowerCase())

        }
    }
}

def sendGitHubStatus(status) {
    def gitHubContext = 'Linter check'
    def gitHubRepoOwner = 'mike-rus'
    def gitHubTokenOwner = 'mikerusjen'
    def gitHubRepoName = 'tg-bot-vb'
    def gitHubCommitSha = env.GIT_COMMIT

    withCredentials([string(credentialsId: 'github_token1', variable: 'GIT_HUB_TOKEN')]) {
        sh """
        curl -X POST -u ${gitHubTokenOwner}:${GIT_HUB_TOKEN} \
        -d '{"state": "${status}", "target_url": "${BUILD_URL}", "description": "${status.capitalize()} in Jenkins", "context": "${gitHubContext}"}' \
        https://api.github.com/repos/${gitHubRepoOwner}/${gitHubRepoName}/statuses/${gitHubCommitSha}
        """
    }
}


def determineTgName(author) {
    def name
    
    if (author == 'mike-rus') {
        name = 'Mike18R'
    } else if (author == 'Y') {
        name = 'polinaGrit'
    } else {
        name = 'Unknown'
    }
    
    return name
}