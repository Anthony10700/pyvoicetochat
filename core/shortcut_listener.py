# core/shortcut_listener.py
"""
Ce module définit le thread qui écoute les raccourcis clavier de manière globale,
c'est-à-dire sur l'ensemble du système d'exploitation, même lorsque l'application
principale n'a pas le focus.
"""

# Importations nécessaires
import threading  # Pour créer et gérer le thread
from pynput import keyboard  # Pour écouter les frappes de clavier
from utils.signals import WorkerSignals
from constants import RECOGNITION_SHORTCUT_STR, DEFINE_TARGET_SHORTCUT_STR

def _format_shortcut_for_pynput(shortcut_str: str) -> str:
    """
    Formate une chaîne comme "Ctrl+Alt+V" en "<ctrl>+<alt>+v" pour pynput.
    Les touches de modification sont entourées de <>, mais pas les caractères simples.
    """
    parts = shortcut_str.lower().split('+')
    formatted_parts = []
    for part in parts:
        # Les touches de modification ou spéciales (ctrl, alt, f1...) ont une longueur > 1.
        # Les caractères simples (v, b...) ont une longueur de 1.
        if len(part) > 1:
            formatted_parts.append(f"<{part}>")
        else:
            formatted_parts.append(part)
    return '+'.join(formatted_parts)

class ShortcutListenerThread(threading.Thread):
    """
    Thread qui écoute les raccourcis clavier globaux en utilisant le système
    de "HotKeys" de pynput, plus robuste qu'un listener manuel.
    """

    def __init__(self):
        """Initialise le thread et ses signaux."""
        super().__init__()
        self.signals = WorkerSignals()
        self.listener = None  # Pour garder une référence et pouvoir l'arrêter

    def run(self) -> None:
        """Méthode principale du thread : configure et démarre l'écouteur de HotKeys."""
        try:
            # Formate les chaînes de raccourcis pour qu'elles soient compatibles avec GlobalHotKeys
            recognition_hotkey = _format_shortcut_for_pynput(RECOGNITION_SHORTCUT_STR)
            define_target_hotkey = _format_shortcut_for_pynput(DEFINE_TARGET_SHORTCUT_STR)

            # Définit les actions à déclencher pour chaque raccourci
            hotkeys = {
                recognition_hotkey: self._on_recognition_shortcut,
                define_target_hotkey: self._on_define_target_shortcut
            }

            # Crée et démarre le listener. Il s'exécutera jusqu'à l'appel de .stop()
            self.listener = keyboard.GlobalHotKeys(hotkeys)
            self.listener.start()
            self.listener.join()  # Bloque le thread jusqu'à la fin du listener
        except Exception as e:
            # Gère les erreurs potentielles si les raccourcis sont mal configurés
            print(f"Erreur dans le thread de raccourcis : {e}")

    def stop(self) -> None:
        """Arrête l'écoute des raccourcis clavier."""
        if self.listener:
            self.listener.stop()

    def _on_recognition_shortcut(self):
        """Callback pour le raccourci de reconnaissance : émet le signal approprié."""
        self.signals.start_recognition_shortcut.emit()

    def _on_define_target_shortcut(self):
        """Callback pour le raccourci de définition de cible : émet le signal approprié."""
        self.signals.define_target_shortcut.emit()