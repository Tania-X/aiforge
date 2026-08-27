"""Agent 运行时数据类型。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class ToolResult:
    name: str
    output: str
    # 需审批的工具被拦截时置 True(调用方应提示用户审批, 通过后走 execute_approved)
    needs_approval: bool = False


@dataclass
class LLMResponse:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str = ""
    cost: float = 0.0
