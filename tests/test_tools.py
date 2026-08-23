"""工具注册表与内置工具测试。"""

from __future__ import annotations

from aiforge.tools.builtin import register_builtin_tools
from aiforge.tools.registry import ToolRegistry


def test_builtin_tools_registered(tmp_path):
    registry = ToolRegistry()
    register_builtin_tools(registry, cwd=tmp_path)

    names = {s["function"]["name"] for s in registry.schemas()}
    assert names == {"list_dir", "read_file", "echo", "current_time"}

    (tmp_path / "hello.txt").write_text("hi", encoding="utf-8")
    result = registry.execute("read_file", {"path": "hello.txt"})
    assert result.output == "hi"


def test_execute_json_parses_arguments():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    result = registry.execute_json("echo", '{"text": "hello"}')
    assert result.output == "hello"


def test_unknown_tool_returns_error():
    registry = ToolRegistry()
    result = registry.execute("nope", {})
    assert "未知工具" in result.output
