from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

app = FastAPI(
    title="Virtual Cloud Phone Controller API",
    description="API de gestion et d'orchestration de téléphones virtuels Android",
    version="1.0.0"
)

# Modèles Pydantic pour la validation des requêtes
class TaskRequest(BaseModel):
    task_name: str = Field(..., example="account_creation", description="Nom du scénario à exécuter")
    target_app: str = Field(..., example="com.example.app", description="Package ou URL cible")
    phone_count: int = Field(default=1, ge=1, le=100, description="Nombre de téléphones virtuels à réquisitionner")
    payload: Optional[dict] = Field(default={}, description="Paramètres spécifiques pour la tâche")

class DeviceStatusResponse(BaseModel):
    device_id: str
    status: str
    assigned_task: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Virtual Cloud Phone API Gateway"}

@app.post("/tasks/dispatch", status_code=202)
def dispatch_task(task: TaskRequest):
    """
    Reçoit une instruction et le nombre de téléphones nécessaires,
    puis distribue la tâche dans la queue Redis / Celery.
    """
    logger.info(f"Ordre reçu: {task.task_name} sur {task.phone_count} téléphones.")
    
    # Génération d'un ID de batch pour suivre l'exécution
    batch_id = f"batch_{task.task_name}_{task.phone_count}"
    
    # TODO: Pousser les N sub-tasks dans Celery / Redis
    
    return {
        "status": "queued",
        "batch_id": batch_id,
        "task_name": task.task_name,
        "allocated_phones": task.phone_count,
        "message": f"Tâche diffusée avec succès à {task.phone_count} instances."
    }

@app.get("/devices", response_model=List[DeviceStatusResponse])
def list_devices():
    """
    Retourne la liste et l'état courant de la flotte de téléphones virtuels.
    """
    # Exemple de données simulées / à relier avec DeviceManager
    return [
        {"device_id": "127.0.0.1:5555", "status": "idle", "assigned_task": None},
        {"device_id": "127.0.0.1:5556", "status": "running", "assigned_task": "account_creation"}
    ]
