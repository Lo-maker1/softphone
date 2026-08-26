import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class VirtualDevice:
    """Classe pour interagir avec une instance Android via ADB."""

    def __init__(self, device_id: str):
        """
        :param device_id: Identifiant de l'appareil (ex: '127.0.0.1:5555' ou 'emulator-5554')
        """
        self.device_id = device_id

    def _run_adb(self, command: list[str]) -> str:
        """Exécute une commande ADB pour cet appareil spécifique."""
        full_command = ["adb", "-s", self.device_id] + command
        try:
            result = subprocess.run(
                full_command, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logging.error(f"Erreur ADB [{self.device_id}] : {e.stderr.strip()}")
            raise e

    def is_connected(self) -> bool:
        """Vérifie si l'appareil est en ligne et accessible."""
        try:
            state = self._run_adb(["get-state"])
            return state == "device"
        except Exception:
            return False

    def install_apk(self, apk_path: str) -> bool:
        """Installe un fichier APK sur le téléphone virtuel."""
        logging.info(f"Installation de {apk_path} sur {self.device_id}...")
        out = self._run_adb(["install", "-r", apk_path])
        return "Success" in out

    def tap(self, x: int, y: int):
        """Simule un clic aux coordonnées (X, Y)."""
        self._run_adb(["shell", "input", "tap", str(x), str(y)])

    def type_text(self, text: str):
        """Saisit du texte sur le champ actif (remplace les espaces par %s pour ADB)."""
        formatted_text = text.replace(" ", "%s")
        self._run_adb(["shell", "input", "text", formatted_text])

    def press_home(self):
        """Appuie sur le bouton Home."""
        self._run_adb(["shell", "input", "keyevent", "KEYCODE_HOME"])

    def launch_app(self, package_name: str):
        """Lance une application via son nom de paquet."""
        self._run_adb(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])


if __name__ == "__main__":
    # Test basique de connexion
    DEVICE_ADDRESS = "127.0.0.1:5555"
    device = VirtualDevice(DEVICE_ADDRESS)

    if device.is_connected():
        logging.info(f"Appareil {DEVICE_ADDRESS} connecté avec succès.")
    else:
        logging.warning(f"Impossible de se connecter à {DEVICE_ADDRESS}. Vérifiez qu'une instance tourne.")
