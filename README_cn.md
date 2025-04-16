# Joern MCP Server

一个简单的Joern的MCP Server。

## 项目简介

本项目是一个基于Joern的MCP Server，提供了一系列功能来帮助开发者进行代码审查和安全分析。

## 环境要求

- Python >= 3.10(默认3.12) & uv
- Joern

## 安装步骤

1. 克隆项目到本地：
   ```bash
   git clone https://github.com/sfncat/mcp-joern.git
   cd mcp-joern
   ```

2. 安装Python依赖：
   ```bash
   uv venv .venv
   source .venv/bin/activate
   uv sync
   ```

## 项目结构

```
├── server.py                       # MCP Server主程序
├── test_mcp_client.py              # joern server和 mcp tool测试程序
├── test_sc_tools.py                # 直接测试sc中的tool程序
├── common_tools.py                 # 通用工具函数
├── server_tools.py                 # 服务器工具函数
├── server_tools.sc                 # 服务器工具函数的scala实现
├── requirements.txt                # Python依赖文件
├── sample_cline_mcp_settings.json  # cline mcp 配置样例文件
└── env_example.txt                 # 环境变量样例文件
```

## 使用方法

1. 启动Joern服务器：
   ```bash
   joern -J-Xmx40G --server --server-host 127.0.0.1 --server-port 16162 --server-auth-username user --server-auth-password password --import server_tools.sc
   ```

2. 复制env_example.txt为.env
   修改配置信息和joern server启动配置的信息一致

3. 运行测试连接：
   修改`test_mcp_client.py`中的信息，确认joern server正常

   ```bash
   uv run test_mcp_client.py
   Starting MCP server test...
   ==================================================
   Testing server connection...
   [04/16/25 20:38:54] INFO     Processing request of type CallToolRequest                                                                                                                     server.py:534
   Connection test result: Successfully connected to Joern MCP, joern server version is XXX
   ```
   
4. 配置MCP server
   在cline中配置mcp服务器，可参考 `sample_cline_mcp_settings.json` 。

5. 使用MCP server
   向大模型提问，可参考`prompts_cn.md`

## 开发说明

- `.env` 文件用于存储环境变量
- `.gitignore` 文件定义了Git版本控制需要忽略的文件
- `pyproject.toml` 定义了项目的Python配置
- mcp tool开发
  - 在`server_tools.sc`中实现，在`server_tools.py`增加定义，在`test_mcp_client.py`中增加测试


## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

欢迎增加更多的tool。

## 参考

https://github.com/flankerhqd/jebmcp

https://docs.joern.io/server/

https://docs.joern.io/interpreter/