"""Agent 主循环: Plan → Act → Observe。"""

from __future__ import annotations

import logging
from typing import Any, Protocol

from aiforge.agent.memory import Memory
from aiforge.agent.types import LLMResponse
from aiforge.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个通用 AI Agent。
你可以调用工具来获取信息或执行操作。
请根据用户任务选择合适的工具，并最终用中文给出简洁回答。
"""


class LLMProtocol(Protocol):
    def chat(
        self,
        messages: list[dict],
        *,
        tools: list[dict] | None = None,
    ) -> LLMResponse: ...


class Agent:
    def __init__(
        self,
        llm: LLMProtocol,
        tools: ToolRegistry,
        *,
        max_steps: int = 10,
        system_prompt: str = SYSTEM_PROMPT,
    ):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.memory = Memory()
        self.memory.add("system", system_prompt)

    def run(self, task: str) -> str:
        self.memory.add("user", task)
        messages = self.memory.snapshot()

        for step in range(1, self.max_steps + 1):
            logger.info("agent step %d/%d", step, self.max_steps)
            resp = self.llm.chat(messages, tools=self.tools.schemas())

            if not resp.tool_calls:
                self.memory.add("assistant", resp.content or "")
                return resp.content or ""

            for call in resp.tool_calls:
                result = self.tools.execute(call.name, call.arguments)
                logger.info(
                    "tool %s -> %s", result.name, result.output[:200]
                )
                self.memory.add_tool_result(call.id, result.output)
                messages = self.memory.snapshot()

        return "已达到最大步数，任务未完成。"
