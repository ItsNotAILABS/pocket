from pocket.auth import is_app_shell, path_is_public
from pocket.phoneai_mcp import phone_apps, safe_invoke, tool_is_safe
from pocket.phoneai_os_ui import phoneai_os_html, phoneai_system_html


def test_mcp_servers_are_phone_apps():
    cat = phone_apps()
    assert cat["ok"] is True
    ids = {a["id"] for a in cat["apps"]}
    assert "pocket" in ids
    assert "github" in ids
    pocket = next(a for a in cat["apps"] if a["id"] == "pocket")
    assert pocket["icon"]
    assert pocket["url"].startswith("/phoneai/mcp")
    assert "platform_health" in pocket["safe_tools"] or tool_is_safe("platform_health")


def test_phone_invoke_blocks_shell():
    assert tool_is_safe("platform_health") is True
    assert tool_is_safe("runtime_status") is True
    assert tool_is_safe("shell") is False
    assert tool_is_safe("vcomp_act") is False
    assert tool_is_safe("webmcp_use") is False
    assert tool_is_safe("fs_write") is False
    bad = safe_invoke("pocket", "vcomp_shell")
    assert bad.get("ok") is False


def test_kernel_html_has_mcp_folder():
    html = phoneai_os_html()
    assert 'data-go="mcp"' in html
    assert "/phoneai/mcp" in html
    assert "/v1/phoneai/mcp" in html
    os_html = phoneai_system_html()
    assert "/phoneai/mcp" in os_html


def test_mcp_folder_is_not_anonymous_on_tunnel():
    remote = {"CF-Connecting-IP": "8.8.8.8"}
    addr = ("1.2.3.4", 443)
    assert path_is_public("/phoneai/mcp", headers=remote, client_address=addr) is False
    assert path_is_public("/phoneai/mcp", headers={}, client_address=("192.168.1.40", 9)) is True
    assert is_app_shell("/phoneai/mcp") is True
