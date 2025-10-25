"""AI service for content summarization using Ollama."""

import httpx


class OllamaService:
    """Service for interacting with Ollama API."""

    def __init__(self, endpoint: str, model: str):
        self.endpoint = endpoint
        self.model = model

    async def summarize(self, content: str, max_length: int = 200) -> str:
        """Summarize content using Ollama."""
        try:
            prompt = f"""Riassumi brevemente il seguente testo in italiano, in massimo {max_length} parole:

{content}

Riassunto:"""

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.endpoint}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "top_p": 0.9,
                        },
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "").strip()
                else:
                    return f"Errore AI: {response.status_code}"

        except Exception as e:
            return f"Errore nella chiamata AI: {str(e)}"
