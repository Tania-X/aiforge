# aiforge

AI-Native Software Delivery & Operations Platform — Agent Runtime

> 当前阶段：本地 init，先做 AI Agent Runtime 最小闭环。

## 已包含

- Agent 主循环（Plan → Act → Observe）
- 工具注册表
- 内置安全工具：`list_dir` / `read_file` / `echo` / `current_time`
- 简单会话记忆
- CLI 入口
- 单测

## 快速开始

```bash
# 创建虚拟环境并安装
python3 -m venv .venv
.venv/bin/pip install -e .

# 需要复用 ai-tools gateway
# .venv/bin/pip install -e ../ai-tools

# 运行 Agent 任务
.venv/bin/aiforge run "帮我看看当前目录"
```

## 结构

```text
aiforge/
├── aiforge/
│   ├── agent/
│   │   ├── loop.py          # Agent 主循环
│   │   ├── memory.py        # 短期记忆
│   │   └── types.py         # 数据类型
│   ├── tools/
│   │   ├── registry.py      # 工具注册表
│   │   └── builtin.py       # 内置安全工具
│   ├── llm.py               # LLM 网关适配（复用 ai-tools gateway）
│   └── cli.py               # CLI
└── tests/
```

## 路线图

- [x] Agent Runtime 最小闭环
- [ ] 接入 ai-tools gateway 真实模型
- [ ] 工具权限/审批
- [ ] 多 Agent
- [ ] 记忆持久化 / RAG
- [ ] 评测集
- [ ] 连接器（GitLab / Jenkins / 日志 / 指标）
- [ ] UI
