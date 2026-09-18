# 实机历史回传记录摘录

来源：参赛者在本项目真实 Codex 对话中提交的串口/GDB 输出。以下为原文摘录，不是新执行测试，也不是重新生成的设备输出。来源时间为对话事件时间，不假定等于设备测量时间。

## 联网测试
事件时间：2026-09-10T14:46:52.978Z；seq=1420；source_ordinal=3670

```text
nsh> et
nsh> emacinit emac
emacinit: esp_emac_init begin
emacinit: esp_emac_init returned
emacinit: OK
nsh> ifconfig
nsh: ifconfig: Could not open /proc/net (is procfs mounted?)
nsh: ifconfig: opendir failed: No such file or directory
nsh>
nsh> mkdir /proc
nsh> mount -t procfs /proc
nsh>   ifconfig
eth0    Link encap:Ethernet HWaddr e8:f6:0a:e3:a6:46 at DOWN mtu 1500
        inet addr:0.0.0.0 DRaddr:0.0.0.0 Mask:0.0.0.0

nsh> ifup eth0
ifup eth0...OK
nsh> renew eth0
nsh> ifconfig eth0
eth0    Link encap:Ethernet HWaddr e8:f6:0a:e3:a6:46 at RUNNING mtu 1500
        inet addr:192.168.1.136 DRaddr:192.168.1.1 Mask:255.255.255.0

nsh> ping 192.168.1.1
PING 192.168.1.1 56 bytes of data
56 bytes from 192.168.1.1: icmp_seq=0 time=20.0 ms
56 bytes from 192.168.1.1: icmp_seq=1 time=10.0 ms
56 bytes from 192.168.1.1: icmp_seq=2 time=10.0 ms
56 bytes from 192.168.1.1: icmp_seq=3 time=10.0 ms
56 bytes from 192.168.1.1: icmp_seq=4 time=10.0 ms
56 bytes from 192.168.1.1: icmp_seq=5 time=10.0 ms
56 bytes from 192.168.1.1: icmp_seq=6 time=10.0 ms
56 bytes from 192.168.1.1: icmp_seq=7 time=10.0 ms
56 bytes from 192.168.1.1: icmp_seq=8 time=10.0 ms
56 bytes from 192.168.1.1: icmp_seq=9 time=10.0 ms
10 packets transmitted, 10 received, 0% packet loss, time 10100 ms
rtt min/avg/max/mdev = 10.000/11.000/20.000/3.000 ms
nsh> ping www.baidu.com
PING 110.242.69.21 56 bytes of data
56 bytes from 110.242.69.21: icmp_seq=0 time=20.0 ms
56 bytes from 110.242.69.21: icmp_seq=1 time=20.0 ms
56 bytes from 110.242.69.21: icmp_seq=2 time=20.0 ms
56 bytes from 110.242.69.21: icmp_seq=3 time=20.0 ms
56 bytes from 110.242.69.21: icmp_seq=4 time=20.0 ms
56 bytes from 110.242.69.21: icmp_seq=5 time=20.0 ms
56 bytes from 110.242.69.21: icmp_seq=6 time=20.0 ms
56 bytes from 110.242.69.21: icmp_seq=7 time=20.0 ms
56 bytes from 110.242.69.21: icmp_seq=8 time=20.0 ms
56 bytes from 110.242.69.21: icmp_seq=9 time=20.0 ms
10 packets transmitted, 10 received, 0% packet loss, time 10100 ms
rtt min/avg/max/mdev = 20.000/20.000/20.000/0.000 ms
```

## 任务栈观测
事件时间：2026-09-16T12:20:31.909Z；seq=2861；source_ordinal=8332

```text
NuttShell (NSH)
nsh> ps
  PID GROUP PRI POLICY   TYPE    NPX STATE    EVENT     SIGMASK            STACK    USED FILLED COMMAND
    0     0   0 FIFO     Kthread   - Ready              0000000000000000 0002016 0000732  36.3%  CPU0 IDLE
    1     0 100 RR       Kthread   - Waiting  Semaphore 0000000000000000 0001968 0000408  20.7%  lpwork 0x4ff49540 0x4ff49588
    2     2 100 RR       Task      - Running            0000000000000000 0032704 0001668   5.1%  nsh_main
    3     0 252 RR       Kthread   - Waiting  Semaphore 0000000000000000 0004016 0000324   8.0%  esp_timer 0x4ff66c38
    4     0  15 RR       Kthread   - Waiting  Semaphore 0000000000000000 0004032 0000352   8.7%  emac_rx 0x4ff67f28
nsh> ai_agent set_llm mimo
[agent-check-0916] builtin enter
[setdiag-v3] monitor create rc=0
[agent-config-0916] begin set_llm
store ready at /data/agent/config/config.json
[llm] No API key. Use CLI: set_llm <preset> <key>
[agent-config-0916] llm init rc=0
m_router] lock begin
[llm_router] lock done
[llm_router] profile read begin
[llm_router] profile read done: -1
[llm_router] backend 0 read begin
[llm_router] backend 0 read done: -1
[llm_router] backend 1 read begin
[llm_router] backend 1 read done: -1
[llm_router] backend 2 read begin
[llm_router] backend 2 read done: -1
[llm_router] backend 3 read begin
[llm_router] backend 3 read done: -1
[llm_router] Router initialized: 0 backends, profile=0
[agent-config-0916] router init rc=0
[setdiag-v1] command enter argc=2
[setdiag-v1] existing backend read begin
[setdiag-v1] existing backend read done
[setdiag-v1] backend save begin
[setdiag-v2] save 1 returned rc=0
ed: api.xiaomimimo.com
[setdiag-v1] backend save returned rc=0
[setdiag-v1] apply begin
[setdiag-v2] save 2 returned rc=0
[setdiag-v2] save 3 returned rc=0
[setdiag-v2] save 4 returned rc=0
[setdiag-v2] save 5 returned rc=0
ically: api.xiaomimimo.com/v1/chat/completions (model: mimo-v2-flash)
[setdiag-v1] apply returned rc=0
LLM backend: api.xiaomimimo.com:443/v1/chat/completions (model: mimo-v2-flash) [router slot 0]
[agent-check-0916] command returned rc=0
[agent-check-0916] builtin returned rc=0
nsh> ai_agent config_show
[agent-check-0916] builtin enter
[agent-config-0916] begin config_show
 store ready at /data/agent/config/config.json
=== Current Configuration ===
  Feishu AppID  : (not set)
  Feishu Secret : (not set)
  API Key       : (not set)
  Model         : mimo-v2-flash
  LLM Host      : api.xiaomimimo.com
  LLM Path      : /v1/chat/completions
  Vision Model  : (not set)
  Vision Host   : (not set)
  Vision Key    : (not set)
  Proxy Host    : (not set)
  Proxy Port    : (not set)
  SerpAPI Key   : (not set)
  Exa Key       : (not set)
  Tavily Key    : (not set)
  News Key      : (not set)
  Tavily Key    : (not set)
  Gateway       : (not set)
  GW Port       : (not set)
  GW Token      : (not set)
  MQTT Broker   : (not set)
  Volc AppKey   : (not set)
  Volc Token    : (not set)
  Volc API Key  : (not set)
  Volc Speaker  : (not set)
[netmgr] Found iface eth0 addr 192.168.1.136
[netmgr] Found iface eth0 addr 192.168.1.136
Network: connected / 192.168.1.136
=============================
[agent-check-0916] command returned rc=0
[agent-check-0916] builtin returned rc=0
nsh> ps
  PID GROUP PRI POLICY   TYPE    NPX STATE    EVENT     SIGMASK            STACK    USED FILLED COMMAND
    0     0   0 FIFO     Kthread   - Ready              0000000000000000 0002016 0000732  36.3%  CPU0 IDLE
    1     0 100 RR       Kthread   - Waiting  Semaphore 0000000000000000 0001968 0000408  20.7%  lpwork 0x4ff49540 0x4ff49588
    2     2 100 RR       Task      - Running            0000000000000000 0032704 0003572  10.9%  nsh_main
    3     0 252 RR       Kthread   - Waiting  Semaphore 0000000000000000 0004016 0000324   8.0%  esp_timer 0x4ff66c38
    4     0  15 RR       Kthread   - Waiting  Semaphore 0000000000000000 0004032 0000352   8.7%  emac_rx 0x4ff67f28
```

## 堆自环现场
事件时间：2026-09-16T13:28:20.174Z；seq=2981；source_ordinal=8737

```text
(gdb) target remote localhost:3333
Remote debugging using localhost:3333
warning: No executable has been specified and target does not support
determining executable automatically.  Try using the "file" command.
0x40012e58 in ?? ()
(gdb) file "//wsl.[REDACTED_OPAQUE_TOKEN]"
A program is being debugged already.
Are you sure you want to change the file? (y or n) y
Reading symbols from //wsl.[REDACTED_OPAQUE_TOKEN]...
(gdb)  monitor halt
[esp32p4.hp.cpu0] Target halted, PC=0x40012E58, debug_reason=00000000
(gdb) bt
#0  0x40012e58 in __ultoa_invert (val=7757, str=0x4ff66309 "40204O8", str@entry=0x4ff66308 "640204O8", base=10)
    at stream/lib_ultoa_invert.c:64
#1  0x40012bce in vsprintf_internal (stream=0x4ff66364, arglist=0x0, numargs=0, fmt=<optimized out>, ap=0x4ff663c4,
    numargs=0, arglist=0x0) at stream/lib_libvsprintf.c:1303
#2  0x4002ead0 in vsnprintf (buf=buf@entry=0x4ff70548 "     402040", size=size@entry=512,
    format=format@entry=0x40081cc4 "%11lu%11lu%11lu%11lu%11lu%7lu%7lu %s\n", ap=ap@entry=0x4ff663bc)
    at stdio/lib_vsnprintf.c:72
#3  0x4002ae44 in procfs_snprintf (buf=buf@entry=0x4ff70548 "     402040", size=size@entry=512,
    format=format@entry=0x40081cc4 "%11lu%11lu%11lu%11lu%11lu%7lu%7lu %s\n") at procfs/fs_procfsutil.c:148
#4  0x4002a0a4 in meminfo_read (filep=0x4ff6eaa0,
    buffer=0x4ff70750 "   402040      77576     324464      80416     321208    114     40 Umem\n     402040      77576     324464      80416     321208    114     40 Umem\n     402040      77576     324464      80416     321"...,
    buflen=512) at procfs/fs_procfsmeminfo.c:360
#5  0x40006c32 in file_readv_compat (filep=<optimized out>, iov=<optimized out>, iovcnt=<optimized out>)
    at vfs/fs_read.c:84
#6  file_readv (filep=0x4ff6eaa0, iov=iov@entry=0x4ff66498, iovcnt=iovcnt@entry=1) at vfs/fs_read.c:175
#7  0x40006c6e in nx_readv (fd=fd@entry=3, iov=iov@entry=0x4ff66498, iovcnt=iovcnt@entry=1) at vfs/fs_read.c:258
#8  0x40006ca4 in readv (fd=fd@entry=3, iov=iov@entry=0x4ff66498, iovcnt=iovcnt@entry=1) at vfs/fs_read.c:323
#9  0x40006cd0 in read (fd=fd@entry=3, buf=buf@entry=0x4ff70750, nbytes=nbytes@entry=512) at vfs/fs_read.c:357
#10 0x4001a774 in nsh_catfile (vtbl=0x4ff70e38, cmd=0x4ff710f4 "free", filepath=<optimized out>) at nsh_fsutils.c:171
#11 0x40017f0c in nsh_command (vtbl=0x4ff70e38, argc=1, argv=0x4ff665d0) at nsh_command.c:1329
#12 0x40015d9a in nsh_execute (vtbl=vtbl@entry=0x4ff70e38, argc=argc@entry=1, argv=argv@entry=0x4ff665d0,
    param=param@entry=0x4ff66564) at nsh_parse.c:722
#13 0x40016a5c in nsh_parse_command (vtbl=vtbl@entry=0x4ff70e38, cmdline=<optimized out>, param=0x4ff66564)
    at nsh_parse.c:2987
#14 0x40016b1a in nsh_parse (vtbl=vtbl@entry=0x4ff70e38, cmdline=cmdline@entry=0x4ff710f4 "free") at nsh_parse.c:3109
#15 0x400152cc in nsh_session (pstate=pstate@entry=0x4ff70e38, login=login@entry=1, argc=argc@entry=1,
    argv=argv@entry=0x4ff5e708) at nsh_session.c:246
#16 0x400150d0 in nsh_consolemain (argc=argc@entry=1, argv=argv@entry=0x4ff5e708) at nsh_consolemain.c:75
--Type <RET> for more, q to quit, c to continue without paging--p g_procfs_meminfoc
#17 0x40015098 in nsh_main (argc=1, argv=0x4ff5e708) at nsh_main.c:74
#18 0x400118fc in nxtask_startup (entrypt=entrypt@entry=0x40015068 <nsh_main>, argc=<optimized out>,
    argv=<optimized out>) at sched/task_startup.c:66
#19 0x4000bfa6 in nxtask_start () at task/task_start.c:107
#20 0x00000000 in ?? ()
Backtrace stopped: frame did not save the PC
(gdb) p g_procfs_meminfo
$1 = (struct procfs_meminfo_entry_s *) 0x4ff5dac0
(gdb) p *g_procfs_meminfo
$2 = {name = 0x40080790 "Umem", heap = 0x4ff5d938, next = 0x4ff5dac0, mallinfo = 0x0, memdump = 0x0, refs = 2}
(gdb)
$3 = {name = 0x40080790 "Umem", heap = 0x4ff5d938, next = 0x4ff5dac0, mallinfo = 0x0, memdump = 0x0, refs = 2}
(gdb)
$4 = {name = 0x40080790 "Umem", heap = 0x4ff5d938, next = 0x4ff5dac0, mallinfo = 0x0, memdump = 0x0, refs = 2}
(gdb)
$5 = {name = 0x40080790 "Umem", heap = 0x4ff5d938, next = 0x4ff5dac0, mallinfo = 0x0, memdump = 0x0, refs = 2}
(gdb)
$6 = {name = 0x40080790 "Umem", heap = 0x4ff5d938, next = 0x4ff5dac0, mallinfo = 0x0, memdump = 0x0, refs = 2}
(gdb)
$7 = {name = 0x40080790 "Umem", heap = 0x4ff5d938, next = 0x4ff5dac0, mallinfo = 0x0, memdump = 0x0, refs = 2}
(gdb)
$8 = {name = 0x40080790 "Umem", heap = 0x4ff5d938, next = 0x4ff5dac0, mallinfo = 0x0, memdump = 0x0, refs = 2}
(gdb) p g_procfs_meminfo->next
$9 = (struct procfs_meminfo_entry_s *) 0x4ff5dac0
(gdb)   p g_procfs_meminfo->next == g_procfs_meminfo
$10 = 1
(gdb)
```
