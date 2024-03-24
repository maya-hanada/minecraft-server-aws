# 利用方法

## 全体の流れ

1. Lambdaを作成しレイヤーを設定する
2. コードをコピーする
3. ロールのポリシーを編集する
4. 環境変数を設定する

## 注意点

### 1. Lambdaを作成しレイヤーを設定する

- 任意のPythonランタイムやアーキテクチャを利用しても大丈夫ですが、対応したレイヤーの設定をお願いします。[KLayers](https://github.com/keithrozario/Klayers/tree/master)でrequestsライブラリが利用できるレイヤーを探してください。  

- Lambdaの一般設定のタイムアウトの設定を変更してください。数分あれば大丈夫です、そうしないとタイムアウトになります。

### 2. コードをコピーする

- discordへの通知が不要な場合は「send_webhook」関数の呼び出し部分をコメントアウトしてください。

### 3. ロールのポリシーを編集する

- ポリシーのjsonを参考にして、権限を追加します。最小権限にしたい場合は対象のリソースを条件に指定してください。

### 4. 環境変数を設定する

設定値と設定例です。  

mc_start（マイクラサーバの起動）

| 変数名        | 設定例                                     | 詳細                                    |
| ------------- | ------------------------------------------ | --------------------------------------- |
| INSTANCE_ID   | i-12996a4ed478csa7a                        | 起動を行いたいEC2インスタンスのIDを設定 |
| WEBHOOK_URL   | https&#58;//discord.com/api/webhooks/xxxxx | DiscordのWebhookURLを入力               |
| MAX_WAIT_TIME | 180                                        | EC2起動のタイムアウト時間を秒で設定     |

mc_stop（マイクラサーバの停止）

| 変数名        | 設定例                                     | 詳細                                              |
| ------------- | ------------------------------------------ | ------------------------------------------------- |
| INSTANCE_ID   | i-12996a4ed478csa7a                        | 停止を行いたいEC2インスタンスのIDを設定           |
| WEBHOOK_URL   | https&#58;//discord.com/api/webhooks/xxxxx | DiscordのWebhookURLを入力                         |
| LOG_PATH      | /opt/minecraft/server/logs/latest.log      | Minecraftログのファイルパスを指定                 |
| MAX_WAIT_TIME | 40                                         | Minecraftログの読み取りタイムアウト時間を秒で設定 |

## 参考サイト

- [ローコストで24時間MineCraftサーバーを実現する #AWS - Qiita](https://qiita.com/ekko/items/851fb0cc9eddb9680071)
- [ブラウザが自動でfavicon.icoを読み込むのを防ぐ | DailyHackOn デイリーハックオン](https://dailyhackon.com/other-favicon-error/)
- [【AWS】Lambdaの戻り値のHTMLがHTMLと認識しない](https://teratail.com/questions/284579)
- [【AWS】AWSマネジメントコンソールから、セッションマネージャーを使ってEC2に接続 - Techfirm Cloud Architect Blog](https://techblog.techfirm.co.jp/entry/aws-ssm-ec2-access-from-aws-console)
- [SSM - Boto3 1.34.69 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html)
