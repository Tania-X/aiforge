"""工具注册表与执行器。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from aiforge.agent.types import ToolResult


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict
    handler: Callable[..., str]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict,
        handler: Callable[..., str],
    ) -> None:
        self._tools[name] = ToolSpec(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
        )

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def schemas(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": spec.name,
                    "description": spec.description,
                    "parameters": spec.parameters,
                },
            }
            for spec in self._tools.values()
        ]

    def execute(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        spec = self.get(name)
        if spec is None:
            return ToolResult(name=name, output=f"未知工具: {name}")
        try:
            output = spec.handler(**arguments)
        except Exception as e:
            output = f"工具执行异常: {type(e).__name__}: {e}"
        return ToolResult(name=name, output=str(output))

    def execute_json(self, name: str, arguments_json: str) -> ToolResult:
        try:
            arguments = json.loads(arguments_json or "{}")
        except json.JSONDecodeError as e:
            return ToolResult(name=name, output=f"参数 JSON 解析失败: {e}")
        return self.execute(name, arguments)
