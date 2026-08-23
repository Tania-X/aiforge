"""内置安全工具集(默认不含 shell)。"""

from __future__ import annotations

import datetime
from pathlib import Path

from aiforge.tools.registry import ToolRegistry


def register_builtin_tools(registry: ToolRegistry, cwd: str | Path = ".") -> None:
    root = Path(cwd).resolve()

    def list_dir(path: str = ".") -> str:
        target = (root / path).resolve()
        if not str(target).startswith(str(root)):
            return "错误: 路径越界"
        if not target.is_dir():
            return f"错误: 不是目录: {path}"
        return "\n".join(sorted(p.name for p in target.iterdir()))

    def read_file(path: str, max_lines: int = 200) -> str:
        target = (root / path).resolve()
        if not str(target).startswith(str(root)):
            return "错误: 路径越界"
        if not target.is_file():
            return f"错误: 文件不存在: {path}"
        lines = target.read_text(encoding="utf-8", errors="ignore").splitlines()
        body = "\n".join(lines[:max_lines])
        if len(lines) > max_lines:
            body += f"\n...(共 {len(lines)} 行, 已截断)"
        return body

    def echo(text: str) -> str:
        return text

    def current_time() -> str:
        return datetime.datetime.now().isoformat()

    registry.register(
        "list_dir",
        "列出目录内容",
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "相对当前工作目录的路径, 默认 '.'"}
            },
        },
        list_dir,
    )
    registry.register(
        "read_file",
        "读取文本文件内容",
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "相对当前工作目录的文件路径"},
                "max_lines": {"type": "integer", "description": "最多读取行数, 默认 200"},
            },
            "required": ["path"],
        },
        read_file,
    )
    registry.register(
        "echo",
        "原样返回文本",
        {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
        echo,
    )
    registry.register(
        "current_time",
        "返回当前时间",
        {"type": "object", "properties": {}},
        current_time,
    )
