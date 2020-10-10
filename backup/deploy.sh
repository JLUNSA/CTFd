#!/bin/bash

# Root check
if [[ $(id -u) -ne 0 ]]; then
    echo "请使用 root 用户运行本脚本" >&2
    exit 1
fi

# Config
if [ -z ${backup_path} ];then
    echo "无默认配置！使用同目录配置文件。"
    source ./backup.conf
fi

# Place at /usr/lib/systemd/system/
echo "存放配置文件"
exer="Environment=deploy_path=$deploy_path"
sed "8c $exer" backup.service > /etc/systemd/system/backup.service
cat backup.timer > /etc/systemd/system/backup.timer

# Run timer
echo "开始定时任务..."
systemctl start backup.timer
