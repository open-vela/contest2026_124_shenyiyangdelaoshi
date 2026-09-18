# 作品介绍材料

本目录是 2026-09-16 的提交前补图稿。只生成文档，不修改固件；未伪造实机截图或测试通过记录。

## 直接使用

| 文件 | 用途 |
| --- | --- |
| `ESP32P4-openvela-AI-diagnostics.pptx` | 可编辑 PPT，16:9，13 页主讲 + 2 页答辩附录 |
| `project-introduction.docx` | 可编辑 Word 介绍文档 |
| `project-introduction.pdf` | 介绍文档阅读版，共 8 页 |
| `project-introduction.md` | 介绍文档纯文本源，方便版本审查 |
| `presentation-preview.pdf` | PPT 同源布局预览，共 15 页 |
| `slide-overview.png` | 全部幻灯片缩略图 |
| `previews/` | 每页 1600×900 预览 |
| `video-script-and-screenshots.md` | 每页旁白、补图要求与建议时长 |

PPT 的演讲者备注也有旁白。主讲建议合计 287 秒，加入真实录屏时应压缩旁白，最终视频不超过 5 分钟。附录不纳入主视频。

## 明天补图

| 页码 | 截图内容 | 需保留的证据 |
| --- | --- | --- |
| 1 | 板卡连接 | 板卡、USB、网线 |
| 6 | 真实工具问答 | 问题、结果、返回 `nsh>`；另附工具调用证据 |
| 7 | 启动栈定位 | 异常寄存器与修正后 `ps` 的栈使用量 |
| 8 | 堆布局定位 | 旧 `next == self` 记录与修正后 `free` |
| 12 | 最终回归 | DHCP、日期、连续请求、`free` |

删除灰色占位框与其中提示文字，再插入实机截图，按原框裁剪。PPT 中的文字、框和架构元素均可编辑。不要用示意输出替代实机证据，不要录入密钥。

补图与人工修改后，请从 PowerPoint / Word 重新导出最终 PDF。目录内 PDF、PNG 是生成器输出的同源预览，不是 Office 原生渲染，也不会随人工修改自动更新。生成时采用微软雅黑，交付前请用实际录制电脑打开确认字体与换行。

## 内容边界

- 不声称首个适配，不评价其他团队；区分现有 NuttX / Espressif 基础、openvela Agent 框架与本项目增量。
- 工作量以工程范围、实机排障链和当前文件改动快照呈现，不把上游整体代码算成原创。
- 已有实机反馈与待测试项目分开；开发 Skill、日志和 PR 尚未完成的，不标为已完成。
- 当前镜像的 SmartFS 名称长度为 16，仓内目标 defconfig 为 48。正式发布前必须结合数据区格式对齐并重新验证，本次没有替用户修改配置。
- 当前 TLS `VERIFY_OPTIONAL` 未完成生产级证书验证。网络工具只读接口状态，不证明互联网可达。

## 再生成（会覆盖生成文件）

先备份手工编辑的 PPT / Word；重新生成会丢失人工补图和内容修改。

依赖：Python 3、python-pptx、python-docx、reportlab、Pillow。字体路径在 `build_materials.py` 中，默认使用 WSL 可读取的 Windows 微软雅黑和黑体。字体文件不随材料分发。

当前环境命令：

```bash
PYTHONPATH=/tmp/contest-doc-libs python3 build_materials.py
```

内容与布局源文件为 `build_materials.py`；`layout-data.json` 是生成的布局数据，不是手工编辑入口。换机器须重新安装依赖并调整字体路径。

## 校验口径

生成器检查所有 PPT 元素在画布内，并按实际字体测量换行与文本框高度。生成后校验 PPT 页数、演讲者备注、DOCX/PPTX 包完整性、PDF 页数与文本可提取性。原生 Office 渲染仍需在录制电脑上检查。
