"""Agent 主循环测试。"""

from __future__ import annotations

from aiforge.agent.loop import Agent
from aiforge.agent.types import LLMResponse, ToolCall
from aiforge.tools.builtin import register_builtin_tools
from aiforge.tools.registry import ToolRegistry


class FakeLLM:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def chat(self, messages, *, tools=None):
        self.calls.append({"messages": messages, "tools": tools})
        return self._responses.pop(0)


def test_agent_uses_tool_then_answers():
    llm = FakeLLM([
        LLMResponse(
            content="",
            tool_calls=[ToolCall(id="c1", name="echo", arguments={"text": "hi"})],
        ),
        LLMResponse(content="结果是 hi"),
    ])
    registry = ToolRegistry()
    register_builtin_tools(registry)
    agent = Agent(llm, registry)
    answer = agent.run("echo hi")
    assert answer == "结果是 hi"
    assert len(llm.calls) == 2
    # 第二次调用应包含 tool 结果
    tool_msgs = [m for m in llm.calls[1]["messages"] if m["role"] == "tool"]
    assert tool_msgs and tool_msgs[0]["content"] == "hi"


def test_agent_max_steps():
    llm = FakeLLM([
        LLMResponse(
            content="",
            tool_calls=[ToolCall(id="c1", name="echo", arguments={"text": "x"})],
        )
        for _ in range(5)
    ])
    registry = ToolRegistry()
    register_builtin_tools(registry)
    agent = Agent(llm, registry, max_steps=3)
    answer = agent.run("loop")
    assert "最大步数" in answer
