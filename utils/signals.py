# utils/signals.py
"""
Ce module centralise la définition de tous les signaux PyQt personnalisés
utilisés pour la communication entre les différents threads de l'application
(par exemple, entre les threads de travail et le thread principal de l'interface).

L'utilisation de signaux est le moyen le plus sûr et le plus propre de faire
communiquer des threads dans une application PyQt.
"""
# Importations nécessaires
from PyQt6.QtCore import QObject, pyqtSignal  # Classes de base pour les signaux/slots


class WorkerSignals(QObject):
    """
    Une collection de signaux pour la communication inter-threads.

    Hérite de QObject pour pouvoir définir des signaux. Une seule instance de
    cette classe est généralement créée dans chaque thread travailleur.
    """
    # Signal émis lorsqu'une phrase a été reconnue avec succès.
    # Le `str` indique que le signal transportera une chaîne de caractères.
    recognized_text = pyqtSignal(str)

    # Signal émis lorsqu'une erreur non bloquante se produit.
    error_occurred = pyqtSignal(str)

    # Signal pour envoyer des messages de statut à afficher dans l'UI.
    status_message = pyqtSignal(str)

    # Signal émis après qu'un utilisateur a cliqué pour définir une cible.
    # Transporte les coordonnées X et Y du clic.
    target_defined = pyqtSignal(int, int)

    # Signal émis par le ShortcutListener lorsque le raccourci de reconnaissance est pressé.
    start_recognition_shortcut = pyqtSignal()

    # Signal émis par le ShortcutListener lorsque le raccourci de définition de cible est pressé.
    define_target_shortcut = pyqtSignal()

    # Signal émis par le CalibrationThread lorsque le calibrage est terminé.
    # Transporte la valeur de sensibilité (seuil d'énergie) calculée.
    calibration_complete = pyqtSignal(int)