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

# Stop timer
echo "停止定时任务..."
systemctl stop backup.timer

# Place at /usr/lib/systemd/system/
echo "删除配置文件"
rm -f /etc/systemd/system/backup.service
rm -f /etc/systemd/system/backup.timer
