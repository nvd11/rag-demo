帮我编写一个非常非常详尽的的md文档, 描述我们是如何基于 langchain+gemini + cloudsql(pgvector) 实现RAG的

要求:
阅读当前项目每一个python 文件和/docs 文件夹下的每一个md 文件,


2 分成3个大节点, 分别是:
 a.数据库准备和表设计
 具体参考: docs/db_schema_design.md
 b knowledge base 数据准备
      文档:https://doc.rvspace.org/VisionFive2/PDF/VisionFive2_DS.pdf
     具体代码:src/examples/import_doc.py 
     要求要详细讲解里面引用的每一个python 类or module
  c. 用自然语言查询知识库
     具体代码:src/examples/agent_query_demo.py
     要求要详细讲解里面引用的每一个python 类or module

3. 对于上面的b 和c 都要画流程图


4. 最好贴上每一个python 文件的核心代码, 和非常具体的讲解

5. agent_query_demo 里有4个问题

要介绍他们的区别细节

a. 问题1 和2 被没有在调用agent时指定topic 范围, 需要由llm自己detect,而 问题3.4 被指定了topic 范围
b. 对于问题1, 根据log输出, agent 首先尝试了topic "VisionFive 2",但检索知识库失败, 然后agent 重试了不用topic , 全表搜索
c. 对于问题2, 与知识库无关, llm拒绝回答
d. 对于问题3, llm回答准确
c. 对于问题4, 与知识库无关, llm根据自己的知识库回答



log of agent_query_demo:

```bash
(.venv) ➜  /workspace git:(agent-query) ✗ ./.venv/bin/python src/examples/agent_query_demo.py
project_path is /workspace
2026-01-02 14:20:30.138 | INFO     | src.configs.log_config:setup_logging:36 - Loguru configured for standard terminal output.
2026-01-02 14:20:30.138 | INFO     | src.configs.config:<module>:39 - Application Environment (APP_ENVIRONMENT) is set to: 'local'
2026-01-02 14:20:30.138 | INFO     | src.configs.config:<module>:49 - Attempting to load configuration from: /workspace/src/configs/config_local.yaml
2026-01-02 14:20:30.139 | INFO     | src.configs.config:<module>:54 - Successfully loaded configuration from config_local.yaml
2026-01-02 14:20:30.139 | INFO     | src.configs.config:<module>:60 - all configs loaded
2026-01-02 14:20:30.139 | INFO     | src.configs.db:<module>:49 - Database connection URL built successfully.
2026-01-02 14:20:30.139 | INFO     | src.configs.db:get_async_engine:64 - Creating new async engine instance.
2026-01-02 14:20:30.163 | INFO     | src.configs.db:<module>:114 - Database engine and session factory configured.

==================================================
🤖 Agent Demo: General Assistant
==================================================

2026-01-02 14:20:30.968 | INFO     | src.services.retrieval_service:__init__:23 - Retrieval Service initialized with embedding model: google/models/text-embedding-004
2026-01-02 14:20:30.968 | INFO     | src.services.retrieval_service:__init__:29 - Retrieval Service initialized with similarity threshold: 0.8
2026-01-02 14:20:30.969 | INFO     | src.llm.gemini_chat_model:__init__:55 - GeminiChatModel initialized with model: gemini-2.5-pro

❓ Question: topic:开发板 ,VisionFive 2 的 CPU 主频是多少？
2026-01-02 14:20:35.110 | INFO     | src.services.retrieval_service:search_knowledge_base:41 - Generating embedding for query: CPU主频
2026-01-02 14:20:35.605 | INFO     | src.services.retrieval_service:search_knowledge_base:49 - Filtering search by topic: VisionFive 2
2026-01-02 14:20:41.283 | WARNING  | src.services.retrieval_service:search_knowledge_base:52 - No documents found for topic 'VisionFive 2'.
2026-01-02 14:20:43.359 | INFO     | src.services.retrieval_service:search_knowledge_base:41 - Generating embedding for query: CPU frequency
2026-01-02 14:20:43.585 | INFO     | src.services.retrieval_service:search_knowledge_base:49 - Filtering search by topic: VisionFive 2
2026-01-02 14:20:43.777 | WARNING  | src.services.retrieval_service:search_knowledge_base:52 - No documents found for topic 'VisionFive 2'.
2026-01-02 14:20:48.913 | INFO     | src.services.retrieval_service:search_knowledge_base:41 - Generating embedding for query: VisionFive 2 CPU
2026-01-02 14:20:49.140 | INFO     | src.services.retrieval_service:search_knowledge_base:55 - No topic provided. Performing global search across all documents.
2026-01-02 14:20:49.140 | INFO     | src.services.retrieval_service:search_knowledge_base:58 - Searching database...
2026-01-02 14:20:58.017 | INFO     | src.services.retrieval_service:search_knowledge_base:110 - Retrieved 5 chunks (Valid by threshold: 5).
💡 Answer: VisionFive 2搭载的CPU工作频率最高可达1.5 GHz。
📚 Sources: 5 found
   - [Source 1] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.3641)
Content: --- Page Break --- 1. 产品介绍 昉·星光 2  是全球首款集成了GPU的高性能RISC-V单板计算机。与昉·星光相比，昉·星光 2全面 升级，在处理器速度、多媒体处理能力、可扩展性等方面均有显著提升。性能卓越，价格亲 民，昉·星光 2将成为迄今为止性价比最高的RISC-V开发平台。 昉·星光 2  搭载四核64位RV64GC ISA的芯片平台（SoC），工作频率最高可达1.5...
   - [Source 2] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.3689)
Content: --- Page Break --- | 1 - 产品介绍 图  1-2 昉·星光 2  产品框图（底部视图） Audio HDMI 2.0 1 x USB 3.0 1 x USB 2.0 Host 1 x USB 3.0 1 x USB 2.0 Host Ethernet (RJ45) Ethernet (RJ45) TF Card eMMC QSPI Flash M.2 11 © 2018-2...
   - [Source 3] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.3832)
Content: 昉·星光 2数据手册 版本：1.53 日期：2023/04/28 Doc ID: VisionFive 2-DSCH-001 --- Page Break --- 法律声明 阅读本文件前的重要法律告知。 版权注释 版权 ©上海赛昉科技有限公司，2023。版权所有。 本文档中的说明均基于“视为正确”提供，可能包含部分错误。内容可能因产品开发而定期更 新或修订。上海赛昉科技有限公司  （以下简称“赛昉...
   - [Source 4] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.4009)
Content: --- Page Break --- | 5 - 外设 5.8. M.2连接器 昉·星光 2提供带有1个PCIe 2.0接口的M.2 M-Key SSD插槽，支持高速存储设备。 5.9. 千兆以太网接口 昉·星光 2提供2个RJ45千兆以太网接口。 5.10. 启动模式Pin 昉·星光 2提供专门的pin，帮助用户在上电前配置启动模式。有以下启动模式可供选择： • 1-bit QSPI Nor F...
   - [Source 5] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.4328)
Content: --- Page Break --- 5. 外设 昉·星光 2  的外设如下： • GPIO接口  (第  18页) • eMMC插槽  (第  20页) • 摄像头和显示接口  (第  20页) • USB Host  (第  24页) • HDMI  (第  24页) • 音频插孔  (第  24页) • M.2连接器  (第  25页) • 千兆以太网接口  (第  25页) • 按钮  (...

❓ Question: 叶丽法的胸围是多少？
💡 Answer: 我无法回答这个问题。我是一个AI助手，我的知识库主要包含技术文档和资料，不包含动漫、游戏角色的个人信息。

==================================================
🤖 Agent Demo: VisionFive 2 Specialist
==================================================

2026-01-02 14:21:07.235 | INFO     | src.services.retrieval_service:__init__:23 - Retrieval Service initialized with embedding model: google/models/text-embedding-004
2026-01-02 14:21:07.235 | INFO     | src.services.retrieval_service:__init__:29 - Retrieval Service initialized with similarity threshold: 0.8
2026-01-02 14:21:07.235 | INFO     | src.llm.gemini_chat_model:__init__:55 - GeminiChatModel initialized with model: gemini-2.5-pro

❓ Question: 昉·星光 2 是什么公司的产品？
2026-01-02 14:21:14.462 | INFO     | src.services.retrieval_service:search_knowledge_base:41 - Generating embedding for query: 昉·星光 2
2026-01-02 14:21:14.986 | INFO     | src.services.retrieval_service:search_knowledge_base:49 - Filtering search by topic: 开发板
2026-01-02 14:21:15.181 | INFO     | src.services.retrieval_service:search_knowledge_base:58 - Searching database...
2026-01-02 14:21:19.642 | INFO     | src.services.retrieval_service:search_knowledge_base:110 - Retrieved 5 chunks (Valid by threshold: 5).
💡 Answer: “昉·星光 2”是**上海赛昉科技有限公司**（StarFive）的产品。

根据其数据手册的法律声明，该产品的版权归“上海赛昉科技有限公司”所有。
📚 Sources: 5 found
   - [Source 1] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.4393)
Content: 目录 表格清单.....................................................................................................................................................................5 插图清单.........................
   - [Source 2] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.4393)
Content: 昉·星光 2数据手册 版本：1.53 日期：2023/04/28 Doc ID: VisionFive 2-DSCH-001 --- Page Break --- 法律声明 阅读本文件前的重要法律告知。 版权注释 版权 ©上海赛昉科技有限公司，2023。版权所有。 本文档中的说明均基于“视为正确”提供，可能包含部分错误。内容可能因产品开发而定期更 新或修订。上海赛昉科技有限公司  （以下简称“赛昉...
   - [Source 3] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.4427)
Content: 1. 产品介绍.................................................................................................................................................9 1.1. 产品框图........................................
   - [Source 4] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.4463)
Content: 目录 插图清单 图  1-1  昉·星光 2  产品框图（顶部视图）....................................................................................................10 图  1-2  昉·星光 2  产品框图（底部视图）........................................
   - [Source 5] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.4628)
Content: --- Page Break --- 前言 关于本指南和技术支持信息 关于本手册 用户通过该手册能获取赛昉科技昉·星光 2单板计算机的功能和技术规格。 修订历史 表  0-1 修订历史 版本 发布说明 修订 1.0 2022/09/05 首次发布。 1.1 2022/09/08 • 更新了机械制图和产品框图（底部视 图）。 • 更新了Reset键的描述。 1.2 2022/10/20 • 修改了M...

❓ Question: Linux Kernel 的编译步骤？
2026-01-02 14:21:25.322 | INFO     | src.services.retrieval_service:search_knowledge_base:41 - Generating embedding for query: Linux Kernel 编译步骤
2026-01-02 14:21:25.669 | INFO     | src.services.retrieval_service:search_knowledge_base:49 - Filtering search by topic: 开发板
2026-01-02 14:21:25.862 | INFO     | src.services.retrieval_service:search_knowledge_base:58 - Searching database...
2026-01-02 14:21:32.627 | INFO     | src.services.retrieval_service:search_knowledge_base:110 - Retrieved 5 chunks (Valid by threshold: 5).
💡 Answer: 抱歉，我在知识库中没有找到关于 Linux Kernel 编译步骤的相关信息。知识库中的文档主要包含产品介绍、功能、接口和机械参数等内容。

如果您想了解通用的 Linux Kernel 编译步骤，通常包括以下几个阶段：
1.  **获取内核源代码**：从官方网站（kernel.org）或相关的代码仓库（如 Git）下载您需要的内核版本的源代码。
2.  **安装编译工具链**：确保您的系统安装了必要的编译工具，如 GCC、Make、Binutils 等。
3.  **配置内核**：根据您的硬件平台和需求，配置内核编译选项。通常可以使用 `make menuconfig`、`make defconfig` 等命令。
4.  **编译内核**：执行 `make` 命令来编译内核。这可能需要较长的时间。
5.  **安装模块和内核**：编译成功后，使用 `make modules_install` 和 `make install` 命令来安装内核模块和内核镜像。
6.  **更新引导加载程序**：更新 GRUB 或其他引导加载程序的配置，以便在系统启动时可以选择新的内核。
7.  **重启系统**：重启计算机并选择新的内核版本启动。

请注意，针对特定的开发板（如 RISC-V 架构的开发板），可能需要使用交叉编译工具链，并且需要针对该开发板特定的配置文件（defconfig）。建议您查阅您所使用的开发板的官方文档或社区以获取更详细和精确的指导。
📚 Sources: 5 found
   - [Source 1] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.4760)
Content: 5. 外设.......................................................................................................................................................18 5.1. GPIO接口.................................
   - [Source 2] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.4811)
Content: 2.3. 软件..........................................................................................................................................................13 3. 机械参数................................
   - [Source 3] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.4933)
Content: --- Page Break --- 1. 产品介绍 昉·星光 2  是全球首款集成了GPU的高性能RISC-V单板计算机。与昉·星光相比，昉·星光 2全面 升级，在处理器速度、多媒体处理能力、可扩展性等方面均有显著提升。性能卓越，价格亲 民，昉·星光 2将成为迄今为止性价比最高的RISC-V开发平台。 昉·星光 2  搭载四核64位RV64GC ISA的芯片平台（SoC），工作频率最高可达1.5...
   - [Source 4] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.4968)
Content: --- Page Break --- | 2 - 功能 2.2. 接口 • 1 × 2-lane MIPI DSI • 1 × 4-lane MIPI DSI • 1 × 2-lane MIPI CSI • 1 × 3.5 mm音频插孔 • 1 × USB-C接口，可用于供电 • 1 × USB device接口（和USB-C接口复用） • 4 × USB 3.0接口（通过昉·惊鸿7110的PCI...
   - [Source 5] (Page: 0, Title: 昉·星光 2数据手册, File: VisionFive2_DS.pdf) (Score: 0.5005)
Content: --- Page Break --- 前言 关于本指南和技术支持信息 关于本手册 用户通过该手册能获取赛昉科技昉·星光 2单板计算机的功能和技术规格。 修订历史 表  0-1 修订历史 版本 发布说明 修订 1.0 2022/09/05 首次发布。 1.1 2022/09/08 • 更新了机械制图和产品框图（底部视 图）。 • 更新了Reset键的描述。 1.2 2022/10/20 • 修改了M...
(.venv) ➜  /workspace git:(agent-query) ✗ 

```