import os
from dotenv import load_dotenv

load_dotenv()  # Automatically loads from `.env` or `.env.local`

DEFAULT_MESSAGE_TRANSPORT = os.getenv("DEFAULT_MESSAGE_TRANSPORT", "SLIM")
TRANSPORT_SERVER_ENDPOINT = os.getenv("TRANSPORT_SERVER_ENDPOINT", "http://localhost:46357")
INTERSIGHT_AGENT_HOST = os.getenv("INTERSIGHT_AGENT_HOST", "localhost")
INTERSIGHT_AGENT_PORT = int(os.getenv("INTERSIGHT_AGENT_PORT", "9999"))
LLM_PROVIDER = os.getenv("LLM_PROVIDER")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG").upper()
