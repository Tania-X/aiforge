"""Agent 短期会话记忆。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Memory:
    """简单的消息列表记忆，后续可替换为向量/长期记忆。"""

    messages: list[dict] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def add_tool_result(self, tool_call_id: str, content: str) -> None:
        self.messages.append(
            {"role": "tool", "tool_call_id": tool_call_id, "content": content}
        )

    def snapshot(self) -> list[dict]:
        return list(self.messages)
