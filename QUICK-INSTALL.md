# Content Processor Skill - 快速安装指南

> ⚡ 最快方式：直接复制粘贴即可使用

---

## 🚀 最快安装方式（30秒）

### 步骤 1：一键复制命令

在目标 OpenClaw 终端执行：

```bash
# 创建目录并下载
cd /tmp && \
curl -fsSL "https://raw.githubusercontent.com/yourname/content-processor-skill/main/content-processor.tar.gz" -o cp.tar.gz && \
tar -xzf cp.tar.gz -C ~/.agents/skills/ && \
echo "✅ 安装完成！"
```

### 步骤 2：验证安装

```bash
ls ~/.agents/skills/content-processor/
# 应看到：INSTALL.md  QUICK-INSTALL.md  SKILL.md  scripts/
```

### 步骤 3：安装依赖

```bash
# Python 依赖
pip install playwright faster-whisper requests -q
playwright install chromium

# 系统依赖（Ubuntu/Debian）
sudo apt install ffmpeg tesseract-ocr -y
```

---

## 📋 完整手动安装（无网络时）

如果无法下载，按以下步骤手动创建：

### 1. 创建目录结构

```bash
mkdir -p ~/.agents/skills/content-processor/scripts
touch ~/.agents/skills/content-processor/scripts/__init__.py
```

### 2. 复制 SKILL.md 内容

将下面整个代码块内容保存到 `~/.agents/skills/content-processor/SKILL.md`：

<details>
<summary>点击展开 SKILL.md 完整内容</summary>

```markdown
---
name: content-processor
description: 统一信息处理流程，支持视频链接转录、网页文章抓取、图片OCR识别。当用户发送链接或图片时自动触发：视频链接（今日头条/抖音/B站等）→ 语音识别转录；文章链接 → 正文抓取；图片 → OCR识别。最终输出结构化Markdown保存至飞书知识库。
---

# 内容处理器 (Content Processor)

统一信息处理工作流，自动识别输入类型并路由到对应处理流程。

## 核心原则

**只提取整理，不添加主观内容**

- ✅ **基于信息本身**：严格依据原始内容进行处理
- ❌ **不添加主观认知**：不加入个人理解、评价或观点
- ❌ **不推测**：不对原文未提及的内容进行推断
- ❌ **不想象**：不补充原文未明确的信息
- ✅ **忠实原文**：保持原意，仅做格式整理和结构化

## 触发条件

收到以下类型输入时自动执行：
- **视频链接**：含 `toutiao.com` / `ixigua.com` / `douyin.com` / `bilibili.com` / `youtube.com`
- **文章链接**：知乎、公众号、博客等普通网页
- **图片**：`.jpg` / `.png` / `.gif` / `.webp` 等格式

## 处理流程

### 1️⃣ 视频链接 → 语音转录

```
视频链接 → Playwright拦截音频流 → ffmpeg提取音频 → Whisper语音识别 → 转录文本 → Markdown → 飞书
```

### 2️⃣ 文章链接 → 正文抓取

```
网页链接 → browser抓取 → 提取正文/标题/作者 → 生成Markdown → 飞书
```

### 3️⃣ 图片 → OCR识别

```
图片 → Tesseract OCR → 提取文字 → Markdown → 飞书
```

## 输出规范

### 保存位置

**飞书 Wiki 收集箱节点**：`QwYuwDPBFidUxOkjYB3cSs9jn9c`

### 文档格式

| 属性 | 规则 |
|------|------|
| 标题格式 | `[YYYY-MM-DD] 原标题` |
| 内容结构 | 标题 + 来源信息 + 正文 + 关键要点 |

---

**创建时间**: 2026-04-10  
**版本**: v1.1
```

</details>

---

## 📦 文件清单（可复制）

| 文件名 | 用途 | 位置 |
|--------|------|------|
| `SKILL.md` | 技能定义文档 | `~/.agents/skills/content-processor/` |
| `INSTALL.md` | 详细安装说明 | `~/.agents/skills/content-processor/` |
| `scripts/toutiao_audio_extractor.py` | 视频转录脚本 | `~/.agents/skills/content-processor/scripts/` |
| `scripts/save_to_feishu.py` | 飞书保存脚本 | `~/.agents/skills/content-processor/scripts/` |
| `scripts/transcript_post_processor.py` | 转录后处理 | `~/.agents/skills/content-processor/scripts/` |
| `scripts/delete_feishu_doc.py` | 文档删除（备用） | `~/.agents/skills/content-processor/scripts/` |

---

## 🔧 依赖检查清单

安装后执行以下命令验证：

```bash
echo "=== 检查 Python ==="
python3 --version

echo "=== 检查 Playwright ==="
pip show playwright | grep Version

echo "=== 检查 ffmpeg ==="
ffmpeg -version 2>&1 | head -1

echo "=== 检查 Tesseract ==="
tesseract --version 2>&1 | head -1

echo "=== 检查技能文件 ==="
ls -la ~/.agents/skills/content-processor/
```

---

## ✅ 安装完成测试

发送以下内容给 OpenClaw 测试：

```
https://www.example.com/article
```

如果技能正常工作，OpenClaw 会：
1. 识别为文章链接
2. 自动抓取内容
3. 整理为 Markdown
4. 保存到飞书（如果配置了）

---

## 🆘 常见问题

### Q1: OpenClaw 不识别技能？
**A:** 重启 OpenClaw 或检查文件路径是否正确

### Q2: 脚本执行报错？
**A:** 检查依赖是否全部安装，特别是 `playwright install chromium`

### Q3: 无法保存到飞书？
**A:** 需要配置飞书 App ID 和 Secret

---

## 📞 支持

- 查看 `INSTALL.md` 获取详细说明
- 查看 `SKILL.md` 了解使用方式
- 检查 OpenClaw 日志排查问题

---

**版本**: v1.1  
**更新**: 2026-04-18