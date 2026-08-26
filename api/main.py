from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
from workers.worker import execute_device_task
from core.manager import DeviceManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

app = FastAPI(
    title="Virtual Cloud Phone Controller API",
    description="API de gestion et d'orchestration de téléphones virtuels Android",
    version="1.0.0"
)

device_manager = DeviceManager()

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
    Reçoit une instruction, réserve N téléphones actifs et distribue
    les tâches asynchrones dans la file Celery / Redis.
    """
    logger.info(f"Ordre reçu: {task.task_name} sur {task.phone_count} téléphones.")
    
    # 1. Récupération des téléphones virtuels actuellement en ligne
    active_devices = device_manager.list_running_devices()
    
    if not active_devices:
        raise HTTPException(
            status_code=503, 
            detail="Aucun téléphone virtuel actif n'est disponible sur le serveur."
        )
    
    if len(active_devices) < task.phone_count:
        logger.warning(
            f"Demandé: {task.phone_count}, mais seulement {len(active_devices)} appareils disponibles."
        )
    
    # Sélection des N premiers téléphones disponibles
    selected_devices = active_devices[:task.phone_count]
    
    # 2. Construction de la charge utile (payload)
    task_payload = task.payload.copy()
    task_payload["target_app"] = task.target_app
    
    dispatched_tasks = []
    
    # 3. Envoi des sous-tâches asynchrones à la file Celery
    for dev in selected_devices:
        device_id = dev["device_id"]
        celery_job = execute_device_task.delay(
            device_id=device_id, 
            task_name=task.task_name, 
            payload=task_payload
        )
        dispatched_tasks.append({
            "device_id": device_id,
            "task_id": celery_job.id
        })
    
    return {
        "status": "queued",
        "task_name": task.task_name,
        "target_app": task.target_app,
        "requested_phones": task.phone_count,
        "allocated_phones": len(dispatched_tasks),
        "tasks": dispatched_tasks
    }

@app.get("/devices", response_model=List[DeviceStatusResponse])
def list_devices():
    """
    Retourne la liste et l'état courant de la flotte de téléphones virtuels.
    """
    devices = device_manager.list_running_devices()
    return [
        {
            "device_id": dev["device_id"], 
            "status": dev["status"], 
            "assigned_task": None
        }
        for dev in devices
    ]
