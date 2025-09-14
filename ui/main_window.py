# ui/main_window.py
"""
Ce module définit la classe `VoiceToChatApp`, qui est la fenêtre principale
de l'application et le cœur de l'orchestration de toutes les fonctionnalités.
"""

# Importations des bibliothèques externes et de l'interface graphique
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLabel, QMessageBox, QSystemTrayIcon, QMenu, QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QTimer, QEvent
from PyQt6.QtGui import QIcon, QAction
from pynput import mouse
# NOUVELLE IMPORTATION : Le contrôleur de clavier de pynput, plus fiable pour la frappe
from pynput.keyboard import Controller as KeyboardController
import pyautogui
import unicodedata
import re

# Importations des modules internes du projet
from ui.screen_overlay import RecordingOverlay
from core.voice_recognizer import VoiceRecognizerThread
from core.shortcut_listener import ShortcutListenerThread
from core.calibration import CalibrationThread
from core import config_manager
from utils.signals import WorkerSignals
from constants import (RECOGNITION_SHORTCUT_STR, DEFINE_TARGET_SHORTCUT_STR,
                       ICON_FILE, DEFAULT_ENERGY_THRESHOLD, DEFAULT_PAUSE_THRESHOLD, KEYWORD_ACTIONS)


class VoiceToChatApp(QWidget):
    """
    La fenêtre principale de l'application.

    Cette classe gère l'interface utilisateur, l'état de l'application (écoute ou non),
    le lancement des threads de travail (reconnaissance, calibrage, raccourcis),
    et la connexion de tous les signaux et slots pour faire fonctionner l'ensemble.
    """

    def __init__(self):
        """Initialise la fenêtre principale, ses composants et ses états."""
        super().__init__()

        # --- NOUVEAU : Initialisation du contrôleur de clavier pynput ---
        self.keyboard_controller = KeyboardController()

        # --- Initialisation des attributs d'état ---
        self.is_listening = False  # Drapeau pour savoir si la reconnaissance est active
        self.last_typed_text = ""  # Mémoire de la dernière phrase tapée (pour suppression)
        self.recognizer_thread = None  # Placeholder pour le thread de reconnaissance
        self.calibration_thread = None  # Placeholder pour le thread de calibrage
        self.microphone_device_index = None  # Pour une future sélection de micro

        # Dictionnaire de configuration, initialisé avec des valeurs par défaut
        self.config = {
            "target": None,
            "settings": {
                "energy_threshold": DEFAULT_ENERGY_THRESHOLD,
                "pause_threshold": DEFAULT_PAUSE_THRESHOLD
            }
        }

        # --- Initialisation des objets UI et de communication ---
        self.recording_overlay = RecordingOverlay()  # Crée l'overlay visuel
        self.mouse_signals = WorkerSignals()  # Crée un bus de signaux pour la souris

        # --- Lancement des séquences d'initialisation ---
        self._load_saved_config()      # Charge la configuration depuis config.json
        self._init_ui()                # Construit l'interface utilisateur
        self._init_tray_icon()         # Crée l'icône dans la barre des tâches
        self._connect_signals()        # Connecte tous les signaux (clics, etc.)
        self._start_shortcut_listener()# Lance l'écoute des raccourcis clavier

    def _init_ui(self) -> None:
        """Crée et configure tous les widgets de l'interface utilisateur."""
        self.setWindowTitle("PyVoiceToChat")
        self.setWindowIcon(QIcon(ICON_FILE))
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        self.status_label = QLabel("Prêt à l'emploi.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toggle_button = QPushButton(f"Démarrer Reconnaissance ({RECOGNITION_SHORTCUT_STR})")
        self.define_target_button = QPushButton(f"Définir la Cible ({DEFINE_TARGET_SHORTCUT_STR})")
        self.target_coords_label = QLabel("Cible non définie.")
        if self.config["target"]:
            x, y = self.config["target"]['x'], self.config["target"]['y']
            self.target_coords_label.setText(f"Cible chargée : X={x}, Y={y}")

        energy_layout = QHBoxLayout()
        energy_label = QLabel("Sensibilité du microphone :")
        self.energy_spinbox = QSpinBox()
        self.energy_spinbox.setToolTip("Augmentez si votre voix n'est pas détectée.\nDiminuez si le bruit de fond déclenche la reconnaissance.")
        self.energy_spinbox.setRange(500, 10000)
        self.energy_spinbox.setSingleStep(100)
        self.energy_spinbox.setValue(self.config["settings"]["energy_threshold"])
        self.calibrate_button = QPushButton("Calibrage Auto")
        self.calibrate_button.setToolTip("Ajuste automatiquement la sensibilité en fonction du bruit ambiant.")
        energy_layout.addWidget(energy_label)
        energy_layout.addWidget(self.energy_spinbox)
        energy_layout.addWidget(self.calibrate_button)

        pause_layout = QHBoxLayout()
        pause_label = QLabel("Délai de phrase (s) :")
        self.pause_spinbox = QDoubleSpinBox()
        self.pause_spinbox.setToolTip("Valeur basse (< 0.8) pour un effet 'live' rapide.\nValeur haute (> 1.0) pour des phrases complètes et précises.")
        self.pause_spinbox.setRange(0.3, 3.0)
        self.pause_spinbox.setSingleStep(0.1)
        self.pause_spinbox.setValue(self.config["settings"]["pause_threshold"])
        pause_layout.addWidget(pause_label)
        pause_layout.addWidget(self.pause_spinbox)

        layout.addWidget(self.status_label)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.define_target_button)
        layout.addWidget(self.target_coords_label)
        layout.addLayout(energy_layout)
        layout.addLayout(pause_layout)
        self.setLayout(layout)

    def _init_tray_icon(self) -> None:
        """Crée et configure l'icône de l'application dans la barre des tâches."""
        self.tray_icon = QSystemTrayIcon(QIcon(ICON_FILE), self)
        tray_menu = QMenu()
        show_action = QAction("Afficher", self)
        show_action.triggered.connect(self.showNormal)
        tray_menu.addAction(show_action)
        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def _connect_signals(self) -> None:
        """Connecte tous les signaux des widgets à leurs slots (méthodes) respectifs."""
        self.toggle_button.clicked.connect(self.toggle_recognition)
        self.define_target_button.clicked.connect(self.define_target_position)
        self.mouse_signals.target_defined.connect(self.on_target_defined)
        self.energy_spinbox.valueChanged.connect(self.on_settings_changed)
        self.pause_spinbox.valueChanged.connect(self.on_settings_changed)
        self.calibrate_button.clicked.connect(self.run_auto_calibration)
        QApplication.instance().aboutToQuit.connect(self._cleanup_on_quit)

    def _load_saved_config(self) -> None:
        """Charge la configuration depuis config.json et met à jour l'état de l'app."""
        loaded_config = config_manager.load_config()
        if loaded_config:
            self.config = loaded_config
        self.config.setdefault("target", None)
        self.config.setdefault("settings", {}).setdefault("energy_threshold", DEFAULT_ENERGY_THRESHOLD)
        self.config["settings"].setdefault("pause_threshold", DEFAULT_PAUSE_THRESHOLD)

    def on_settings_changed(self) -> None:
        """Slot appelé quand un réglage est modifié dans l'UI. Sauvegarde la config."""
        self.config["settings"]["energy_threshold"] = self.energy_spinbox.value()
        self.config["settings"]["pause_threshold"] = self.pause_spinbox.value()
        config_manager.save_config(self.config)
        self.status_label.setText("Réglages sauvegardés.")

    def run_auto_calibration(self):
        """Lance le processus de calibration automatique dans un thread séparé."""
        self.toggle_button.setEnabled(False)
        self.define_target_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)
        self.status_label.setText("Veuillez rester silencieux pendant 2 secondes...")
        self.calibration_thread = CalibrationThread(device_index=self.microphone_device_index)
        self.calibration_thread.signals.calibration_complete.connect(self.on_calibration_finished)
        self.calibration_thread.signals.error_occurred.connect(self.on_error_occurred)
        self.calibration_thread.start()

    def on_calibration_finished(self, energy_threshold: int):
        """Slot appelé lorsque la calibration est terminée avec succès."""
        self.status_label.setText(f"Calibration terminée ! Sensibilité réglée sur {energy_threshold}.")
        self.energy_spinbox.setValue(energy_threshold)
        self.toggle_button.setEnabled(True)
        self.define_target_button.setEnabled(True)
        self.calibrate_button.setEnabled(True)

    def start_recognition(self) -> None:
        """Démarre une session de reconnaissance vocale."""
        if not self.config["target"]:
            QMessageBox.warning(self, "Cible requise", "Veuillez d'abord définir une cible.")
            return
        if self.recognizer_thread and self.recognizer_thread.is_alive():
            return
        try:
            pyautogui.click(self.config["target"]['x'], self.config["target"]['y'])
        except Exception as e:
            QMessageBox.critical(self, "Erreur PyAutoGUI", f"Impossible de cliquer sur la cible : {e}")
            return
        self.is_listening = True
        self.update_ui_for_listening_state()
        energy = self.config["settings"]["energy_threshold"]
        pause = self.config["settings"]["pause_threshold"]
        self.recognizer_thread = VoiceRecognizerThread(
            energy_threshold=energy,
            pause_threshold=pause,
            device_index=self.microphone_device_index
        )
        self.recognizer_thread.signals.recognized_text.connect(self.on_recognized_text)
        self.recognizer_thread.signals.error_occurred.connect(self.on_error_occurred)
        self.recognizer_thread.signals.status_message.connect(self.on_status_message)
        self.recognizer_thread.start()

    def on_recognized_text(self, text: str) -> None:
        """Slot appelé quand du texte a été reconnu. Le traite et le tape."""
        if not self.config["target"]:
            return

        try:
            # Nettoie le texte reçu
            processed_text = text.lower().strip()
            # Remplace le symbole '&' par le mot 'et'
            processed_text = processed_text.replace('&', 'et')
            actions_to_perform = None

            # Cherche un mot-clé dans le texte
            for keyword, actions in KEYWORD_ACTIONS.items():
                if keyword in processed_text:
                    processed_text = processed_text.replace(keyword, "").strip()
                    actions_to_perform = actions
                    break

            # Gère l'action spéciale "supprimer phrase"
            if actions_to_perform == ["DELETE_LAST_PHRASE"]:
                if self.last_typed_text:
                    # On utilise pyautogui ici car il est fiable pour presser une touche unique
                    pyautogui.press('backspace', presses=len(self.last_typed_text), interval=0.05)
                    self.last_typed_text = ""
                return

            if processed_text:
                # --- Conversion des mots-nombres en chiffres ---
                number_words = {
                    "zéro": "0", "un": "1", "deux": "2", "trois": "3", "quatre": "4",
                    "cinq": "5", "six": "6", "sept": "7", "huit": "8", "neuf": "9"
                }
                for word, digit in number_words.items():
                    processed_text = re.sub(r'\b' + word + r'\b', digit, processed_text)

                text_to_type = processed_text + " "

                # --- Conversion des accents ---
                nfkd_form = unicodedata.normalize('NFD', text_to_type)
                ascii_text = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')

                # --- MODIFICATION MAJEURE : Utilisation de pynput pour une frappe fiable ---
                # Le contrôleur de pynput gère bien mieux les layouts de clavier (AZERTY, etc.)
                self.keyboard_controller.type(ascii_text)

                # Mémorise le texte qui a été réellement tapé pour la suppression
                self.last_typed_text = ascii_text
            else:
                self.last_typed_text = ""

            # Les actions (raccourcis, etc.) sont toujours gérées par pyautogui
            if actions_to_perform:
                for action in actions_to_perform:
                    if isinstance(action, list):
                        pyautogui.hotkey(*action)
                    else:
                        pyautogui.press(action)

        except Exception as e:
            QMessageBox.critical(self, "Erreur de saisie automatique", f"Impossible de traiter le texte reconnu : {e}")

    def _start_shortcut_listener(self) -> None:
        """Initialise et démarre le thread d'écoute des raccourcis clavier."""
        self.shortcut_listener = ShortcutListenerThread()
        self.shortcut_listener.signals.start_recognition_shortcut.connect(self.toggle_recognition)
        self.shortcut_listener.signals.define_target_shortcut.connect(self.define_target_position)
        self.shortcut_listener.daemon = True
        self.shortcut_listener.start()

    def toggle_recognition(self) -> None:
        """Bascule l'état de la reconnaissance (marche/arrêt)."""
        if self.is_listening:
            self.stop_recognition()
        else:
            self.start_recognition()

    def stop_recognition(self) -> None:
        """Arrête proprement la session de reconnaissance vocale."""
        if self.recognizer_thread and self.recognizer_thread.is_alive():
            self.recognizer_thread.stop()
            self.recognizer_thread.join(timeout=1.0)
        self.is_listening = False
        self.update_ui_for_listening_state()

    def update_ui_for_listening_state(self) -> None:
        """Met à jour l'interface (boutons, overlay) en fonction de l'état d'écoute."""
        if self.is_listening:
            self.toggle_button.setText(f"Arrêter Reconnaissance ({RECOGNITION_SHORTCUT_STR})")
            self.recording_overlay.show()
            self.status_label.setText("Démarrage de l'écoute...")
        else:
            self.toggle_button.setText(f"Démarrer Reconnaissance ({RECOGNITION_SHORTCUT_STR})")
            self.recording_overlay.hide()
            QApplication.restoreOverrideCursor()
            self.status_label.setText("Prêt. Écoute arrêtée.")

    def on_error_occurred(self, message: str) -> None:
        """Slot pour afficher les erreurs venant des threads."""
        self.status_label.setText(f"Info : {message}")
        if "Erreur API" in message:
            self.is_listening = False
            self.update_ui_for_listening_state()

    def on_status_message(self, message: str) -> None:
        """Slot pour afficher les messages de statut des threads."""
        self.status_label.setText(message)
        if "Reconnaissance en cours..." in message and self.is_listening:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        else:
            QApplication.restoreOverrideCursor()

    def define_target_position(self) -> None:
        """Lance le processus de sélection de la cible à l'écran."""
        if self.is_listening:
            self.status_label.setText("Veuillez d'abord arrêter l'écoute.")
            return
        self.status_label.setText("Veuillez cliquer sur la zone de texte cible...")
        self.showMinimized()
        QTimer.singleShot(200, self._begin_target_selection)

    def _begin_target_selection(self) -> None:
        """Change le curseur et démarre l'écouteur de souris."""
        QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)
        listener = mouse.Listener(on_click=self._on_mouse_click)
        listener.start()

    def _on_mouse_click(self, x: int, y: int, _button, pressed: bool) -> bool:
        """Callback appelé lors d'un clic de souris pendant la sélection."""
        if pressed:
            self.mouse_signals.target_defined.emit(x, y)
            return False
        return True

    def on_target_defined(self, x: int, y: int) -> None:
        """Slot appelé une fois la cible définie. Sauvegarde les coordonnées."""
        QApplication.restoreOverrideCursor()
        self.config["target"] = {'x': x, 'y': y}
        config_manager.save_config(self.config)
        self.target_coords_label.setText(f"Cible définie en X={x}, Y={y}")
        self.status_label.setText("Cible définie. Prêt.")
        self.showNormal()
        self.activateWindow()

    def changeEvent(self, event: QEvent) -> None:
        """Surveille les changements d'état de la fenêtre pour forcer l'overlay à rester visible."""
        if event.type() == QEvent.Type.WindowStateChange and self.is_listening:
            if self.windowState() == Qt.WindowState.WindowMinimized:
                QTimer.singleShot(100, self.recording_overlay.show)
        super().changeEvent(event)

    def _cleanup_on_quit(self) -> None:
        """Méthode de nettoyage appelée juste avant la fermeture de l'application."""
        self.stop_recognition()
        # NOUVEAU : Arrêter proprement l'écouteur de raccourcis.
        # C'est l'étape cruciale pour que le processus se termine.
        if self.shortcut_listener and self.shortcut_listener.is_alive():
            self.shortcut_listener.stop()

    def closeEvent(self, event) -> None:
        """Intercepte l'événement de fermeture de la fenêtre (clic sur la croix)."""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Application Réduite",
            "PyVoiceToChat est toujours actif. Cliquez droit sur l'icône pour quitter.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )