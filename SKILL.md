---
name: content-processor
description: 统一信息处理流程，支持视频链接转录、网页文章抓取、图片OCR识别。当用户发送链接或图片时自动触发：视频链接（今日头条/抖音/B站等）→ 语音识别转录；文章链接 → 正文抓取；图片 → OCR识别。最终输出结构化Markdown保存至飞书知识库。
---

# 内容处理器 (Content Processor)

统一信息处理工作流，自动识别输入类型并路由到对应处理流程。

---

## 核心原则

**只提取整理，不添加主观内容**

- ✅ **基于信息本身**：严格依据原始内容进行处理
- ❌ **不添加主观认知**：不加入个人理解、评价或观点
- ❌ **不推测**：不对原文未提及的内容进行推断
- ❌ **不想象**：不补充原文未明确的信息
- ✅ **忠实原文**：保持原意，仅做格式整理和结构化

> 重要：输出内容必须完全可追溯至原始输入，任何非原始信息都需明确标注为"推测"或"备注"。

---

## 触发条件

收到以下类型输入时自动执行：
- **视频链接**：含 `toutiao.com` / `ixigua.com` / `douyin.com` / `bilibili.com` / `youtube.com`
- **文章链接**：知乎、公众号、博客等普通网页
- **图片**：`.jpg` / `.png` / `.gif` / `.webp` 等格式

---

## 处理流程

```
用户输入 → 类型识别 → 路由处理 → 内容提取 → 整理输出 → 保存飞书
```

### 类型识别规则

| 输入类型 | 识别规则 |
|----------|----------|
| 视频链接 | URL含 `video/` 或短链 `is/`，域名含视频平台 |
| 文章链接 | 普通网页链接 |
| 图片 | 图片扩展名或本地图片路径 |

### 路由处理

#### 1️⃣ 视频链接 → 语音转录

```
视频链接 → Playwright拦截音频流 → ffmpeg提取音频 → Whisper语音识别 → 转录文本 → 人工整理 → Markdown → 飞书
```

**执行脚本**：
```bash
python3 skills/content-processor/scripts/toutiao_audio_extractor.py "<链接>" "<标题>"
```

**后续处理**：
- 转录完成后进行人工整理（修正识别错误、分章节、提取要点）
- 只保存人工整理版，不包含原始转录文本对照

#### 2️⃣ 文章链接 → 正文抓取

```
网页链接 → browser抓取 → 提取正文/标题/作者 → 生成Markdown → 飞书
```

**执行方式**：使用 `browser` 工具抓取页面内容，提取结构化信息

#### 3️⃣ 图片 → OCR识别

```
图片 → Tesseract OCR → 提取文字 → Markdown → 飞书
```

**执行命令**：
```bash
tesseract <图片路径> stdout -l chi_sim+eng
```

---

## 输出规范

### 保存位置

**飞书 Wiki 收集箱节点**：`QwYuwDPBFidUxOkjYB3cSs9jn9c`

### 文档格式

| 属性 | 规则 |
|------|------|
| 标题格式 | `[YYYY-MM-DD] 原标题` |
| 内容结构 | 标题 + 来源信息 + 正文 + 关键要点 |
| 视频处理 | 只保存人工整理版，不包含原始转录对照 |

### 内容模板

```markdown
# [标题]

> **来源：** [平台名](原文链接)  
> **作者：** xxx  
> **处理时间：** YYYY-MM-DD

---

## 内容概述

[简介]

---

## 详细内容

[正文]

---

## 关键要点

1. 要点1
2. 要点2
3. 要点3

---

*AI自动处理*
```

---

## 更新收集箱目录

保存文档后**必须**更新收集箱主页面目录，添加新记录：

```markdown
| 序号 | 文件名 | 处理时间 | 链接 |
|------|--------|----------|------|
| N | [YYYY-MM-DD] 标题 | YYYY-MM-DD | [查看](url) |
```

---

## 脚本说明

### toutiao_audio_extractor.py

**功能**：今日头条视频音频提取与语音识别

**流程**：
1. Playwright 拦截音频流地址
2. ffmpeg 直接提取音频（无需下载视频）
3. faster-whisper 语音识别
4. 生成时间戳格式的转录文本

**依赖**：
- Playwright
- ffmpeg
- faster-whisper

---

## 完整执行示例

### 处理视频链接

```bash
# 1. 执行转录
python3 skills/content-processor/scripts/toutiao_audio_extractor.py \
  "https://m.toutiao.com/is/xxxxx/" \
  "视频标题"

# 2. 人工整理转录文本
# 3. 保存到飞书
# 4. 更新收集箱目录
```

---

## 删除文档

目前飞书 API **不支持**直接删除 Wiki 节点（返回 404）。如需删除文档，请手动操作：

### 手动删除步骤

1. 打开飞书 Wiki 收集箱：https://www.feishu.cn/wiki/QwYuwDPBFidUxOkjYB3cSs9jn9c
2. 找到要删除的文档
3. 点击文档右上角「···」→「删除」

### API 删除脚本（备用）

如果将来开通权限，可使用以下脚本：

```bash
# 删除云文档
python3 skills/content-processor/scripts/delete_feishu_doc.py doc <document_id>

# 删除Wiki节点
python3 skills/content-processor/scripts/delete_feishu_doc.py wiki <space_id> <node_token>
```

---

**创建时间**: 2026-04-10  
**版本**: v1.1
