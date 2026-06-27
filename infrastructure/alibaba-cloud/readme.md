# Alibaba Cloud Deployment Notes

This folder records the cloud deployment exploration from the project development process. It is not required for the basic GitHub showcase demo.

The active local demo path is:

```bash
cd apps
docker compose up
```

Use the Alibaba Cloud script only if you want to build and push Docker images to your own Alibaba Cloud Container Registry.

## Environment Variables

Create a `.env` file in the project root based on `.env.example`, then provide your own registry values:

```bash
ALIYUN_USER=your-aliyun-account
ALIYUN_PASSWORD=your-aliyun-password-or-token
ALIYUN_REGISTRY=registry.example.com
ALIYUN_NAMESPACE=your-namespace
ALIYUN_BACKEND_IMAGE=newsense-backend
ALIYUN_FRONTEND_IMAGE=newsense-frontend
```

Do not commit real passwords, access tokens, registry usernames, or private image URLs.

## Build and Push

```bash
bash infrastructure/alibaba-cloud/execute.bash
```