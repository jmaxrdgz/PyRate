#!/bin/bash

# Configuration de l'IP du serveur
SERVER_IP="127.0.0.1"  # Remplacez par l'adresse IP du serveur si nécessaire
PORT="8000"

# Vérification si le serveur est accessible
if curl -s --head --request GET "http://$SERVER_IP:$PORT/video/stream" | grep "200 OK" > /dev/null; then
    echo "Connexion au serveur réussie. Lancement du flux vidéo..."
    # Ouvrir le flux vidéo dans un navigateur par défaut
    if command -v xdg-open > /dev/null; then
        xdg-open "http://$SERVER_IP:$PORT/video/stream"
    elif command -v open > /dev/null; then
        open "http://$SERVER_IP:$PORT/video/stream"
    else
        echo "Impossible d'ouvrir le navigateur. Veuillez ouvrir manuellement http://$SERVER_IP:$PORT/video/stream"
    fi
else
    echo "Serveur non accessible à l'adresse http://$SERVER_IP:$PORT"
    exit 1
fi

# Lancer l'agent en tâche de fond
python tests/dummy_agent.py &

