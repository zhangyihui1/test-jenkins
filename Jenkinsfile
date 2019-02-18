pipeline {
    agent any
    options {
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr:'20'))
        timeout(time: 30, unit: 'MINUTES')
    } 
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
                        sh "${env.startServerScript} --package-url ${env.mcuPackageUrl} --package-name \
                        mcu-all-bin-v{data}.tgz  --base-dir ${env.mcuServerBasePath} --git-branch ${GIT_BRANCH} --owner zhangyihui1 
                        --repo test-jenkins --commit-id ${GIT_COMMIT} --github-script /home/webrtctest3/zyh_github_test/github_checks/push_result.py"
                    }
                }
            }
        }
        stage('startP2PServer'){
            agent{
                node {
                    label "${env.p2pServer}"
                }
            }
            steps{
                script{
                    withEnv(['JENKINS_NODE_COOKIE=dontkill']) {
                        sh "${env.startServerScript} --server-path ${env.p2pServerPath}" --owner zhangyihui1 --repo test-jenkins --commit-id ${GIT_COMMIT} --github-script /home/webrtctest3/zyh_github_test/github_checks/push_result.py"
                        }    
                }
            }
        }
        stage('runAndroidCICase'){
            agent{
                node {
                    label "${env.androidRunCaseServer}"
                }
            }
            steps {
                sh "python /home/webrtctest3/zyh_github_test/webrtc-webrtc-qa/dailyTestScript/testScript/android/runTest.py --log-dir /home/webrtctest3/workspace/Test/log/${GIT_COMMIT} --dependencies-dir ${env.andoridLibWebrtcPath} --source-path /home/webrtctest3/zyh_github_test/oms-client-android --instrumentation /home/webrtctest3/zyh_github_test/webrtc-webrtc-qa/dailyTestScript/testScript/android/caselist.json --unit --p2p-server http://webrtc151.sh.intel.com:8095 --conference-server-http http://webrtc151.sh.intel.com:3001 --mode ci --owner zhangyihui1 --repo test-jenkins --commit-id ${GIT_COMMIT} --github-script /home/webrtctest3/zyh_github_test/github_checks/push_result.py"
            }
        }
    }
}
