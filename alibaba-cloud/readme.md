# For Deployment Instruction

```bash
docker login --username= msp24053-registry.cn-hongkong.cr.aliyuncs.com --password-stdin
docker tag newsense-backend registry.cn-hangzhou.aliyuncs.com/fyp-newsense/newsense-backend:latest
docker push registry.cn-hangzhou.aliyuncs.com/fyp-newsense/newsense-backend:latest

msp24053-registry.cn-hongkong.cr.aliyuncs.com

docker tag newsense-frontend registry.cn-hangzhou.aliyuncs.com/fyp-newsense/newsense-frontend:latest
docker push registry.cn-hangzhou.aliyuncs.com/fyp-newsense/newsense-frontend:latest
```