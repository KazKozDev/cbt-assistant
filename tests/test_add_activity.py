import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.server import app

@pytest.mark.asyncio
async def test_add_activity_tool():
    # We will simulate a chat request that triggers the tool
    pass
