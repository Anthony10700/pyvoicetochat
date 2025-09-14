#!/bin/bash

# Ce script est conçu pour lancer l'application PyVoiceToChat de manière fiable.

# Se déplace dans le répertoire où se trouve le script.
# C'est une étape cruciale pour s'assurer que tous les chemins relatifs (comme pour l'icône) fonctionnent.
cd "$(dirname "$0")"

# Active l'environnement virtuel Python qui contient toutes les dépendances.
source .venv/bin/activate

# Lance l'application principale en utilisant l'interpréteur Python de l'environnement virtuel.
python main.py