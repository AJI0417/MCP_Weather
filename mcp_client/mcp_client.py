<<<<<<< HEAD
<<<<<<< HEAD
from langchain_mcp_adapters.client import MultiServerMCPClient


def get_mcp_client():

    return MultiServerMCPClient(
        {
            "LINE_Notify": {
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8001/mcp",
            },
            "Weather": {
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8002/mcp",
            },
        }
=======
from langchain_mcp_adapters.client import MultiServerMCPClient


def get_mcp_client():

    return MultiServerMCPClient(
        {
            "LINE_Notify": {
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8001/mcp",
            },
            "Weather": {
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8002/mcp",
            },
        }
>>>>>>> 67b7abdcdd8ed79b45fa4cef461cc01cced1c1e3
=======
from langchain_mcp_adapters.client import MultiServerMCPClient


def get_mcp_client():

    return MultiServerMCPClient(
        {
            "LINE_Notify": {
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8001/mcp",
            },
            "Weather": {
                "transport": "streamable-http",
                "url": "http://127.0.0.1:8002/mcp",
            },
        }
>>>>>>> 67b7abdcdd8ed79b45fa4cef461cc01cced1c1e3
    )