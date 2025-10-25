#!/bin/bash

# Script per riassumere articoli da URL usando DeepSeek-R1 tramite Ollama
# Uso: ./summarize_from_url.sh "https://example.com/article"

if [ $# -eq 0 ]; then
    echo "Errore: Nessun URL fornito"
    echo "Uso: $0 \"https://example.com/article\""
    exit 1
fi

URL="$1"

echo "Scaricamento contenuto da: $URL"
echo "----------------------------------------"

# Scarica il contenuto dell'articolo usando curl e converte HTML in testo
ARTICLE=$(curl -s "$URL" | html2text 2>/dev/null || curl -s "$URL")

if [ -z "$ARTICLE" ]; then
    echo "Errore: Impossibile scaricare il contenuto dall'URL"
    exit 1
fi

PROMPT="Per favore, crea un sommario conciso e strutturato del seguente articolo web. Includi i punti principali e le conclusioni chiave:

$ARTICLE"

echo "Invio articolo a DeepSeek-R1 per il sommario..."
echo "----------------------------------------"

ollama run deepseek-r1:7B "$PROMPT"