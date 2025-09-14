# constants.py
"""
Ce fichier centralise toutes les constantes et valeurs de configuration statiques
du projet. Cela facilite la modification des paramètres sans avoir à chercher
dans tout le code.
"""
# Importations nécessaires
from pynput import keyboard  # Pour définir les touches des raccourcis

# --- Configuration de la Reconnaissance Vocale ---
# Seuil de sensibilité initial. Sera ajusté par le calibrage.
DEFAULT_ENERGY_THRESHOLD: int = 4000
# Délai de silence (en secondes) considéré comme la fin d'une phrase.
DEFAULT_PAUSE_THRESHOLD: float = 0.8
# Durée maximale d'enregistrement (en secondes) pour une seule phrase.
PHRASE_TIME_LIMIT_SECONDS: int = 15


# --- Configuration des Fichiers ---
# Nom du fichier de configuration où les réglages sont sauvegardés.
CONFIG_FILE: str = "config.json"
# Nom du fichier d'icône de l'application.
ICON_FILE: str = "icon.png"


# --- Configuration des Raccourcis Clavier ---
# Ensemble des touches pour le raccourci qui démarre/arrête la reconnaissance.
RECOGNITION_SHORTCUT: set = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('v')}
# Ensemble des touches pour le raccourci qui lance la définition de la cible.
DEFINE_TARGET_SHORTCUT: set = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('b')}
# Représentation textuelle des raccourcis, affichée sur les boutons.
RECOGNITION_SHORTCUT_STR: str = "Ctrl+Alt+V"
DEFINE_TARGET_SHORTCUT_STR: str = "Ctrl+Alt+B"


# --- Configuration des Mots-Clés ---
# Dictionnaire associant une commande vocale (clé) à une liste d'actions à exécuter.
# - Une chaîne simple (ex: "enter") correspond à une pression de touche simple (`pyautogui.press`).
# - Une liste de chaînes (ex: ['ctrl', 'a']) correspond à un raccourci clavier (`pyautogui.hotkey`).
KEYWORD_ACTIONS: dict = {
    # Quand "envoyer" est détecté, appuie sur la touche Entrée.
    "envoyer": ["enter"],
    # Sélectionne tout (`Ctrl+A`) puis efface (`Backspace`).
    "supprimer tout": [['ctrl', 'a'], 'backspace'],
    # Action spéciale gérée par le code pour supprimer la dernière phrase dictée.
    "supprimer phrase": ["DELETE_LAST_PHRASE"],
}