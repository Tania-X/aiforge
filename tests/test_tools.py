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
    # read_file 需审批: 直接 execute 被拦截, 审批后 execute_approved 才读
    blocked = registry.execute("read_file", {"path": "hello.txt"})
    assert blocked.needs_approval is True
    approved = registry.execute_approved("read_file", {"path": "hello.txt"})
    assert approved.output == "hi"


def test_execute_json_parses_arguments():
    registry = ToolRegistry()
    register_builtin_tools(registry)
    result = registry.execute_json("echo", '{"text": "hello"}')
    assert result.output == "hello"


def test_unknown_tool_returns_error():
    registry = ToolRegistry()
    result = registry.execute("nope", {})
    assert "未知工具" in result.output


# ---------------------------------------------------------------- 审批机制
def _counted_tool(counter):
    def handler(text: str) -> str:
        counter["calls"] += 1
        return f"ran:{text}"
    return handler


def test_requires_approval_blocks_execute():
    counter = {"calls": 0}
    registry = ToolRegistry()
    registry.register("danger", "危险操作", {"type": "object", "properties": {"text": {"type": "string"}}},
                      _counted_tool(counter), requires_approval=True)

    result = registry.execute("danger", {"text": "x"})
    assert result.needs_approval is True
    assert "需审批" in result.output
    assert counter["calls"] == 0  # handler 未被调用


def test_execute_approved_runs_handler():
    counter = {"calls": 0}
    registry = ToolRegistry()
    registry.register("danger", "危险操作", {"type": "object", "properties": {"text": {"type": "string"}}},
                      _counted_tool(counter), requires_approval=True)

    result = registry.execute_approved("danger", {"text": "x"})
    assert result.needs_approval is False
    assert result.output == "ran:x"
    assert counter["calls"] == 1


def test_normal_tool_not_blocked():
    counter = {"calls": 0}
    registry = ToolRegistry()
    registry.register("safe", "安全操作", {"type": "object", "properties": {}},
                      lambda: "ok")
    result = registry.execute("safe", {})
    assert result.needs_approval is False
    assert result.output == "ok"


def test_approval_flag_not_in_schema():
    """审批标记是运行时策略, 不应暴露在工具 schema 中。"""
    registry = ToolRegistry()
    registry.register("danger", "危险", {"type": "object", "properties": {}},
                      lambda: "", requires_approval=True)
    schema = registry.schemas()[0]["function"]
    assert "requires_approval" not in schema
    assert schema["name"] == "danger"
