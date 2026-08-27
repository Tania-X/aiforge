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
    # 敏感工具标记: execute() 会拦截, 需显式审批(execute_approved)后才执行
    requires_approval: bool = False


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict,
        handler: Callable[..., str],
        *,
        requires_approval: bool = False,
    ) -> None:
        self._tools[name] = ToolSpec(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
            requires_approval=requires_approval,
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
        """执行工具。需审批的工具被拦截(handler 不调用), 返回 needs_approval 结果。"""
        spec = self.get(name)
        if spec is None:
            return ToolResult(name=name, output=f"未知工具: {name}")
        if spec.requires_approval:
            return ToolResult(
                name=name,
                needs_approval=True,
                output=f"工具需审批未执行: {name}(参数: {arguments})",
            )
        return self._run(spec, arguments)

    def execute_approved(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        """审批通过后执行(跳过审批检查, 仍校验工具存在与参数)。"""
        spec = self.get(name)
        if spec is None:
            return ToolResult(name=name, output=f"未知工具: {name}")
        return self._run(spec, arguments)

    def execute_json(self, name: str, arguments_json: str) -> ToolResult:
        try:
            arguments = json.loads(arguments_json or "{}")
        except json.JSONDecodeError as e:
            return ToolResult(name=name, output=f"参数 JSON 解析失败: {e}")
        return self.execute(name, arguments)

    @staticmethod
    def _run(spec: ToolSpec, arguments: dict[str, Any]) -> ToolResult:
        try:
            output = spec.handler(**arguments)
        except Exception as e:
            output = f"工具执行异常: {type(e).__name__}: {e}"
        return ToolResult(name=spec.name, output=str(output))
