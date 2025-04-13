# Joern MCP Server

一个简单的Joern的MCP Server。

## 项目简介

本项目是一个基于Joern的MCP Server，提供了一系列功能来帮助开发者进行代码审查和安全分析。

## 环境要求

- Python >= 3.12 & uv
- Joern

## 安装步骤

1. 克隆项目到本地：
   ```bash
   git clone [项目地址]
   ```

2. 安装Python依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 项目结构

```
├── server.py           # MCP Server主程序
├── demo.sc             # joern sc示例脚本
├── demo.py             # joern server和 mcp tool测试程序
├── common_tools.py     # 通用工具函数
├── server_tools.py     # 服务器工具函数
└── requirements.txt    # Python依赖文件
└── env_example.txt     # 环境变量样例文件
```

## 使用方法

1. 启动Joern服务器：
   ```bash
   joern -J-xmx40G --server --server-host 127.0.0.1 --server-port 16162 --server-auth-username user --server-auth-password password
   ```
2. 复制env_example.txt为.env
   修改配置信息和joern server信息一致

3. 运行测试连接：
   修改demo.py中的信息，确认joern server正常
   ```bash
   python demo.py
   ```

4. 配置MCP server
   在cline中配置mcp服务器，可参考 `sample_cline_mcp_settings.json` 。

5. 使用MCP server
   向大模型提问，可参考prompts_cn.md

## 开发说明

- `.env` 文件用于存储环境变量
- `.gitignore` 文件定义了Git版本控制需要忽略的文件
- `pyproject.toml` 定义了项目的Python配置

## 许可证

[待补充]

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

## 联系方式

[待补充]