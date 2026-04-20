# Content Processor Skill 安装指南

> 本技能用于统一信息处理：视频链接转录、网页文章抓取、图片OCR识别

---

## 📦 方式一：直接复制安装（推荐）

### 步骤 1：复制技能文件

在你的 OpenClaw 工作空间中执行：

```bash
# 创建 skills 目录（如果不存在）
mkdir -p ~/.agents/skills

# 复制 content-processor 技能
# 方式 A：从其他 OpenClaw 实例复制（在同一服务器）
cp -r /path/to/other/openclaw/.agents/skills/content-processor ~/.agents/skills/

# 方式 B：解压下载的压缩包
tar -xzf content-processor-v1.1.tar.gz -C ~/.agents/skills/
```

### 步骤 2：验证安装

```bash
# 检查文件结构
ls -la ~/.agents/skills/content-processor/
# 应输出：
# SKILL.md
# INSTALL.md
# QUICK-INSTALL.md
# scripts/
#   ├── article_extractor.py
#   ├── delete_feishu_doc.py
#   ├── save_to_feishu.py
#   ├── toutiao_audio_extractor.py
#   └── transcript_post_processor.py
```

---

## 🔧 方式二：手动创建文件

如果无法直接复制，可以手动创建以下文件结构：

### 目录结构

```
~/.agents/skills/
└── content-processor/
    ├── SKILL.md              # 技能主文档
    └── scripts/
        ├── __init__.py       # 空文件即可
        ├── delete_feishu_doc.py
        ├── save_to_feishu.py
        ├── toutiao_audio_extractor.py
        └── transcript_post_processor.py
```

### 创建命令

```bash
mkdir -p ~/.agents/skills/content-processor/scripts
touch ~/.agents/skills/content-processor/scripts/__init__.py

# 然后将 SKILL.md 和各脚本内容复制到对应位置
```

---

## 📋 依赖安装

本技能需要以下依赖，请根据你的系统选择安装方式：

### 1. Python 依赖

```bash
# 安装必要的 Python 包
pip install playwright faster-whisper requests beautifulsoup4 lxml

# 安装 Playwright 浏览器
playwright install chromium
```

### 2. 系统依赖

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y ffmpeg tesseract-ocr tesseract-ocr-chi-sim
```

**macOS:**
```bash
brew install ffmpeg tesseract
```

**CentOS/RHEL:**
```bash
sudo yum install ffmpeg tesseract tesseract-langpack-chi_sim
```

### 3. 验证依赖

```bash
# 检查各工具是否安装成功
python3 --version
playwright --version
ffmpeg -version | head -1
tesseract --version
```

---

## ⚙️ 配置说明

### 飞书配置（用于保存到知识库）

如果你需要将处理结果保存到飞书 Wiki，需要配置飞书凭证：

```bash
# 设置环境变量（添加到 ~/.bashrc 或 ~/.zshrc）
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
```

或者修改 `scripts/save_to_feishu.py` 中的默认配置。

### 知识库节点 ID

默认保存到收集箱，如需修改，编辑各脚本中的 `WIKI_NODE_TOKEN` 变量。

---

## 🚀 使用方法

安装完成后，OpenClaw 会自动识别技能。你可以通过以下方式触发：

### 1. 发送视频链接

当用户发送今日头条/抖音/B站等视频链接时，自动触发转录流程。

### 2. 发送文章链接

发送普通网页链接，自动抓取正文内容。

### 3. 手动执行脚本

```bash
# 视频转录
python3 ~/.agents/skills/content-processor/scripts/toutiao_audio_extractor.py \
  "https://m.toutiao.com/is/xxxxx/" \
  "视频标题"

# 保存到飞书
python3 ~/.agents/skills/content-processor/scripts/save_to_feishu.py \
  /path/to/processed/content.md \
  "文档标题"
```

---

## 📝 技能文件清单

| 文件 | 大小 | 用途 |
|------|------|------|
| `SKILL.md` | ~8KB | 技能定义和使用说明 |
| `INSTALL.md` | ~5KB | 详细安装指南 |
| `QUICK-INSTALL.md` | ~5KB | 快速安装指南 |
| `scripts/article_extractor.py` | ~9KB | 文章链接抓取和正文提取 |
| `scripts/delete_feishu_doc.py` | ~2KB | 删除飞书文档（备用） |
| `scripts/save_to_feishu.py` | ~5KB | 保存内容到飞书 Wiki |
| `scripts/toutiao_audio_extractor.py` | ~8KB | 今日头条视频音频提取和转录 |
| `scripts/transcript_post_processor.py` | ~3KB | 转录文本后处理 |

**总计：** ~40KB，纯文本文件

---

## 🔍 故障排查

### 问题 1：Playwright 无法启动浏览器

**解决：**
```bash
# 重新安装浏览器
playwright install --with-deps chromium
```

### 问题 2：找不到 tesseract

**解决：**
```bash
# 检查安装
which tesseract

# 如果未安装，根据系统安装
# Ubuntu
sudo apt install tesseract-ocr

# macOS
brew install tesseract
```

### 问题 3：ffmpeg 报错

**解决：**
```bash
# 检查版本
ffmpeg -version

# 如果版本太旧，升级到 4.0+
```

### 问题 4：技能未被 OpenClaw 识别

**解决：**
```bash
# 检查文件路径
ls -la ~/.agents/skills/content-processor/SKILL.md

# 重启 OpenClaw 或刷新技能列表
# 某些 OpenClaw 版本需要重启服务
```

---

## 📞 获取帮助

1. 查看 SKILL.md 获取详细使用说明
2. 检查各脚本头部的注释了解参数用法
3. 查看 OpenClaw 日志排查问题

---

## 📄 许可证

本技能为内部使用，遵循项目相关规定。

---

**版本：** v1.1  
**最后更新：** 2026-04-18