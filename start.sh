#!/bin/bash

# Levanta el Rasa server con API habilitada
rasa run --enable-api --cors "*" --port $PORT &

# Espera 5 segundos para que Rasa server arranque
sleep 5

# Levanta el Action server
rasa run actions
