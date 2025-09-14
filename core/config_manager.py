# core/config_manager.py
"""
Ce module fournit des fonctions utilitaires pour gérer la lecture et l'écriture
du fichier de configuration de l'application (config.json).

La configuration est utilisée pour sauvegarder les réglages de l'utilisateur,
tels que la sensibilité du microphone, le délai de pause, et les coordonnées
de la cible, afin qu'ils persistent entre les sessions.
"""

# Importations nécessaires
import json  # Pour manipuler les données au format JSON
from typing import Dict, Any, Optional  # Pour l'annotation de type
from constants import CONFIG_FILE  # Pour obtenir le nom du fichier de configuration

def save_config(config: Dict[str, Any]) -> None:
    """
    Sauvegarde un dictionnaire de configuration dans le fichier JSON.

    Args:
        config (Dict[str, Any]): Le dictionnaire de configuration complet.
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4) # indent=4 pour un fichier plus lisible
    except IOError as e:
        print(f"Erreur lors de la sauvegarde de la configuration : {e}")

def load_config() -> Optional[Dict[str, Any]]:
    """
    Charge la configuration depuis le fichier JSON.

    Returns:
        Optional[Dict[str, Any]]: Le dictionnaire de configuration s'il existe, sinon None.
    """
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None