import boto3
import time
import requests
import os

# 環境変数から値を取得する
# EC2インスタンスID
instance_id = os.environ['INSTANCE_ID']
# Discord Webhook URL
webhook_url = os.environ['WEBHOOK_URL']
# インスタンス起動までの最大待ち時間(秒)
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
    ec2 = boto3.client('ec2')
    state = check_instance_state(ec2)
    if state == 'running':
        #DiscordにWebhookを送信
        _ = send_webhook('インスタンスはすでに起動しています')
        return success

    # EC2インスタンスを起動するためのパラメータ
    _ = ec2.start_instances(InstanceIds=[instance_id])

    # EC2インスタンスが起動するのを待つ
    instance_running = False
    wait_time = 0
    while not instance_running:
        state = check_instance_state(ec2)
        if state == 'running':
            instance_running = True
        else:
            # 10秒待つ
            time.sleep(10)
            wait_time += 10
            # 最大待ち時間を超えた場合は通知を行い終了する
            if wait_time >= int(max_wait_time):
                #DiscordにWebhookを送信
                _ = send_webhook(f'インスタンスが{max_wait_time}秒以内に起動しませんでした。')
                return success

    #DiscordにWebhookを送信
    _ = send_webhook('インスタンスが起動しました')
    return success

# ec2インスタンスの起動を確認する
def check_instance_state(ec2):
    instance = ec2.describe_instances(InstanceIds=[instance_id])
    state = instance['Reservations'][0]['Instances'][0]['State']['Name']
    return state

# DiscordにWebhookを送信
def send_webhook(content):
    data = {'content': content}
    result = requests.post(webhook_url, json=data)
    return result