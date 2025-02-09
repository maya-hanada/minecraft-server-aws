# 利用の注意点

## 前提

- Amazon Linux 2023のAMIを利用、アーキテクチャはt4gシリーズを利用するため64-bit(Arm)を選択しています。
- t4gシリーズでの実行を確認しています。t4g.medium以上を推奨します。基本的にはメモリが4GB以上あることが安定稼働に必要です。ap-northeast-1リージョンのメモリ4GB以上のインスタンスはt4g.mediumが最安値でした(2024/03/24時点)
- EC2インスタンスの立ち上げ初回に実行するユーザデータスクリプトとして提供しています。手動でユーザデータスクリプトのコマンドをサーバで実行しても同様に構築可能です。
- Modやプラグインを利用する前提にしているので、PaperMC(プラグイン)とMohistMC(Modとプラグイン両方)のユーザデータスクリプトを用意しています。

## IAM インスタンスプロフィールを作成して起動時にEC2に設定してください

必要な権限は以下の通りです。

- AmazonSSMManagedInstanceCore
- CloudWatchAgentAdminPolicy
- CloudWatchAgentServerPolicy

## MINECRAFTSERVERURLについて

### PaperMCバージョン(userdata_papermc.sh)の場合

最新のPaperMCが設定されます  
[こちら](https://zenn.dev/isksss/articles/373991b9377784)のサイトを参考にして、最新のPaperMCを取得するようにしました。

### MohistMC(userdata_mohist.sh)の場合

インストールしたいバージョンを「VERSION」変数に入れてください。  
[こちら](https://mohistmc.com/downloadSoftware?project=mohist)のサイトへアクセスして、最新バージョンを指定するなどしてください。

## 起動時のメモリサイズを調整してください

`java -Xmx3G -Xms3G -jar server.jar nogui`

[こちら](https://game.xserver.ne.jp/minecraft-media/memory-allocation/)のサイトを参考にしました。基本的にはシステム全体のメモリ量から1GBを引いた数字を設定するのがよさそうです。サーバでマインクラフト以外のアプリケーションも並行して実行する場合は調整をお願いします。  
t4g.mediumよりスペックの高いサーバを利用する場合はメモリ量にあった数字にしてください。

## CloudWatch Agentの設定を確認してください

デフォルトで取得されるCPU使用率等に加えて追加した項目は以下の通りです。

- メモリ使用量
- ディスク使用量
- マインクラフトサーバログ
- システムログ

※運用監視が必要無い場合はCloudWatchの権限や設定は不要なので該当箇所の削除をしてください。個人的にはログやリソース使用状況が見れた方が良いのでデフォルトで用意しています。

## 参考サイト

- [Setting up a Minecraft Java server on Amazon EC2](https://aws.amazon.com/jp/blogs/gametech/setting-up-a-minecraft-java-server-on-amazon-ec2/)
- [WinSCPでEC2に接続してみました。 - 協栄情報ブログ](https://cloud5.jp/winscp-ec2/)
- [【AWS】AWSマネジメントコンソールから、セッションマネージャーを使ってEC2に接続 - Techfirm Cloud Architect Blog](https://techblog.techfirm.co.jp/entry/aws-ssm-ec2-access-from-aws-console)
- [Amazon Linux 2023 のシステムログを CloudWatch Logs へ出力する方法 - サーバーワークスエンジニアブログ](https://blog.serverworks.co.jp/how-to-export-system-logs-of-amazon-linux-2023-to-cloudwatch-logs)
- [AWS EC2 起動テンプレートのユーザーデータを使用して Pytorch用 jupyter notebook の自動起動設定をする #AWS - Qiita](https://qiita.com/ground0state/items/09c43976b14ecef83d2a)
- [Amazon Linux 2023にCloudWatch agentをインストールしてカスタムメトリクスの設定をしてみる｜hiroyu0510](https://note.com/hiroyu0510/n/n0e6d19397218)
- [【マイクラ】サーバーのメモリ割り当てを最適化する方法 | ゼロから始めるマイクラサーバー運用ガイド](https://game.xserver.ne.jp/minecraft-media/memory-allocation/)
- [PaperMCの最新バージョンをダウンロードする](https://zenn.dev/isksss/articles/373991b9377784)
- [Install Mohist on Linux](https://mohistmc.com/mohist/docs/en-us/installation/linux)
