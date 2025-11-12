"""
Module main.

Ce module fait partie du système Arkalia Luna Pro.
"""

import os

from core import app

if __name__ == "__main__":
    import uvicorn

    host = "0.0.0.0" if os.getenv("ENV") == "prod" else "127.0.0.1"  # arkalia.luna.system@gmail.com
    uvicorn.run(app, host=host, port=8000)
