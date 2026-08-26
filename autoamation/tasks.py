import time
import logging
from core.device import VirtualDevice

logging.basicConfig(level=logging.INFO)

def run_signup_flow(device_id: str, email: str, username: str):
    """
    Exemple de scénario automatisé pour remplir un formulaire d'inscription.
    """
    device = VirtualDevice(device_id)
    logging.info(f"[{device_id}] Lancement du scénario d'inscription...")

    # 1. Retour à l'écran d'accueil
    device.press_home()
    time.sleep(1)

    # 2. Tap sur le champ 'Email' (coordonnées fictives à adapter au layout)
    device.tap(x=300, y=500)
    time.sleep(0.5)
    device.type_text(email)

    # 3. Tap sur le champ 'Nom d'utilisateur'
    device.tap(x=300, y=600)
    time.sleep(0.5)
    device.type_text(username)

    # 4. Tap sur le bouton 'Valider'
    device.tap(x=300, y=750)
    logging.info(f"[{device_id}] Inscription soumise pour {username}.")
