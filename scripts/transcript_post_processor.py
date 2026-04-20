#!/usr/bin/env python3
"""
转录文本后处理器
功能：口语化文本 → 结构化Markdown
"""

import re
import json
from datetime import datetime

class TranscriptPostProcessor:
    """转录文本后处理器"""
    
    def __init__(self, transcript_data, full_text):
        self.transcript = transcript_data  # [{'time': '00:00', 'text': '...'}, ...]
        self.full_text = full_text
        self.segments = []
        
    def merge_short_sentences(self, min_length=20):
        """合并短句，形成完整段落"""
        print("📝 合并短句...")
        
        merged = []
        current_para = {"text": "", "start_time": "", "end_time": ""}
        
        for i, item in enumerate(self.transcript):
            text = item['text'].strip()
            
            # 跳过语气词
            if text in ['嗯', '啊', '那个', '就是', '然后', '所以']:
                continue
                
            if not current_para["text"]:
                current_para["start_time"] = item['time']
                current_para["text"] = text
            else:
                # 判断是否继续当前段落
                if len(current_para["text"]) < min_length:
                    current_para["text"] += " " + text
                else:
                    # 结束当前段落
                    current_para["end_time"] = item['time']
                    merged.append(current_para.copy())
                    # 开始新段落
                    current_para = {"text": text, "start_time": item['time'], "end_time": ""}
        
        # 添加最后一个段落
        if current_para["text"]:
            current_para["end_time"] = self.transcript[-1]['time']
            merged.append(current_para)
        
        self.segments = merged
        print(f"✅ 合并为 {len(merged)} 个段落")
        return merged
    
    def detect_chapters(self):
        """自动检测章节/主题"""
        print("📑 检测章节结构...")
        
        # 章节标记词
        chapter_markers = [
            '第一', '第二', '第三', '第四', '第五', '第六', '第七', '第八', '第九', '第十',
            '首先', '其次', '然后', '最后', '总结', '结论',
            '接下来', '下面我们', '我们来看', '比如说'
        ]
        
        chapters = []
        current_chapter = {"title": "开场", "content": [], "start": ""}
        
        for segment in self.segments:
            text = segment['text']
            found_marker = False
            
            # 检查是否是新章节开头
            for marker in chapter_markers:
                if text.startswith(marker) or f'，{marker}' in text[:10]:
                    # 保存上一章节
                    if current_chapter["content"]:
                        chapters.append(current_chapter.copy())
                    
                    # 提取章节标题（前15个字）
                    title = text[:15] + "..." if len(text) > 15 else text
                    current_chapter = {
                        "title": title,
                        "content": [text],
                        "start": segment['start_time']
                    }
                    found_marker = True
                    break
            
            if not found_marker:
                current_chapter["content"].append(text)
        
        # 添加最后一个章节
        if current_chapter["content"]:
            chapters.append(current_chapter)
        
        print(f"✅ 检测到 {len(chapters)} 个章节")
        return chapters
    
    def extract_key_points(self, text):
        """提取关键要点"""
        print("🔑 提取关键要点...")
        
        key_points = []
        
        # 按句号分割
        sentences = re.split(r'[。！？]', text)
        
        for sent in sentences:
            sent = sent.strip()
            # 提取包含关键信息的句子（长度适中）
            if 15 < len(sent) < 80 and not sent.startswith(('嗯', '啊', '那个')):
                # 检查是否包含实质性内容
                if any(keyword in sent for keyword in ['是', '需要', '必须', '应该', '可以', '方法', '技巧', '重点', '核心']):
                    key_points.append(sent)
        
        # 去重并限制数量
        unique_points = list(dict.fromkeys(key_points))[:10]
        print(f"✅ 提取 {len(unique_points)} 个要点")
        return unique_points
    
    def clean_text(self, text):
        """清理口语化表达"""
        # 去除重复词
        text = re.sub(r'(然后|就是|那个|这个|嗯|啊)\s*', '', text)
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text)
        # 去除语气词开头
        text = re.sub(r'^(嗯|啊|那个|就是|然后)[，,]?', '', text)
        return text.strip()
    
    def generate_structured_markdown(self, title, video_url, chapters, key_points):
        """生成结构化的Markdown"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        md = f"# {title}\n\n"
        md += f"> **原视频：** [点击观看]({video_url})\n"
        md += f"> **平台：** 今日头条\n"
        md += f"> **转录时间：** {date_str}\n\n"
        
        # 目录
        md += "---\n\n## 📋 目录\n\n"
        for i, chapter in enumerate(chapters, 1):
            md += f"{i}. [{chapter['title']}](#chapter-{i})\n"
        md += f"\n{len(chapters)+1}. [关键要点](#key-points)\n"
        
        # 章节内容
        md += "\n---\n\n## 📝 详细内容\n\n"
        for i, chapter in enumerate(chapters, 1):
            md += f"<a id='chapter-{i}'></a>\n"
            md += f"### {i}. {chapter['title']}\n\n"
            
            # 合并内容并清理
            content = " ".join(chapter['content'])
            content = self.clean_text(content)
            
            # 分段显示
            paragraphs = self.split_into_paragraphs(content)
            for para in paragraphs:
                md += f"{para}\n\n"
        
        # 关键要点
        md += "<a id='key-points'></a>\n"
        md += "---\n\n## 🔑 关键要点\n\n"
        for i, point in enumerate(key_points, 1):
            point = self.clean_text(point)
            if point:
                md += f"{i}. {point}\n\n"
        
        md += "---\n\n*AI自动转录并结构化处理*\n"
        
        return md
    
    def split_into_paragraphs(self, text, max_length=200):
        """将长文本分成段落"""
        if len(text) <= max_length:
            return [text]
        
        # 按语义分割（寻找句号、分号等）
        sentences = re.split(r'([。；])', text)
        paragraphs = []
        current = ""
        
        for sent in sentences:
            if len(current) + len(sent) < max_length:
                current += sent
            else:
                if current:
                    paragraphs.append(current)
                current = sent
        
        if current:
            paragraphs.append(current)
        
        return paragraphs
    
    def process(self, title, video_url):
        """完整处理流程"""
        print("="*60)
        print("🔄 转录文本后处理")
        print("="*60)
        
        # 1. 合并短句
        self.merge_short_sentences(min_length=30)
        
        # 2. 检测章节
        chapters = self.detect_chapters()
        
        # 3. 提取关键要点
        key_points = self.extract_key_points(self.full_text)
        
        # 4. 生成结构化Markdown
        markdown = self.generate_structured_markdown(title, video_url, chapters, key_points)
        
        print(f"\n✅ 处理完成！")
        print(f"   - 章节数: {len(chapters)}")
        print(f"   - 关键要点: {len(key_points)}")
        print(f"   - 最终长度: {len(markdown)} 字符")
        
        return markdown


def process_transcript(transcript_json, title, video_url):
    """处理转录结果的主函数"""
    # 解析转录数据
    transcript_data = json.loads(transcript_json) if isinstance(transcript_json, str) else transcript_json
    
    # 提取全文
    full_text = " ".join([item['text'] for item in transcript_data])
    
    # 后处理
    processor = TranscriptPostProcessor(transcript_data, full_text)
    markdown = processor.process(title, video_url)
    
    return markdown


if __name__ == "__main__":
    # 示例用法
    example_transcript = [
        {"time": "00:00", "text": "嗯，大家好啊"},
        {"time": "00:02", "text": "今天我们来聊一个话题"},
        {"time": "00:05", "text": "第一点呢，就是要做好准备工作"},
        {"time": "00:10", "text": "那个，准备工作很重要的"},
        {"time": "00:15", "text": "第二，我们需要注意细节"},
    ]
    
    full_text = " ".join([item['text'] for item in example_transcript])
    
    processor = TranscriptPostProcessor(example_transcript, full_text)
    result = processor.process("示例视频", "https://example.com")
    
    print("\n" + "="*60)
    print(result)
