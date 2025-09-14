# core/calibration.py
"""
Ce module contient le thread de travail pour le calibrage automatique
du microphone. Il est conçu pour fonctionner en arrière-plan afin de ne pas
geler l'interface utilisateur pendant l'analyse du bruit ambiant.
"""

# Importations nécessaires
import threading  # Pour créer et gérer le thread
import speech_recognition as sr  # Bibliothèque principale pour la reconnaissance vocale
from utils.signals import WorkerSignals  # Signaux personnalisés pour la communication inter-threads

# Définit un seuil de sensibilité minimal pour garantir que le calibrage
# ne produit pas de valeurs trop basses ou négatives, ce qui pourrait rendre
# la détection de la parole inefficace.
MIN_ENERGY_THRESHOLD = 500


class CalibrationThread(threading.Thread):
    """
    Un thread qui écoute le bruit ambiant pendant un court instant pour
    calculer et recommander un seuil de sensibilité (energy_threshold) optimal.

    Ce thread est essentiel pour permettre un calibrage non bloquant de l'UI.
    Il communique le résultat via des signaux PyQt.

    Attributes:
        device_index (int, optional): L'index du périphérique microphone à utiliser.
                                      Si None, le microphone par défaut est utilisé.
        signals (WorkerSignals): Un objet contenant les signaux PyQt pour
                                 communiquer avec le thread principal.
    """

    def __init__(self, device_index: int = None):
        """
        Initialise le thread de calibrage.

        Args:
            device_index (int, optional): L'index du microphone à utiliser.
                                          Laissé à None pour le système par défaut.
        """
        # Appel du constructeur de la classe parente (threading.Thread)
        super().__init__()
        # Stocke l'index du microphone pour une utilisation ultérieure
        self.device_index = device_index
        # Crée une instance de WorkerSignals pour pouvoir émettre des signaux
        self.signals = WorkerSignals()

    def run(self) -> None:
        """
        La méthode principale exécutée lors du démarrage du thread.

        Elle accède au microphone, écoute le bruit ambiant, calcule le seuil
        d'énergie, s'assure qu'il n'est pas trop bas, puis émet le résultat.
        """
        # Utilisation d'un bloc try...except pour capturer les erreurs potentielles
        # (par exemple, si aucun microphone n'est trouvé).
        try:
            # Crée une instance de l'objet Recognizer
            recognizer = sr.Recognizer()
            # Ouvre le microphone en tant que ressource contextuelle pour garantir sa fermeture
            with sr.Microphone(device_index=self.device_index) as source:
                # C'est la fonction clé : elle écoute le bruit ambiant pendant 2 secondes
                # et ajuste dynamiquement le `energy_threshold` du recognizer.
                recognizer.adjust_for_ambient_noise(source, duration=2)

                # Applique une sécurité : la valeur calculée ne doit pas être inférieure
                # à notre seuil minimal défini. `max` choisit la plus grande des deux valeurs.
                calibrated_threshold = max(recognizer.energy_threshold, MIN_ENERGY_THRESHOLD)

                # Émet un signal `calibration_complete` avec la valeur calculée et validée.
                # Ce signal sera capté par la fenêtre principale.
                self.signals.calibration_complete.emit(calibrated_threshold)
        # Si une erreur se produit pendant le processus...
        except Exception as e:
            # ...émet un signal `error_occurred` avec un message d'erreur descriptif.
            self.signals.error_occurred.emit(f"Erreur de calibration : {e}")