#!/bin/bash

# 載入 .env 檔案
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo ".env file not found! Please create one with ALIYUN_USER variable."
  exit 1
fi

# 登錄阿里雲容器鏡像服務
docker login --username=${ALIYUN_USER} registry.cn-hangzhou.aliyuncs.com --password=${ALIYUN_PASSWORD}

# 構建後端映像
cd apps/backend
docker build -t newsense-backend .

# 構建前端映像
cd ../frontend
docker build -t newsense-frontend .

# 回到專案根目錄
cd ../../..

# 標記映像
docker tag newsense-backend registry.cn-hangzhou.aliyuncs.com/fyp-demo/newsense-backend:latest
docker tag newsense-frontend registry.cn-hangzhou.aliyuncs.com/fyp-demo/newsense-frontend:latest

# 推送映像到阿里雲
docker push registry.cn-hangzhou.aliyuncs.com/fyp-demo/newsense-backend:latest
docker push registry.cn-hangzhou.aliyuncs.com/fyp-demo/newsense-frontend:latest

echo "All done! Images have been pushed to Alicloud."