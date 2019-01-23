pipeline {
    agent any
    stages {
        stage('startMCU'){
            agent{
                node {
                    label "${env.mcuServer}"
                }
            }
            steps {
                script{
                    withEnv(['JENKINS_NODE_COOKIE=dontkill']) {
                        sh "${env.starMcuScriptPath} --package-url ${env.mcuPackageUrl} --package-name \
                        mcu-all-bin-v{data}.tgz  --base-dir ${env.mcuServerBasePath} --git-branch ${GIT_BRANCH}"
                    }
                }
            }
        }
    }
}
