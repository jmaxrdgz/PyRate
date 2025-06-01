#!/bin/bash

# Vérification si le serveur est déjà lancé
if pgrep -f "uvicorn pyrate.api:app" > /dev/null; then
    echo "Le serveur est déjà en cours d'exécution."
else
    echo "Lancement du serveur PyRate..."
    # Lancer le serveur uvicorn avec reload pour le développement
    uvicorn pyrate.api:app --reload
fi
