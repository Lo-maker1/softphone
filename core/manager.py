import subprocess
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DeviceManager:
    """Gestionnaire du cycle de vie des conteneurs Android (Reddroid)."""

    def __init__(self, android_version: str = "11.0.0-latest"):
        self.android_image = f"reddoi/reddroid:{android_version}"

    def start_instance(self, instance_id: int, port: int) -> bool:
        """Démarre une nouvelle instance Reddroid dans Docker."""
        container_name = f"android_phone_{instance_id}"
        
        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--privileged",
            "-p", f"{port}:5555",
            self.android_image
        ]
        
        try:
            logging.info(f"Lancement de l'instance {container_name} sur le port {port}...")
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            # Connexion ADB immédiate au port hôte
            subprocess.run(["adb", "connect", f"localhost:{port}"], check=False)
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Erreur lors du démarrage de {container_name} : {e.stderr}")
            return False

    def stop_instance(self, instance_id: int) -> bool:
        """Arrête et supprime une instance Android."""
        container_name = f"android_phone_{instance_id}"
        try:
            logging.info(f"Arrêt de l'instance {container_name}...")
            subprocess.run(["docker", "stop", container_name], check=True, capture_output=True)
            subprocess.run(["docker", "rm", container_name], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Erreur lors de l'arrêt de {container_name} : {e.stderr}")
            return False

    def list_running_devices(self) -> List[Dict[str, str]]:
        """Retourne la liste des téléphones Android actifs connectés via ADB."""
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split("\n")[1:]
            devices = []
            for line in lines:
                if "\tdevice" in line:
                    device_id = line.split("\t")[0]
                    devices.append({"device_id": device_id, "status": "online"})
            return devices
        except subprocess.CalledProcessError as e:
            logging.error(f"Erreur lors de la récupération des appareils : {e.stderr}")
            return []


if __name__ == "__main__":
    manager = DeviceManager()
    print("Appareils actifs :", manager.list_running_devices())
