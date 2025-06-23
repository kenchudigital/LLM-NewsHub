# For Deployment Instruction

```bash
docker login --username=your_alibaba_cloud_username registry.cn-hangzhou.aliyuncs.com
docker tag newsense-backend registry.cn-hangzhou.aliyuncs.com/fyp-newsense/newsense-backend:latest
docker push registry.cn-hangzhou.aliyuncs.com/fyp-newsense/newsense-backend:latest

docker tag newsense-frontend registry.cn-hangzhou.aliyuncs.com/fyp-newsense/newsense-frontend:latest
docker push registry.cn-hangzhou.aliyuncs.com/fyp-newsense/newsense-frontend:latest
```