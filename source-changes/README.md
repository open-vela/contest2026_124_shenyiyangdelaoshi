# 源码归档与还原

这是当前工作区的真实源码增量，不是上游合入声明。分支为 `dev-ai-contest-2026`，固件和公共库的补丁均在本专属仓归档。

`versions.json` 记录基线提交、原本地 HEAD、新文件列表和现有镜像校验值。

## 归属

`nuttx/inherited-port.mbox` 保留已有 ESP32-P4 移植系列的作者和提交记录；原工作文档参考 open-vela/nuttx PR #342。不能将整套上游架构、HAL、摄像头、音频等支持算作本作品原创或实测成果。

`working-tree.patch` 是各仓当前相对于 HEAD 的增量。`nuttx/base-to-working.patch` 则是从公开比赛基线到当前工作树的组合还原补丁，已包含继承的移植代码；**与 inherited-port.mbox 二选一，不要重复应用**。作者归属见 `inherited-authors.txt`。

## 在独立工作区还原

1. 用比赛 manifest 获取 openvela 工作区；在 nuttx、apps、packages/ai_agent 中检出 `versions.json` 的 `base`。若 manifest 未含 ai_agent，单独克隆 `https://github.com/open-vela/packages_ai_agent` 到该路径。
2. 核对各仓干净且基线一致，不在含未保存改动的工作区应用。
3. nuttx 应用 `git apply <本仓>/source-changes/nuttx/base-to-working.patch`。
4. apps、packages/ai_agent 分别应用对应目录的 `working-tree.patch`。
5. 将各目录 `new-files/` 中的文件按相对路径放回相应仓，不能只应用跟踪文件补丁。
6. 当前实机镜像采用的完整配置为 `firmware.config`。它与 usbnet/defconfig 的 SmartFS 名称长度不一致；原样记录是为了可核对，不表示已消除差异。
7. 复现现有镜像配置时，用 `firmware.config` 作为 nuttx/.config 的起点，通过 NuttX 配置工具更新，再构建并检查实际差异。不要未经核对改动已格式化数据区的参数。

当前使用 RISC-V `riscv-none-elf-gcc`、esptool、cJSON 1.7.19、mbedTLS 3.4.0。原工作环境说明在上层工作区 `OPENVELA_ESP32P4_PORT_ENV.md`，正式评审前仍需完成独立目录干净构建验证。此处不声称“任意机器一键通过”。

公共仓改动还应按赛事规则提交相应 fork/PR，并把链接补入报告；归档补丁不能自动替代上游 review。
