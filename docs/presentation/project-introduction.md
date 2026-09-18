# 基于 ESP32-P4 的 openvela AI 设备诊断助手

> 2026-09-16 提交前补图稿。真实结果、代码检查和待测项目分开标注。

## 1. 作品概述

### 作品名称
基于 ESP32-P4 的 openvela AI 设备诊断助手。队伍：124 神一样的老师。材料日期：2026-09-16。定位：新硬件适配与 AI 应用结合的工程原型。

### 核心目标
面向没有屏幕、没有额外传感器的开发板，使用 USB 控制台发起自然语言请求，让 openvela Agent 调用板端设备工具，读取系统与网络配置，再由云端模型解释结果。完成一次问答后返回 NSH，继续执行系统命令。

### 为什么值得做
系统能启动、网口能联网，并不自动等于 Agent 可用。模型调用会同时触及任务栈、内存分配、存储、TLS、系统时间和终端生命周期。本项目针对这些交叉约束完成集成与修正，目标是提供一个可继续开发的板端 AI 诊断基线。

### 差异化主张
不以“首个 ESP32-P4 移植”作为宣传点，也不推测其他参赛作品的水平。差异化在于：设备状态结构化工具、同步 CLI Agent 链路，以及由 GDB 与实机反馈支撑的系统级问题定位。

### 完成度声明
已有实机反馈覆盖联网、云端问答、命令返回、free 与日期。最新短文件名修复已编译，尚待最终实机验收；完整工具演示证据、连续运行记录及干净构建需在提交前补齐。本材料是可补图的提交草稿，不是最终验收报告。

## 2. 架构与使用场景

### 数据链路
USB NSH → ai_agent ask → openvela Agent / ReAct → 华为 MaaS HTTPS 推理 → 工具调用 → 板端 API → JSON → 模型解释 → NSH。设备承担工具执行与请求编排，模型推理在云端，不宣称本地大模型推理。

### device_info
使用 uname、mallinfo 和 CLOCK_MONOTONIC，提供内核版本、架构、运行时间、堆总量、已用、空闲及最大空闲块。board 和 os 字段为实现中的固定标签；证明 openvela 来源应依赖源码版本、构建依赖和实际使用的 Agent 能力，而不是这两个字符串。

### network_status
通过 netlib 获取 eth0 注册状态、UP / RUNNING 标志、IPv4、网关、掩码与 MAC。查询失败的地址字段返回 null。它报告接口状态与配置，不主动测量外网连通性、DNS、速率或丢包，不能把 has_ipv4 等同于互联网可达。

### 数据与接口
配置和会话存于 /data/agent，底层为 SmartFS。已测试的推理入口为 api.modelarts-maas.com/v2/chat/completions，模型标识为 deepseek-v4-flash。模型名称与服务可用性以用户账号实际开通情况为准；密钥由演示者私下配置，不能录入视频或提交仓库。

### 建议演示问题
“请调用 device_info 查看内存和运行时间。”随后询问“请调用 network_status，说明当前 IP、网关与接口状态，不要把接口 UP 当成外网可达。”使用 ifconfig、free 对照；数值可能因请求期间的资源使用和采样时刻而变化，不应要求完全相等。

## 3. 上游基础与本项目贡献

### 尊重开源归属
ESP32-P4 架构、芯片驱动及 HAL 以现有 NuttX / Espressif 和社区实现为基础；Agent 主体、工具注册与 ReAct 框架来自 openvela；JSON、TLS、校时复用 cJSON、mbedTLS 和 NTP。不得把这些组件整体计为本项目原创。正式提交应补充参考 PR 链接、版本及许可说明。

### 贡献 A：目标板集成
面向 Function EV 板整理 USB Console、timer、EMAC、DHCP、procfs、SmartFS 与 Agent 的目标配置；改动涉及内核、应用网络初始化及 Agent 构建配置。工作目标是让板卡启动后的服务依赖顺序与实际可用性一致。

### 贡献 B：真实状态工具
新增 tool_esp32p4.c / .h，实现 device_info 与 network_status，并接入工具注册。工作不是仅添加提示词，而是把真实系统调用返回的数据转换为模型可消费的结构化结果。

### 贡献 C：命令生命周期
增加同步 agent_loop_ask 路径，由 CLI 直接完成 ReAct 请求，复用核心初始化状态并释放请求级缓冲区。避免一次问答启动不必要的常驻服务，回答结束交还 NSH。同步模式不提供后台 cron、heartbeat 或 WebSocket 服务。

### 贡献 D：跨层可靠性
围绕实际症状完成启动任务栈配置、共享堆布局、USB 队列与输出路径、TLS 套件、时间基准和文件名边界的分析与修正。各项修正的证据强弱与验证状态在后文分别注明，不把全部历史卡顿归为单一原因。

## 4. 关键故障定位：任务栈与内存

### 案例 A：set_llm 卡住
GDB 显示异常位置 getumask + 18，mtval = 0x3e。代码路径检查发现，CONFIG_NSH_BUILTIN_AS_COMMAND 下 builtin 使用当前 NSH 任务；启动入口 nsh_main 使用 CONFIG_INIT_STACKSIZE，而此前只扩大了 CONFIG_SYSTEM_NSH_STACKSIZE。旧启动栈为 2048 字节。

### 修正与证据
将 CONFIG_INIT_STACKSIZE 设为 32768，开启栈着色与调试符号。用户实机 ps 显示 NSH 栈可用 32704 字节、观测使用峰值 3572 字节，超过旧 2 KB 配置；set_llm 和 config_show 返回 NSH。结合执行路径、栈峰值与修正效果，支持启动任务栈不足这一判断。

### 案例 B：free 无限打印
用户 GDB 直接观测 g_procfs_meminfo = 0x4ff5dac0，节点 next 同样为 0x4ff5dac0，比较表达式为 1，说明 Umem 链表节点自环。该证据解释了 meminfo_read 不断输出相同行的现象。

### 修正与证据
在当时关闭 PSRAM 用户堆但启用独立内核堆的配置下，板级用户堆和内核堆返回重叠 SRAM。flat 模式关闭 CONFIG_MM_KERNEL_HEAP，改为共享分配器并完整清理重编译；ELF 检查不再保留独立内核堆符号，用户随后确认 free 正常。不是简单修改 free 或人为断开链表。

### 截图位 A / B
请补：GDB 异常寄存器、修正后的 ps；procfs 节点自环记录、修正后的 free 与 nsh>。旧记录仅用于解释定位过程，不作为当前镜像仍有同样故障的证据。

## 5. 跨层集成：USB、TLS、时间与存储

### USB 控制台
原软件环形队列为 64 字节，有效容量 63 字节；修改 RX/TX 缓冲为 2048 字节，并通过 SYSLOG_CONSOLE 统一正常日志输出路径。该修正针对长命令丢字和输出交错；最终仍应补连续长文本回显测试，不宣称绝对不丢字。

### TLS 实际服务互通
启用 ECDHE-RSA / ECDHE-ECDSA，排查配置变化后静态库未充分重建的问题。用户日志已出现 TLSv1.2 / TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384 握手成功，并收到模型回答。握手成功不等于生产级安全完成；当前仍为 MBEDTLS_SSL_VERIFY_OPTIONAL。

### 时间与耗时分离
删除把系统时钟强设为 2026-02-28 的补偿逻辑；冷启动时间无效时启动 NTP 并短时等待，失败返回明确提示。LLM 耗时与 trace 改用 CLOCK_MONOTONIC，避免校时跳变造成几十亿毫秒的假超时。用户已反馈日期恢复至 2026-09-16。

### 文件名边界
当前已构建镜像的 SMARTFS_MAXNAMLEN 为 16；文件系统写名称时预留终止符，16 字节名称存在截断边界。内置名称改为 daily-brief.md、skill-create.md、sys-health.md，增加 errno 及写入/关闭错误检查。修正已编译，最终实机验证待补；不自动删除旧文件或重新格式化数据。

### 发布前配置风险
本次核对发现 usbnet/defconfig 的 SMARTFS_MAXNAMLEN 为 48，而当前 .config 为 16。应结合已有数据区格式对齐正式构建配置并复验，不能将两者视作已经一致。该项尚未在本次文档制作中修改。

## 6. 工作量与验证矩阵

### 工作量口径
2026-09-16 工作区快照：nuttx 有 9 个、apps 有 3 个、packages/ai_agent 有 18 个已跟踪文件存在未提交改动，共 30 个；另有 usbnet 配置目录及 tool_esp32p4.c / .h 新文件。统计只反映当前增量范围，不代表全部移植代码，也不用于声称原创行数或人天。

### 七类工程工作
1. 板级启动与构建配置；2. USB 终端；3. timer / EMAC / DHCP；4. 可写存储；5. Agent CLI 与设备工具；6. TLS / 时间；7. 栈堆定位、回归与交付材料。主要难点是层间约束，不是单文件代码长度。

### 已获得实机反馈
NSH 与联网；DHCP 获取 192.168.1.136；网关及公网域名各一次 10 包 ping 测试均 10 发 10 收；TLS / 云端问答；同步命令返回；free 与日期正常。IP 为当次 DHCP 结果，不是固定配置；零丢包只限上述短测试，不代表长期可靠性。

### 必须补录 / 补测
两项设备工具与命令输出的对照；最新短文件名及内容读取；重启后配置持久化（截图不含密钥）；连续 10 次 ask 前后 free / ps；无效输入与网络异常的可恢复性；干净目录构建和配置一致性。记录 pass / fail 与实际结果，不能预填通过。

### AI 开发协作
AI 用于需求拆解、跨仓检索、补丁生成、日志分析与文档整理；开发者负责板端实验和反馈，调试器提供现场证据。计划归集开发 Skill 与脱敏日志，当前未完成提交，不用板端自带天气 Skill 替代开发成果。

## 7. 演示方案与已知限制

### 视频顺序
主 PPT 13 页，建议旁白约 4 分 47 秒，可根据实机片段调整到 5 分钟以内。先说明场景与原创边界，再展示架构、真实工具、两个深度定位案例和完成度。附录 2 页只供答辩，不计入主视频。

### 五处实机图
第 1 页板卡连接；第 6 页工具问答与 NSH 返回；第 7 页任务栈证据；第 8 页堆链表与 free；第 12 页联网、时间与连续请求。所有占位均明确标记为待补图，没有生成虚构实机结果。

### 能力限制
依赖公网与云端模型，不支持离线大模型推理。天气、搜索等服务密钥未配置；注册表中存在的工具不等于本板具备相应硬件。PSRAM 当前未作为用户堆，不宣称 32 MB 可用 Agent 堆。没有完成全外设验证、长稳测试或性能基准。

### 安全限制
TLS 证书验证尚未产品化，API Key 存储保护也不应视为完成。此前开发交流中出现过密钥，应撤销/轮换，并检查文档、日志、录屏、配置文件及 Git 历史。只演示脱敏信息，不发布含用户数据的 SmartFS 分区。

### 提交清单
正式 README；可复现源码与固定版本；跨仓 PR 及许可归属；固件和校验值；开发 Skill 与脱敏会话日志；最终测试记录；介绍文档、PPT 和不超过 5 分钟的视频。本次仅制作介绍材料，不表示已经提交或已满足全部验收项。

## 8. 代码证据与版本记录

### 关键代码路径
nuttx/boards/risc-v/esp32p4/esp32p4-function-ev-board/configs/usbnet/defconfig；同板 src/esp32p4_bringup.c；nuttx/arch/risc-v/src/esp32p4/espressif/esp_usbserial.c；nuttx/boards/risc-v/esp32p4/common/src/esp_board_spiflash.c。

### Agent 证据路径
packages/ai_agent/src/agent_main.c；src/core/agent_loop.c 与 agent_trace.c；src/tools/tool_esp32p4.c 与 tool_registry.c；src/tools/skill_loader.c；src/infra/vela_tls.c。DHCP 相关增量位于 apps/netutils/netinit。

### 基线快照（不是最终发布版本）
nuttx: 10c4e090243；apps: dcc6a95c3b323e533c98fde8fb209f99e24f0fdd；packages/ai_agent: e65550f18759f086d7f544edcf17d1e31223244f。三仓均叠加本地修改，单独检出这些提交不能复现本项目。

### 当前待最终验收镜像
nuttx/nuttx.bin，695176 字节；SHA-256: d8b6cdd16e46cc0a0cef14e6e94a5702bf6da6c4cada3000e93e6b8eeefabae7。构建记录为 2026-09-16 21:58:33 +0800。最终配置对齐或重新构建后必须更新此记录和截图版本。

### 参考与归属
上游：github.com/open-vela/nuttx、github.com/open-vela/packages_ai_agent。比赛总览与提交指南位于 github.com/open-vela/docs 的 dev-ai-contest-2026 分支 zh-cn/contest_2026/。本材料依据本地源码、构建记录及用户实机反馈整理；未验证的同行比较与首次适配主张均不采用。
