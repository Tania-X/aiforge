"""LLM 网关适配层。

优先复用 ai-tools 的 gateway；如果未安装 ai-tools，则给出可操作提示。
后续可替换/扩展为其他 OpenAI 兼容客户端。
"""

from __future__ import annotations

from typing import Any

from aiforge.agent.types import LLMResponse, ToolCall


class LLM:
    def __init__(self) -> None:
        try:
            from gateway import LLMClient, load_config
        except ImportError as e:
            raise RuntimeError(
                "未找到 ai-tools gateway，请先安装: pip install -e ../ai-tools"
            ) from e

        self._client = LLMClient(load_config())

    def chat(
        self,
        messages: list[dict],
        *,
        tools: list[dict] | None = None,
    ) -> LLMResponse:
        resp = self._client.chat(messages, tools=tools)
        tool_calls = [
            ToolCall(
                id=tc["id"],
                name=tc["name"],
                arguments=__import__("json").loads(tc.get("arguments") or "{}"),
            )
            for tc in (resp.tool_calls or [])
        ]
        return LLMResponse(
            content=resp.content or "",
            tool_calls=tool_calls,
            model=resp.model,
            cost=resp.cost,
        )
