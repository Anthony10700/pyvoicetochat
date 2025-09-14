# PyVoiceToChat

**Dictez du texte et exécutez des commandes dans n'importe quelle application, simplement avec votre voix.**

PyVoiceToChat est un utilitaire léger et puissant qui tourne en arrière-plan pour vous permettre de transcrire votre voix en texte dans n'importe quel champ de texte sur votre ordinateur. Il vous suffit de définir une cible une seule fois, puis d'utiliser un raccourci clavier pour commencer à dicter.

L'application est conçue pour être discrète et efficace, avec des fonctionnalités avancées comme les commandes par mots-clés et le calibrage automatique du microphone pour s'adapter à votre environnement.

---

## Fonctionnalités Clés

- **Dictée Universelle** : Fonctionne avec n'importe quelle application, jeu ou champ de texte capable de recevoir une saisie clavier.
- **Définition de Cible Facile** : Cliquez simplement sur une zone de texte pour la définir comme la destination de votre dictée.
- **Raccourcis Clavier** : Activez/désactivez la reconnaissance vocale et définissez la cible avec des raccourcis clavier globaux (entièrement personnalisables).
- **Commandes par Mots-Clés** : Intégrez des actions à votre dictée. Dites "envoyer" pour appuyer sur `Entrée` ou "supprimer tout" pour effacer le contenu d'un champ.
- **Calibrage Automatique** : D'un simple clic, ajustez automatiquement la sensibilité du microphone au bruit ambiant de votre pièce pour une détection optimale.
- **Réglages Personnalisables** : Ajustez manuellement la sensibilité et le "délai de phrase" pour adapter l'application à votre rythme de parole.
- **Indicateur Visuel Discret** : Un petit cercle rouge s'affiche en haut à gauche de l'écran pour vous indiquer clairement quand l'application est en train d'écouter.
- **Conversion des Accents (ASCII)** : Pour garantir une compatibilité maximale avec toutes les applications, le texte dicté est automatiquement converti en caractères non accentués (ASCII). Par exemple, si vous dictez "ça a été un succès", le texte inséré sera "ca a ete un succes".

---

## Prérequis

- **Python 3.7+**
- Le gestionnaire de paquets `pip`

---

## Installation

1.  **Clonez ce dépôt sur votre machine locale :**
    ```bash
    git clone <url-du-depot>
    cd pyvoicetochat
    ```

2.  **Créez et activez un environnement virtuel (recommandé) :**
    - Sur Linux / macOS :
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```
    - Sur Windows :
      ```bash
      python -m venv .venv
      .\.venv\Scripts\activate
      ```

3.  **Installez les dépendances requises :**
    ```bash
    pip install -r requirements.txt
    ```
    *Note : L'installation de `PyAudio` peut nécessiter des dépendances supplémentaires sur certains systèmes. Veuillez consulter la documentation de PyAudio pour votre OS si vous rencontrez des problèmes.*

---

## Comment l'utiliser

1.  **Lancez l'application :**
    ```bash
    python main.py
    ```
    La fenêtre principale de l'application s'ouvrira.

2.  **Définissez la Cible :**
    - Cliquez sur le bouton **"Définir la Cible"** (ou utilisez le raccourci `Ctrl+Alt+B` par défaut).
    - La fenêtre se minimisera et votre curseur se transformera en croix.
    - Cliquez sur n'importe quel champ de texte à l'écran (une fenêtre de chat, un document Word, une barre de recherche, etc.).
    - La fenêtre principale réapparaîtra, confirmant que la cible a été définie.

3.  **Démarrez la Dictée :**
    - Cliquez sur le bouton **"Démarrer Reconnaissance"** (ou utilisez le raccourci `Ctrl+Alt+V` par défaut).
    - Un **cercle rouge** apparaîtra en haut à gauche de votre écran, indiquant que l'application est en mode écoute.

4.  **Parlez !**
    - Le texte que vous dictez sera automatiquement écrit dans le champ de texte cible.
    - Vous pouvez utiliser les mots-clés configurés (ex: "envoyer").

5.  **Arrêtez la Dictée :**
    - Utilisez à nouveau le raccourci (`Ctrl+Alt+V`) pour arrêter. Le cercle rouge disparaîtra.

---

## Créer un lanceur pour le bureau (Linux/Debian)

Pour une intégration parfaite à votre environnement de bureau, vous pouvez créer un lanceur d'application qui apparaîtra dans votre menu "Applications".

1.  **Vérifiez le script de lancement `run.sh` :**
    Ce script est déjà fourni. Il s'assure que l'application se lance avec le bon environnement virtuel.

2.  **Modifiez le fichier `pyvoicetochat.desktop` :**
    Ce fichier agit comme une carte d'identité pour votre application. Vous devez y indiquer le chemin absolu vers votre projet.
    -   Ouvrez `pyvoicetochat.desktop`.
    -   Modifiez les lignes `Exec=` et `Icon=` pour qu'elles pointent vers les fichiers dans le répertoire de votre projet.
        -   La ligne `Exec` doit contenir le chemin absolu vers le script `run.sh`.
        -   La ligne `Icon` doit contenir le chemin absolu vers l'image `icon.png`.

        Par exemple, si vous avez cloné le projet dans `/home/votre-nom/projets/pyvoicetochat`, les lignes devraient être :
        ```ini
        Exec=/home/votre-nom/projets/pyvoicetochat/run.sh
        Icon=/home/votre-nom/projets/pyvoicetochat/icon.png
        ```

3.  **Installez le lanceur :**
    Ouvrez un terminal dans le répertoire du projet et exécutez les commandes suivantes :

    - **Rendez le script exécutable :**
      ```bash
      chmod +x run.sh
      ```
    - **Installez le fichier de bureau pour votre utilisateur :**
      ```bash
      cp pyvoicetochat.desktop ~/.local/share/applications/
      ```

Après ces étapes (il faudra peut-être vous déconnecter/reconnecter), "PyVoiceToChat" devrait apparaître dans votre menu d'applications, vous permettant de le lancer d'un simple clic.

---

## Personnalisation

Vous pouvez facilement personnaliser les raccourcis et les mots-clés en modifiant le fichier `constants.py`.

- **Raccourcis :** Modifiez les ensembles `RECOGNITION_SHORTCUT` et `DEFINE_TARGET_SHORTCUT`.
- **Mots-clés :** Ajoutez ou modifiez des entrées dans le dictionnaire `KEYWORD_ACTIONS` pour créer vos propres commandes vocales.

---

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.