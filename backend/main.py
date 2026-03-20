"""
K8s Deployment Platform - FastAPI Backend
Mock Kubernetes deployment interface
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import yaml
import json
from datetime import datetime
import uuid

app = FastAPI(title="K8s Deployment Platform", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class DeploymentRequest(BaseModel):
    name: str
    image: str
    replicas: int = 1
    port: int = 8080
    cpu_request: str = "100m"
    memory_request: str = "128Mi"
    environment: Optional[dict] = None


class DeploymentResponse(BaseModel):
    id: str
    name: str
    image: str
    replicas: int
    status: str
    created_at: str
    pods: List[str]


class PodInfo(BaseModel):
    name: str
    status: str
    cpu_usage: str
    memory_usage: str
    restarts: int


# In-memory storage (replace with database in production)
deployments_db = {}
pods_db = {}


def generate_pod_names(deployment_name: str, count: int) -> list:
    """Generate pod names for deployment"""
    return [f"{deployment_name}-pod-{i}" for i in range(count)]


def generate_k8s_manifest(req: DeploymentRequest) -> str:
    """Generate Kubernetes deployment manifest"""
    manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": req.name,
            "labels": {"app": req.name}
        },
        "spec": {
            "replicas": req.replicas,
            "selector": {"matchLabels": {"app": req.name}},
            "template": {
                "metadata": {"labels": {"app": req.name}},
                "spec": {
                    "containers": [
                        {
                            "name": req.name,
                            "image": req.image,
                            "ports": [{"containerPort": req.port}],
                            "resources": {
                                "requests": {
                                    "cpu": req.cpu_request,
                                    "memory": req.memory_request,
                                }
                            },
                            "env": [
                                {"name": k, "value": str(v)}
                                for k, v in (req.environment or {}).items()
                            ]
                        }
                    ]
                }
            }
        }
    }
    return yaml.dump(manifest, default_flow_style=False)


@app.get("/")
async def root():
    return {
        "name": "K8s Deployment Platform",
        "version": "1.0.0",
        "endpoints": ["/deployments", "/manifests"]
    }


@app.post("/deployments", response_model=DeploymentResponse)
async def create_deployment(req: DeploymentRequest):
    """Create new deployment"""
    deployment_id = str(uuid.uuid4())[:8]
    
    # Generate pod names
    pod_names = generate_pod_names(req.name, req.replicas)
    
    # Create pods
    for pod_name in pod_names:
        pods_db[pod_name] = {
            "name": pod_name,
            "status": "Running",
            "cpu_usage": "50m",
            "memory_usage": "64Mi",
            "restarts": 0,
        }
    
    # Store deployment
    deployment = {
        "id": deployment_id,
        "name": req.name,
        "image": req.image,
        "replicas": req.replicas,
        "status": "Running",
        "created_at": datetime.now().isoformat(),
        "pods": pod_names,
        "config": req.dict()
    }
    
    deployments_db[deployment_id] = deployment
    
    return DeploymentResponse(
        id=deployment_id,
        name=req.name,
        image=req.image,
        replicas=req.replicas,
        status="Running",
        created_at=deployment["created_at"],
        pods=pod_names
    )


@app.get("/deployments")
async def list_deployments():
    """List all deployments"""
    return {
        "total": len(deployments_db),
        "deployments": [
            {
                "id": dep["id"],
                "name": dep["name"],
                "image": dep["image"],
                "replicas": dep["replicas"],
                "status": dep["status"],
                "created_at": dep["created_at"],
                "pod_count": len(dep["pods"])
            }
            for dep in deployments_db.values()
        ]
    }


@app.get("/deployments/{deployment_id}")
async def get_deployment(deployment_id: str):
    """Get deployment details"""
    if deployment_id not in deployments_db:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    dep = deployments_db[deployment_id]
    
    return {
        "id": dep["id"],
        "name": dep["name"],
        "image": dep["image"],
        "replicas": dep["replicas"],
        "status": dep["status"],
        "created_at": dep["created_at"],
        "pods": dep["pods"],
        "config": dep["config"]
    }


@app.get("/deployments/{deployment_id}/pods")
async def get_deployment_pods(deployment_id: str):
    """Get pods for deployment"""
    if deployment_id not in deployments_db:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    dep = deployments_db[deployment_id]
    pods = []
    
    for pod_name in dep["pods"]:
        if pod_name in pods_db:
            pods.append(pods_db[pod_name])
    
    return {"deployment_id": deployment_id, "pods": pods}


@app.post("/deployments/{deployment_id}/scale")
async def scale_deployment(deployment_id: str, replicas: int):
    """Scale deployment to new replica count"""
    if deployment_id not in deployments_db:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    dep = deployments_db[deployment_id]
    old_count = dep["replicas"]
    
    # Add or remove pods
    if replicas > old_count:
        for i in range(old_count, replicas):
            pod_name = f"{dep['name']}-pod-{i}"
            pods_db[pod_name] = {
                "name": pod_name,
                "status": "Running",
                "cpu_usage": "50m",
                "memory_usage": "64Mi",
                "restarts": 0,
            }
            dep["pods"].append(pod_name)
    else:
        for _ in range(replicas, old_count):
            if dep["pods"]:
                pod_name = dep["pods"].pop()
                pods_db.pop(pod_name, None)
    
    dep["replicas"] = replicas
    
    return {
        "deployment_id": deployment_id,
        "previous_replicas": old_count,
        "current_replicas": replicas,
        "status": "Scaling"
    }


@app.delete("/deployments/{deployment_id}")
async def delete_deployment(deployment_id: str):
    """Delete deployment"""
    if deployment_id not in deployments_db:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    dep = deployments_db.pop(deployment_id)
    
    # Delete pods
    for pod_name in dep["pods"]:
        pods_db.pop(pod_name, None)
    
    return {"message": "Deployment deleted", "deployment_id": deployment_id}


@app.get("/deployments/{deployment_id}/manifest")
async def get_manifest(deployment_id: str):
    """Get K8s manifest for deployment"""
    if deployment_id not in deployments_db:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    dep = deployments_db[deployment_id]
    manifest = generate_k8s_manifest(DeploymentRequest(**dep["config"]))
    
    return {"deployment_id": deployment_id, "manifest": manifest}


@app.post("/validate-manifest")
async def validate_manifest(manifest: str):
    """Validate K8s manifest YAML"""
    try:
        yaml.safe_load(manifest)
        return {"valid": True, "errors": []}
    except yaml.YAMLError as e:
        return {"valid": False, "errors": [str(e)]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
