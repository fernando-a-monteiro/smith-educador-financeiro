import os
from pathlib import Path

from dotenv import load_dotenv

PASTA_SRC = Path(__file__).resolve().parent
PASTA_RAIZ = PASTA_SRC.parent
PASTA_DATA = PASTA_RAIZ / "data"
ARQUIVO_PROMPTS = PASTA_RAIZ / "docs" / "03-prompts.md"

load_dotenv(PASTA_RAIZ / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")