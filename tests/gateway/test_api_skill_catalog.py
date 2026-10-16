"""The external skill catalog must use the current skill loader contract."""
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
import pytest

from gateway.config import PlatformConfig
from gateway.platforms.api_server import APIServerAdapter


@pytest.mark.asyncio
async def test_skill_catalog_uses_current_loader_and_lists_installed_skill(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    skill = tmp_path / "skills" / "upgrade-check" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: upgrade-check\ndescription: Check update continuity.\n---\nRead state safely.\n",
        encoding="utf-8",
    )
    adapter = APIServerAdapter(PlatformConfig(enabled=True))
    app = web.Application()
    app.router.add_get("/v1/skills", adapter._handle_skills)
    async with TestClient(TestServer(app)) as client:
        response = await client.get("/v1/skills")
        assert response.status == 200
        payload = await response.json()
    assert payload["object"] == "list"
    assert any(row["name"] == "upgrade-check" for row in payload["data"])
