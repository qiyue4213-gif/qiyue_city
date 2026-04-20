# Content Processor Skill

OpenClaw Agent Skill - 统一信息处理工具

## 功能

- **视频链接转录**：支持今日头条、抖音、B站等平台视频的语音识别
- **网页文章抓取**：自动提取正文内容
- **图片 OCR 识别**：提取图片中的文字

## 快速安装

```bash
# 复制到 OpenClaw 技能目录
cp -r content-processor ~/.agents/skills/

# 安装依赖
pip install playwright faster-whisper requests
playwright install chromium

# Ubuntu/Debian 系统依赖
sudo apt install ffmpeg tesseract-ocr tesseract-ocr-chi-sim
```

## 使用方式

安装后，OpenClaw 会自动识别技能。发送视频链接、文章链接或图片时，将自动触发处理流程。

## 文档

- [SKILL.md](SKILL.md) - 技能定义和使用说明
- [INSTALL.md](INSTALL.md) - 详细安装指南
- [QUICK-INSTALL.md](QUICK-INSTALL.md) - 快速安装指南

## 许可证

MIT License
