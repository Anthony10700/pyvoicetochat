# core/voice_recognizer.py
"""
Ce module contient le thread de travail pour la reconnaissance vocale en continu.
Il gère l'écoute du microphone, la communication avec l'API de reconnaissance
vocale de Google et la transmission du texte reconnu.
"""

# Importations nécessaires
import threading  # Pour créer et gérer le thread
import speech_recognition as sr  # Bibliothèque principale pour la reconnaissance vocale
from utils.signals import WorkerSignals  # Signaux pour communiquer avec l'UI
from constants import PHRASE_TIME_LIMIT_SECONDS  # Constantes de configuration


class VoiceRecognizerThread(threading.Thread):
    """
    Un thread qui écoute le microphone en continu et utilise une API (Google)
    pour transcrire la parole en texte.

    Il est conçu pour tourner en arrière-plan et communiquer avec l'interface
    utilisateur de manière asynchrone via des signaux.

    Attributes:
        recognizer (sr.Recognizer): L'objet principal de reconnaissance vocale.
        device_index (int, optional): L'index du microphone à utiliser.
        signals (WorkerSignals): Instance pour émettre des signaux vers l'UI.
        _is_running (bool): Un drapeau pour contrôler la boucle d'écoute principale.
    """

    def __init__(self, energy_threshold: int, pause_threshold: float, device_index: int = None):
        """
        Initialise le thread de reconnaissance vocale.

        Args:
            energy_threshold (int): Le seuil de sensibilité. Les sons en dessous de
                                    cette valeur sont considérés comme du bruit.
            pause_threshold (float): Le temps de silence (en secondes) qui marque
                                     la fin d'une phrase.
            device_index (int, optional): L'index du microphone à utiliser.
        """
        # Appel du constructeur de la classe parente
        super().__init__()
        # Crée une instance de l'objet Recognizer
        self.recognizer = sr.Recognizer()

        # Le seuil d'énergie peut être ajusté dynamiquement par la bibliothèque
        self.recognizer.dynamic_energy_threshold = True
        # Définit le seuil de sensibilité initial
        self.recognizer.energy_threshold = energy_threshold
        # Définit la durée de silence considérée comme la fin d'une phrase
        self.recognizer.pause_threshold = pause_threshold

        # Stocke l'index du microphone
        self.device_index = device_index
        # Crée une instance de signaux pour la communication
        self.signals = WorkerSignals()
        # Initialise le drapeau de contrôle de la boucle à True
        self._is_running = True

    def stop(self) -> None:
        """
        Arrête la boucle d'écoute du thread de manière propre.
        """
        # Passe simplement le drapeau à False. La boucle `run` se terminera.
        self._is_running = False

    def run(self) -> None:
        """
        Méthode principale du thread. Démarre l'écoute et la reconnaissance.
        """
        # Ouvre le microphone en tant que ressource contextuelle
        with sr.Microphone(device_index=self.device_index) as source:
            # Émet un message pour indiquer que la calibration initiale (non-auto) commence
            self.signals.status_message.emit("Calibration audio...")
            # S'ajuste brièvement au bruit ambiant au démarrage
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)

            # Boucle principale : continue tant que `_is_running` est True
            while self._is_running:
                # Émet un message pour indiquer que l'application est prête à écouter
                self.signals.status_message.emit("En écoute...")

                try:
                    # `listen` bloque jusqu'à ce qu'une phrase soit détectée,
                    # en se basant sur `pause_threshold` et `phrase_time_limit`.
                    audio = self.recognizer.listen(source, phrase_time_limit=PHRASE_TIME_LIMIT_SECONDS)

                    # Une fois l'audio capturé, émet un message de statut
                    self.signals.status_message.emit("Reconnaissance en cours...")
                    # Envoie l'audio à l'API de Google pour la transcription
                    text = self.recognizer.recognize_google(audio, language='fr-FR')

                    # Si du texte a été reconnu avec succès...
                    if text:
                        # ...émet un signal avec le texte transcrit.
                        self.signals.recognized_text.emit(text)

                # Gère les erreurs attendues
                except sr.WaitTimeoutError:
                    # Si `listen` expire sans détecter de parole, continue simplement la boucle
                    continue
                except sr.UnknownValueError:
                    # Si l'API ne comprend pas l'audio, ignore et continue d'écouter
                    pass
                except sr.RequestError as e:
                    # Si une erreur d'API se produit (ex: pas de connexion internet),
                    # émet une erreur et arrête le thread.
                    self.signals.error_occurred.emit(f"Erreur API : {e}")
                    self.stop()