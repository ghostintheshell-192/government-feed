#!/bin/bash

# Script pulito per riassumere articoli senza codici ANSI
# Uso: ./summarize_clean.sh "testo" oppure echo "testo" | ./summarize_clean.sh

if [ $# -eq 0 ]; then
    ARTICLE=$(cat)
else
    ARTICLE="$1"
fi

PROMPT="Per favore, crea un sommario conciso e strutturato del seguente articolo. Includi i punti principali e le conclusioni chiave:

$ARTICLE"

# Rimuove i codici ANSI dall'output di ollama
ollama run deepseek-r1:7B "$PROMPT" | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' | sed 's/\[[?][0-9]*[a-zA-Z]//g'