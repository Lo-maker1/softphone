from celery import Celery
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Worker")

# Configuration de Celery avec Redis comme Broker et Backend
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(name="execute_device_task")
def execute_device_task(device_id: str, task_name: str, payload: dict):
    """
    Exécute un scénario d'automatisation sur une instance spécifique.
    """
    logger.info(f"[{device_id}] Démarrage de la tâche '{task_name}'...")
    
    try:
        # Importer VirtualDevice localement pour éviter les imports circulaires
        from core.device import VirtualDevice
        
        device = VirtualDevice(device_id)
        
        if task_name == "install_and_open":
            apk_path = payload.get("apk_path")
            package_name = payload.get("package_name")
            
            if apk_path:
                device.install_apk(apk_path)
            if package_name:
                device.launch_app(package_name)
                
        elif task_name == "custom_click":
            x, y = payload.get("x", 0), payload.get("y", 0)
            device.tap(x, y)
            
        logger.info(f"[{device_id}] Tâche '{task_name}' terminée avec succès.")
        return {"status": "success", "device_id": device_id, "task": task_name}

    except Exception as e:
        logger.error(f"[{device_id}] Échec de la tâche '{task_name}': {str(e)}")
        return {"status": "failed", "device_id": device_id, "error": str(e)}
