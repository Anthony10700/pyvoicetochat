# ui/screen_overlay.py
"""
Ce module définit le widget de l'overlay qui s'affiche à l'écran pour
fournir un retour visuel à l'utilisateur.
"""

# Importations nécessaires
from PyQt6.QtWidgets import QWidget, QApplication  # Composants de base de l'interface
from PyQt6.QtCore import Qt  # Constantes et types de base de Qt
from PyQt6.QtGui import QPainter, QColor, QScreen  # Outils de dessin et d'information sur l'écran

# Constantes pour la taille et la position de l'indicateur
INDICATOR_SIZE = 25
INDICATOR_MARGIN = 10


class RecordingOverlay(QWidget):
    """
    Un widget overlay plein écran, mais entièrement transparent, dont le seul
    rôle est de dessiner un petit indicateur circulaire rouge en haut à gauche.

    Cette approche est robuste car l'overlay capture tout l'écran, garantissant
    qu'il peut dessiner par-dessus n'importe quelle autre application, tout en
    étant configuré pour laisser passer tous les clics de souris et les
    frappes de clavier.
    """

    def __init__(self):
        """Initialise l'overlay d'enregistrement."""
        # Appel du constructeur de la classe parente
        super().__init__()
        # Récupère la géométrie de l'écran principal (résolution, position)
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
        # Définit la géométrie du widget pour qu'elle corresponde à celle de l'écran
        self.setGeometry(screen_geometry)

        # Configuration des "flags" de la fenêtre. C'est l'étape la plus critique.
        self.setWindowFlags(
            # `SplashScreen` est un type de fenêtre conçu pour être au-dessus de tout.
            Qt.WindowType.SplashScreen |
            # Supprime la barre de titre et les bordures de la fenêtre.
            Qt.WindowType.FramelessWindowHint |
            # Garantit que la fenêtre reste au-dessus des autres.
            Qt.WindowType.WindowStaysOnTopHint |
            # Rend la fenêtre complètement transparente aux événements de la souris et du clavier.
            Qt.WindowType.WindowTransparentForInput
        )
        # Attributs supplémentaires pour la transparence et le comportement.
        # Active le fond transparent.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # Empêche la fenêtre de prendre le focus lorsqu'elle est affichée.
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

    def paintEvent(self, event) -> None:
        """
        Méthode appelée automatiquement chaque fois que le widget a besoin d'être redessiné.
        """
        # Crée un objet QPainter pour dessiner sur ce widget
        painter = QPainter(self)
        # Active l'antialiasing pour avoir un cercle aux bords lisses
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Définit la couleur de remplissage à rouge
        painter.setBrush(QColor("red"))
        # Indique qu'il ne faut pas dessiner de contour
        painter.setPen(Qt.PenStyle.NoPen)
        # Dessine une ellipse (un cercle) dans le coin supérieur gauche,
        # en utilisant les constantes de taille et de marge.
        painter.drawEllipse(INDICATOR_MARGIN, INDICATOR_MARGIN, INDICATOR_SIZE, INDICATOR_SIZE)