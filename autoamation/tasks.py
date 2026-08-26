import time
import logging
from core.device import VirtualDevice

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TaskExecutor:
    """Exécuteur de scénarios d'automatisation sur une instance Android."""

    def __init__(self, device_id: str):
        self.device = VirtualDevice(device_id)

    def run_signup_flow(self, email: str, username: str) -> bool:
        """
        Exécute le scénario d'inscription automatique sur un téléphone virtuel.
        """
        logging.info(f"[{self.device.device_id}] Lancement du scénario d'inscription pour {username}...")

        if not self.device.is_connected():
            logging.error(f"[{self.device.device_id}] Appareil non accessible via ADB.")
            return False

        try:
            # 1. Retour à l'écran d'accueil
            self.device.press_home()
            time.sleep(1)

            # 2. Tap sur le champ 'Email' et saisie
            logging.info(f"[{self.device.device_id}] Saisie de l'email : {email}")
            self.device.tap(x=300, y=500)
            time.sleep(0.5)
            self.device.type_text(email)

            # 3. Tap sur le champ 'Nom d'utilisateur' et saisie
            logging.info(f"[{self.device.device_id}] Saisie du username : {username}")
            self.device.tap(x=300, y=600)
            time.sleep(0.5)
            self.device.type_text(username)

            # 4. Tap sur le bouton de validation de l'interface
            logging.info(f"[{self.device.device_id}] Validation du formulaire...")
            self.device.tap(x=300, y=750)
            time.sleep(1)

            logging.info(f"[{self.device.device_id}] Inscription réussie pour {username}.")
            return True

        except Exception as e:
            logging.error(f"[{self.device.device_id}] Erreur lors de l'exécution du scénario : {e}")
            return False


def execute_scenario(device_id: str, task_name: str, payload: dict) -> bool:
    """
    Point d'entrée appelé par le worker Celery pour lancer le bon scénario selon la tâche.
    """
    executor = TaskExecutor(device_id)
    
    if task_name in ["signup_flow", "account_creation"]:
        email = payload.get("email", "default@example.com")
        username = payload.get("username", "default_user")
        return executor.run_signup_flow(email=email, username=username)
    else:
        logging.warning(f"[{device_id}] Tâche inconnue reçue : {task_name}")
        return False
