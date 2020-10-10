#!/bin/bash

#################
# WebDav 备份脚本
# 本脚本应该通过 systemd 启动
#################

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

# Pack
echo "开始打包..."
filename="$prefix"_"$(date +%y%m%d_%H%M%S).tar.gz"
cd "$tmpfs"
tar -czvf "$filename" "$backup_path" 1> /dev/null

if [ $? -eq 0 ]; then
     echo "打包完成...$filename，开始上传..."
else
     echo "打包失败...$filename" >&2
     rm $filename
     exit 1
fi

# Upload
curl -ss --user "$user:$pass" -T "$filename" "$srv"

if [ $? -eq 0 ]; then
     echo "上传完成...$filename"
else
     echo "上传失败...$filename" >&2
fi

rm $filename

# 删除多余备份
flist=$(curl -ss --user "$user:$pass" -X PROPFIND "$srv")
filter=$(echo $flist | grep -Po '<D:href>\/dav\/\K(.+?)(?=<\/D:href>)' -o | grep $prefix | sort)
echo $filter
bk_count=$(echo $filter | wc -w)

if [ $bk_count -gt $keeps ];then
    del_count=`expr $bk_count - $keeps`
    echo "当前共有 $bk_count 个备份文件，待删除 $del_count 个"
    # 删除文件
    del_lst=$(echo $filter | cut -d " " -f 1 | head -$del_count)
    for file in $del_lst; do
        echo "正在删除文件...$file"
        curl -ss --user "$user:$pass" -X DELETE "$srv$file"
        
        if [ $? -eq 0 ]; then
            echo "删除完成...$file"
        else
            echo "删除失败，请手动删除...$file" >&2
        fi
    done
else
    echo "当前共有 $bk_count 个备份文件，无需删除"
fi
