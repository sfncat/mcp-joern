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
├── server_tools_source.sc          # 服务器工具函数的scala实现,使用sourceCode获取method的code
├── requirements.txt                # Python依赖文件
├── sample_cline_mcp_settings.json  # cline mcp 配置样例文件
└── env_example.txt                 # 环境变量样例文件
```

## 使用方法

1. 启动Joern服务器：
   ```bash
   joern -J-Xmx40G -J-XX:CompressedClassSpaceSize=1g -J-XX:MaxMetaspaceSize=2g \
         --server --server-host 127.0.0.1 --server-port 16162 \
         --server-auth-username user --server-auth-password password --import server_tools.sc
   或
   joern -J-Xmx40G -J-XX:CompressedClassSpaceSize=1g -J-XX:MaxMetaspaceSize=2g \
         --server --server-host 127.0.0.1 --server-port 16162 \
         --server-auth-username user --server-auth-password password --import server_tools_source.sc
   ```
   **为什么要加这两个 JVM 参数** —— 默认值偏小，且只在长时间使用后才暴露，容易被误判成"服务坏了"：

   - `-XX:CompressedClassSpaceSize=1g`：Joern REPL 每执行一次查询就编译一个新类（`rs$line$N`），
     默认类空间（128m）在几千次查询后被耗尽，之后**所有**查询都失败并报
     `NoClassDefFoundError: Could not initialize class rs$line$NNNN`。
   - `-XX:MaxMetaspaceSize=2g`：与类空间同步留出元空间余量。
   - `-J-Xmx…`：按 CPG 大小设置堆；堆不足的表现是查询超时，而不是 OOM。实测约 400 MB 的 CPG 用 `-Xmx60G` 稳定。
   如果是在Windows下使用,可能需要通过命令行或在系统环境变量中设置JVM系统变量解决加载脚本失败的问题
   ```
   set _JAVA_OPTIONS=-Dfile.encoding=UTF-8
   ```
   设置joern通用日志级别
   ```
   set SL_LOGGING_LEVEL=ERROR //windows
   export SL_LOGGING_LEVEL=ERROR //linux
   ```
   如果有下面的告警

   ```
   Unable to create a system terminal, creating a dumb terminal (enable debug logging for more information)
   ```
   可以通过设置环境变量关闭
   ```
   set TERM=dumb
   export TERM=dumb
   ```
   恢复
   ```
   set TERM=xterm-256color
   export TERM=xterm-256color
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

## 更新记录

### v1.2.0 (2026-09-10)

**服务端调用链工具（性能）**

- `server_tools.sc` 新增 Scala 助手：`get_methods_by_name`（`nameExact` 索引查询，替代全表
  `.filter(_.fullName.contains(...))` 扫描——后者在大 CPG 上必然超时）、`get_callee_chain`
  （服务端 BFS，一次 HTTP 返回整条调用链：方法全名 + 代码，自动跳过 JDK/框架方法）、
  `get_callee_chain_names`（只要方法名、不带代码的轻量版）。
- 新增对应的 MCP 工具：`get_callee_chain_server`、`get_methods_by_name`。
- 效果：解析一条调用链的 HTTP 往返从约 30 次降到 1 次。

**HTTP 客户端加固（`server.py`）**

- `joern_remote` 改用 keep-alive 的 `requests.Session` 并配置连接池。
- 瞬时失败重试 3 次；401/403 鉴权错误**快速失败**（这类错误不是瞬时故障）。
- 失败时返回明确的 `ERROR: ...` 字符串（原来是 `None`），调用方可以区分“失败”与“空结果”。

**修复**

- 凭据键兼容：仓库自带的 `.env` 用 `USER_NAME`/`PASSWORD`，而宿主配置注入的是
  `JOERN_AUTH_USERNAME`/`JOERN_AUTH_PASSWORD`；原实现只读后者，导致任何不经宿主注入 env 的启动
  （含仓库自带 `test_mcp_client.py`）静默 401。现在两者都接受。
- FastMCP 兼容：`log_level` 构造参数在 fastmcp 2.x 中已被移除，现在用 `try/except` 传入并以
  `FASTMCP_LOG_LEVEL` 兜底。

**文档与杂项**

- 启动命令增加 `-XX:CompressedClassSpaceSize=1g -XX:MaxMetaspaceSize=2g`（默认值为何只在长时间
  使用后才失败，见“启动Joern服务器”下的说明）。
- 代码注释一律英文；中文只保留在 `README_cn.md` 与 `prompts_cn.md`。
- `.gitignore` 增加 `*.cpg`、`*.bak-*` 与本机凭据包装脚本 `run_verify.sh`。
- 版本号升级到 1.2.0。
