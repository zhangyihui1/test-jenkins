pipeline {
    agent any
    stages {
        stage('startMCU'){
            agent{
                node {
                    label "yihui"
                }
            }
            steps {
                script{
                    sh "python3 /home/fengwei/github_checks/push_result.py --owner zhangyihui1 --repo test-jenkins --commit-id ${GIT_COMMIT} --name ${env.AndroidConferenceResultName} --title ${env.AndroidConferenceResultTitle} --summary \"test success\""
                }
            }
        }
    }
}