#!/bin/bash

# Install and enable rsyslog
sudo yum install -y rsyslog
sudo systemctl enable rsyslog
sudo systemctl start rsyslog

# Install CloudWatch agent
sudo dnf install -y amazon-cloudwatch-agent
sudo yum install -y collectd
# *** CLOUDWATCH CONFIGURATION FILE ***
sudo cat <<"EOF" > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
{
        "agent": {
                "metrics_collection_interval": 60,
                "run_as_user": "root"
        },
        "logs": {
                "logs_collected": {
                        "files": {
                                "collect_list": [
                                        {
                                                "file_path": "/var/log/messages",
                                                "log_group_class": "STANDARD",
                                                "log_group_name": "/minecraft/messages",
                                                "log_stream_name": "{instance_id}",
                                                "retention_in_days": -1
                                        },
                                        {
                                                "file_path": "/opt/minecraft/server/logs/latest.log",
                                                "log_group_class": "STANDARD",
                                                "log_group_name": "/minecraft/server/logs",
                                                "log_stream_name": "{instance_id}",
                                                "retention_in_days": -1
                                        }
                                ]
                        }
                }
        },
        "metrics": {
                "aggregation_dimensions": [
                        [
                                "InstanceId"
                        ]
                ],
                "append_dimensions": {
                        "AutoScalingGroupName": "${aws:AutoScalingGroupName}",
                        "ImageId": "${aws:ImageId}",
                        "InstanceId": "${aws:InstanceId}",
                        "InstanceType": "${aws:InstanceType}"
                },
                "metrics_collected": {
                        "collectd": {
                                "metrics_aggregation_interval": 60
                        },
                        "disk": {
                                "measurement": [
                                        "used_percent"
                                ],
                                "metrics_collection_interval": 60,
                                "resources": [
                                        "*"
                                ]
                        },
                        "mem": {
                                "measurement": [
                                        "mem_used_percent"
                                ],
                                "metrics_collection_interval": 60
                        },
                        "statsd": {
                                "metrics_aggregation_interval": 60,
                                "metrics_collection_interval": 60,
                                "service_address": ":8125"
                        }
                }
        }
}
EOF

sudo systemctl enable amazon-cloudwatch-agent
sudo systemctl start amazon-cloudwatch-agent


# *** INSERT SERVER DOWNLOAD URL BELOW ***
# Do not add any spaces between your link and the "=", otherwise it won't work. EG: MINECRAFTSERVERURL=https://urlexample


MINECRAFTSERVERURL=


# Download Java
sudo yum install -y java-17-amazon-corretto-headless
# Install MC Java server in a directory we create
adduser minecraft
mkdir /opt/minecraft/
mkdir /opt/minecraft/server/
cd /opt/minecraft/server

# Download server jar file from Minecraft official website
wget $MINECRAFTSERVERURL

# Generate Minecraft server files and create script
java -Xmx1300M -Xms1300M -jar server.jar nogui
sleep 40
sed -i 's/false/true/p' eula.txt
touch start
# Tune java heap size to fit your needs.
printf '#!/bin/bash\njava -Xmx3G -Xms3G -jar server.jar nogui\n' >> start
chmod +x start
sleep 1
touch stop
printf '#!/bin/bash\nkill -9 $(ps -ef | pgrep -f "java")' >> stop
chmod +x stop
sleep 1
chown -R minecraft:minecraft /opt/minecraft/

# Create SystemD Script to run Minecraft server jar on reboot
cd /etc/systemd/system/
touch minecraft.service
printf '[Unit]\nDescription=Minecraft Server on start up\nWants=network-online.target\n[Service]\nUser=minecraft\nWorkingDirectory=/opt/minecraft/server\nExecStart=/opt/minecraft/server/start\nStandardInput=null\n[Install]\nWantedBy=multi-user.target' >> minecraft.service
sudo systemctl daemon-reload
sudo systemctl enable minecraft.service
sudo systemctl start minecraft.service

# End script