#!/bin/bash

# Script per riassumere articoli usando DeepSeek-R1 tramite Ollama
# Uso: ./summarize_article.sh "testo_articolo"
# oppure: ./summarize_article.sh < articolo.txt

if [ $# -eq 0 ]; then
    echo "Lettura da stdin..."
    ARTICLE=$(cat)
else
    ARTICLE="$1"
fi

if [ -z "$ARTICLE" ]; then
    echo "Errore: Nessun articolo fornito"
    echo "Uso: $0 \"testo articolo\" oppure $0 < file.txt"
    exit 1
fi

PROMPT="Per favore, crea un sommario conciso e strutturato del seguente articolo. Includi i punti principali e le conclusioni chiave:

$ARTICLE"

echo "Invio articolo a DeepSeek-R1 per il sommario..."
echo "----------------------------------------"

ollama run deepseek-r1:7B "$PROMPT"