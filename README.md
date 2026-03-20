# K8s Deployment Platform

A Kubernetes deployment management platform with a modern UI for deploying, scaling, and managing containerized applications.

## Features

- ✅ **Deploy Applications** - Submit container images with resource specifications
- ✅ **Pod Management** - View and monitor running pods
- ✅ **Scaling** - Scale deployments up/down
- ✅ **Manifest Generation** - Auto-generate K8s YAML manifests
- ✅ **Resource Limits** - Set CPU and memory requests
- ✅ **Environment Variables** - Configure app environment
- ✅ **Status Monitoring** - Real-time deployment and pod status

## Tech Stack

- **Backend**: FastAPI with Kubernetes-style mock API
- **Frontend**: React + Vite
- **Deployment Format**: YAML (Kubernetes compliant)

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

Backend runs on: http://localhost:8002
API Docs: http://localhost:8002/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:3002

Visit: http://localhost:3002

## API Endpoints

### Create Deployment

```bash
POST /deployments
Content-Type: application/json

{
  "name": "my-app",
  "image": "nginx:latest",
  "replicas": 3,
  "port": 8080,
  "cpu_request": "100m",
  "memory_request": "128Mi",
  "environment": {
    "LOG_LEVEL": "info",
    "DATABASE_URL": "postgres://db:5432/app"
  }
}

Response: {
  "id": "abc12345",
  "name": "my-app",
  "image": "nginx:latest",
  "replicas": 3,
  "status": "Running",
  "created_at": "2024-01-15T10:30:45.123",
  "pods": ["my-app-pod-0", "my-app-pod-1", "my-app-pod-2"]
}
```

### List Deployments

```bash
GET /deployments

Response: {
  "total": 2,
  "deployments": [
    {
      "id": "abc12345",
      "name": "my-app",
      "image": "nginx:latest",
      "replicas": 3,
      "status": "Running",
      "created_at": "2024-01-15T10:30:45.123",
      "pod_count": 3
    }
  ]
}
```

### Get Deployment Details

```bash
GET /deployments/{deployment_id}

Response: {
  "id": "abc12345",
  "name": "my-app",
  "image": "nginx:latest",
  "replicas": 3,
  "status": "Running",
  "created_at": "2024-01-15T10:30:45.123",
  "pods": ["my-app-pod-0", "my-app-pod-1", "my-app-pod-2"],
  "config": { ... }
}
```

### Get Pods for Deployment

```bash
GET /deployments/{deployment_id}/pods

Response: {
  "deployment_id": "abc12345",
  "pods": [
    {
      "name": "my-app-pod-0",
      "status": "Running",
      "cpu_usage": "50m",
      "memory_usage": "64Mi",
      "restarts": 0
    }
  ]
}
```

### Scale Deployment

```bash
POST /deployments/{deployment_id}/scale
Content-Type: application/json

{ "replicas": 5 }

Response: {
  "deployment_id": "abc12345",
  "previous_replicas": 3,
  "current_replicas": 5,
  "status": "Scaling"
}
```

### Get K8s Manifest

```bash
GET /deployments/{deployment_id}/manifest

Response: {
  "deployment_id": "abc12345",
  "manifest": "apiVersion: apps/v1\nkind: Deployment\n..."
}
```

### Delete Deployment

```bash
DELETE /deployments/{deployment_id}

Response: {
  "message": "Deployment deleted",
  "deployment_id": "abc12345"
}
```

## Resource Specifications

| Field              | Example                 | Notes                     |
| ------------------ | ----------------------- | ------------------------- |
| **CPU Request**    | `100m`, `500m`, `1`     | Millicores; 1000m = 1 CPU |
| **Memory Request** | `128Mi`, `256Mi`, `1Gi` | MiB or GiB                |
| **Port**           | `8080`                  | Container port            |
| **Replicas**       | `1-10`                  | Number of pod copies      |

## Project Structure

```
k8s-deployment-platform-app/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile (optional)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
└── README.md
```

## How It Works

1. **Submit Deployment** - Fill form with app details, click Deploy
2. **Backend creates** - Generates K8s manifest, creates pods in-memory
3. **Dashboard updates** - Shows deployment and pod status
4. **Manage resources** - Scale, delete, view pod logs
5. **Generate YAML** - Export K8s manifest for actual cluster
6. **Export and deploy** - Copy YAML to `kubectl apply -f`

## Integration with Real K8s

To use with actual Kubernetes:

1. Get generated manifest from `/deployments/{id}/manifest`
2. Apply to cluster: `kubectl apply -f manifest.yaml`
3. Monitor with: `kubectl get deployments`, `kubectl get pods`

## Customization

### Add More Resource Types

Extend `DeploymentRequest` model to support:

- Services
- ConfigMaps
- Secrets
- Ingress
- StatefulSets

### Connect to Real K8s

Replace mock storage with actual Kubernetes client:

```python
from kubernetes import client, config
config.load_incluster_config()
v1 = client.AppsV1Api()
```

## Troubleshooting

**YAML manifest errors?**

- Check YAML syntax with `/validate-manifest` endpoint
- Enable verbose logging

**Deployments disappear?**

- They're stored in-memory; restart resets all deployments
- Add database persistence for production

## Future Enhancements

- [ ] Database persistence
- [ ] Real Kubernetes integration
- [ ] Helm chart generation
- [ ] Multi-cluster support
- [ ] Rolling updates
- [ ] Health checks & probes
- [ ] Network policies
- [ ] Persistent volumes

## License

MIT
