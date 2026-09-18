---
name: esp32p4-openvela-bringup-debug
description: Diagnose and verify ESP32-P4 openvela USB-console and CLI Agent bring-up using matching firmware/ELF, task-stack evidence, heap layout, storage limits, network and TLS configuration. Use for board-port debugging or pre-release checks, not generic Agent application design.
---

# ESP32-P4 openvela Bring-up Debug

本 Skill 运行在开发电脑上的 AI 编程助手中，不是板端运行时 Skill。
适用目标：ESP32-P4 Function EV，openvela flat build，USB Serial/JTAG 控制台与 CLI Agent。

## 先记录，后修改

1. 确认源码工作区、目标配置、实际烧写文件和匹配 ELF。运行
   `python3 scripts/check_release.py <openvela-workspace>`，记录配置差异和镜像 SHA-256。
   工具只读，不会构建、烧写、联网或读取 Agent 密钥。
2. 每次只验证当前症状需要的最小路径。保存原始错误，不用最后一行日志直接断言根因。
3. 无板卡访问时，区分“代码检查 / 编译通过”和“实机通过”。不把前者写成后者。

## 根据证据选择路径

### 命令卡住或异常

- 用 `ps` 检查实际任务栈。`CONFIG_NSH_BUILTIN_AS_COMMAND=y` 时内建命令可能在 NSH 当前任务运行。
- 启动入口为 `nsh_main` 时，检查 `CONFIG_INIT_STACKSIZE`，不要只增大 `CONFIG_SYSTEM_NSH_STACKSIZE`。
- GDB 先加载匹配 `nuttx` ELF，再 halt；记录 `bt`、`mepc/mcause/mtval`、`pc/sp/ra` 和故障处反汇编。
  当前 assert 循环的 pc 不一定是原始故障地址，优先同时检查 mepc。
- 不把 ROM 中的 PC、SP=0 解释成应用栈损坏；先确认是否被调试器重置或停在启动阶段。

### free 重复输出同一堆

- 检查 `g_procfs_meminfo` 与 `next` 是否自环，不能仅给打印循环加计数截断。
- 比较板级 `up_allocate_heap` / `up_allocate_kheap` 实际返回范围。
- 只有确认区域重叠且目标为 flat/shared-allocator 方案后，才评估关闭独立内核堆；不要把此操作推广到 protected/kernel build。
- 修正后完整重建，重新启动，验证连续 `free` 返回、堆节点合理及重复 ask 后资源变化。

### USB 丢字

- 先做不含密钥的长文本 echo 测试。比较 USB 包长度和环形缓冲有效容量，留意容量 N 的环可能仅能存 N-1 字节。
- 检查 NSH、syslog、lowputc 是否通过不同路径竞争同一 FIFO。先确定具体 ESP32-P4 编译文件，避免改到同名公共文件却未入镜像。
- 扩大缓冲后仍需实测；不可保证“永不丢字”。

### 存储 / TLS / 时间

- 文件创建失败要记录 errno、fputs 和 fclose 结果。对比 .config、defconfig 和已格式化介质的名称长度；不要贸然格式化 /data。
- TLS 套件修改后核对最终链接归档与 ELF，必要时清理重建依赖库。握手成功不代表证书验证安全完成。
- NTP 修改的是实时时钟；请求超时应使用 CLOCK_MONOTONIC。不要为了 TLS 无条件强设虚构日期。
- 验证顺序按依赖推进：网口注册 → DHCP → DNS/路由 → 校时 → TLS → Agent。`network_status` 只能证明接口配置，不能代替主动连通性测试。

## 验收与停止条件

保留修正前证据、改动位置和修正后结果。至少检查冷启动、重复命令、正常返回 NSH。
烧写、擦除数据、上传日志或推送仓库前确认用户授权。涉及 API Key 的日志必须用合法导出脱敏流程处理。
没有匹配 ELF、原始证据或板端测试能力时停止根因断言，给出下一条最小取证命令，不循环盲改固件。

输出简要记录：症状；证据；确认事实与假设；修正；实际执行的测试；剩余限制。
