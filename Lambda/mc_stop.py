import boto3
import os
import time
import requests

# 環境変数から値を取得する
# EC2インスタンスID
instance_id = os.environ['INSTANCE_ID']
# Discord Webhook URL
webhook_url = os.environ['WEBHOOK_URL']
# Minecraft Logfile Path
log_path= os.environ['LOG_PATH']
# コマンド実行結果の最大待ち時間(秒)
max_wait_time = os.environ['MAX_WAIT_TIME']

# HTMLを返却する
# 関数URLをブラウザから実行した場合にfavicon.icoへのアクセスにより重複実行することを避ける
success = {
    'statusCode':200,
    'headers':{
            'Content-Type':'text/html'
    },
    'body': '<html><head><link rel="icon" href="data:,"></head><body>success</body></html>'
}

def lambda_handler(event, context):

    # インスタンスの稼働状況を確認する
    ec2 = boto3.client('ec2')
    state = check_instance_state(ec2)
    
    # インスタンスが起動していない場合は何もしない
    if state != 'running':
        #DiscordにWebhookを送信
        _ = send_webhook(f'インスタンスが起動していません:{state}')
        return success

    # SSMクライアントの作成
    ssm = boto3.client('ssm')

    # Run Commandを使用してログファイルの読み込みを行う
    try:
        command = 'sudo cat ' + log_path
        log_content = command_runner(ssm, wait=10, command=command)
    except Exception as e:
        msg = f'{e}\nコマンド:{command}'
        print(msg)
        # DiscordにWebhookを送信
        _ = send_webhook(msg)
        return success

    # Minecraftのログを分析する(ログイン中のユーザ数の確認)
    login_user_num = minecraft_log_info(log_content)

    if login_user_num != 0:
        # DiscordにWebhookを送信
        _ = send_webhook(f'{str(login_user_num)}名がログイン中です')
        return success

    # Minecraftサーバの停止
    try:
        # Run Commandを使用してコマンドを実行する
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': [
                'sudo systemctl stop minecraft',
                'sudo shutdown -h now'
            ]}
        )
    except Exception as e:
        msg = f'停止コマンドの実行に失敗しました\n{e}'
        print(msg)
        _ = send_webhook(msg)

    _ = send_webhook('インスタンスの停止を開始しました')
    return success

# ec2インスタンスの起動を確認する
def check_instance_state(ec2):
    instance = ec2.describe_instances(InstanceIds=[instance_id])
    state = instance['Reservations'][0]['Instances'][0]['State']['Name']
    return state

# EC2でコマンドを実行
def command_runner(ssm, wait, command):
    # Run Commandを使用してコマンドを実行する
    response = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': [command]}
    )
    # Run Command実行結果からCommandId取得
    command_id = response['Command']['CommandId']

    # Run Commandの実行結果が取得できるまでwaitを行う
    command_success = False
    wait_time = 0
    while not command_success:
        response = ssm.list_commands(CommandId=command_id)
        status = response['Commands'][0]['Status']
        if status == 'Success':
            command_success = True
        else:
            # 10秒待つ
            time.sleep(10)
            wait_time += 10
            # 最大待ち時間を超えた場合は関数をエラーで終了する
            if wait_time >= int(max_wait_time):
                raise Exception(f'コマンドが実行できませんでした。:{status}')

    # Run Commandの実行結果を取得
    response_result = ssm.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id
    )
    # 実行結果からコンソール出力を取得
    return response_result['StandardOutputContent']

# Minecraftのログを分析する
def minecraft_log_info(log):
    # ログの改行ごとに配列化する
    log_lines = log.split('\n')

    # ログインユーザ数とログアウトユーザ数をカウントする
    login_count = 0
    logout_count = 0
    for line in log_lines:
        if 'joined the game' in line:
            login_count += 1
            print(line)
        if 'left the game' in line:
            logout_count += 1
            print(line)

    print(f"ログイン:{str(login_count)} ログアウト:{str(logout_count)}")
    return login_count - logout_count

# DiscordにWebhookを送信
def send_webhook(content):
    data = {'content': content}
    result = requests.post(webhook_url, json=data)
    return result