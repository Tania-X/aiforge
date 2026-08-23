"""aiforge CLI 入口。

用法:
    aiforge run "帮我看看当前目录"
    aiforge run --cwd /path/to/dir "读取 README.md 并总结"
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from aiforge.agent.loop import Agent
from aiforge.llm import LLM
from aiforge.tools.builtin import register_builtin_tools
from aiforge.tools.registry import ToolRegistry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aiforge", description="AI Agent Runtime CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run an agent task")
    run.add_argument("task", help="task description")
    run.add_argument("--cwd", default=".", help="working directory for builtin tools")
    run.add_argument("--max-steps", type=int, default=10, help="max agent steps")
    run.add_argument("--verbose", action="store_true", help="enable debug logging")

    args = parser.parse_args(argv)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    registry = ToolRegistry()
    register_builtin_tools(registry, cwd=args.cwd)

    llm = LLM()
    agent = Agent(llm, registry, max_steps=args.max_steps)
    answer = agent.run(args.task)
    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
