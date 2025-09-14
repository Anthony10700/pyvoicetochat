# main.py
"""
Point d'entrée principal de l'application PyVoiceToChat.

Ce script est responsable de :
1.  S'assurer que l'icône de l'application existe.
2.  Initialiser l'application Qt.
3.  Créer et afficher la fenêtre principale de l'application.
4.  Lancer la boucle d'événements de l'application.
"""
import sys
import os
import base64
from PyQt6.QtWidgets import QApplication
from ui.main_window import VoiceToChatApp
from constants import ICON_FILE


def main():
    """
    Fonction principale qui initialise et lance l'application.
    """
    app = QApplication(sys.argv)
    window = VoiceToChatApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()