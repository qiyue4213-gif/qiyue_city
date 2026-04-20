#!/usr/bin/env python3
"""
今日头条视频音频提取工具（简化版）
流程：拦截音频流 → 直接下载 → 转录 → 保存Markdown
"""

import asyncio
import os
import sys
import re
import tempfile
import subprocess
from datetime import datetime

from playwright.async_api import async_playwright

class ToutiaoAudioExtractor:
    def __init__(self):
        self.audio_urls = []
        
    async def get_audio_url(self, share_url):
        """使用Playwright获取音频流地址"""
        print(f"🔍 正在解析音频流: {share_url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                locale='zh-CN',
            )
            
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = { runtime: {} };
            """)
            
            page = await context.new_page()
            
            # 只拦截音频流
            async def handle_response(response):
                url = response.url
                if 'toutiaovod.com' in url and 'media-audio' in url:
                    self.audio_urls.append(url)
                    print(f"🔊 发现音频流: {url[:80]}...")
            
            page.on("response", lambda r: asyncio.create_task(handle_response(r)))
            
            # 访问页面
            await page.goto(share_url, wait_until='networkidle', timeout=60000)
            await asyncio.sleep(2)
            
            # 点击播放触发音频加载
            try:
                video = await page.query_selector('video')
                if video:
                    await video.click()
                    await asyncio.sleep(3)
            except:
                pass
            
            await browser.close()
        
        return self.audio_urls[0] if self.audio_urls else None
    
    def download_audio(self, audio_url, output_path):
        """直接下载音频流"""
        print(f"\n📥 正在下载音频...")
        
        # 方案1: 直接用ffmpeg从URL提取（推荐，无需先下载）
        cmd = [
            'ffmpeg', '-i', audio_url,
            '-vn',                    # 去掉视频
            '-c:a', 'pcm_s16le',      # PCM 16位
            '-ar', '16000',           # 16kHz采样率
            '-ac', '1',               # 单声道
            '-y',                     # 覆盖
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ 音频提取完成: {os.path.getsize(output_path)/1024/1024:.1f} MB")
        
        return output_path
    
    def transcribe(self, audio_path):
        """语音识别"""
        print("\n🗣️ 正在进行语音识别...")
        
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
        
        from faster_whisper import WhisperModel
        
        model = WhisperModel('base', device='cpu', compute_type='int8')
        segments, info = model.transcribe(audio_path, language='zh', beam_size=5)
        
        print(f"✅ 检测到语言: {info.language}")
        
        results = []
        full_text = []
        for segment in segments:
            mins, secs = divmod(int(segment.start), 60)
            time_str = f"{mins:02d}:{secs:02d}"
            text = segment.text.strip()
            results.append({'time': time_str, 'text': text})
            full_text.append(text)
        
        return results, ' '.join(full_text)
    
    def generate_markdown(self, title, video_url, transcript_data, full_text):
        """生成Markdown"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        md = f"# {title}\n\n"
        md += f"> **原视频链接：** [点击观看]({video_url})\n"
        md += f"> **平台：** 今日头条\n"
        md += f"> **转录时间：** {date_str}\n\n"
        md += "---\n\n## 转录内容\n\n"
        
        for item in transcript_data:
            md += f"[{item['time']}] {item['text']}\n\n"
        
        md += "\n---\n\n## 全文\n\n"
        md += full_text
        md += "\n\n---\n\n*AI自动转录*\n"
        
        return md
    
    async def process(self, share_url, title=None):
        """完整流程"""
        print("="*60)
        print("🎬 头条视频音频提取")
        print("="*60)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. 获取音频流URL
            audio_url = await self.get_audio_url(share_url)
            
            if not audio_url:
                print("❌ 未找到音频流")
                return None
            
            # 2. 直接提取音频到WAV（ffmpeg直接从URL读取）
            wav_path = os.path.join(temp_dir, 'audio.wav')
            self.download_audio(audio_url, wav_path)
            
            # 3. 语音识别
            transcript_data, full_text = self.transcribe(wav_path)
            
            # 4. 生成Markdown
            if not title:
                title = "今日头条视频转录"
            
            markdown = self.generate_markdown(title, share_url, transcript_data, full_text)
            
            print(f"\n✅ 完成！共 {len(transcript_data)} 段")
            
            return {
                'title': title,
                'markdown': markdown,
                'segments': len(transcript_data)
            }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 toutiao_audio_extractor.py <头条链接> [标题]")
        sys.exit(1)
    
    url = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    
    extractor = ToutiaoAudioExtractor()
    result = asyncio.run(extractor.process(url, title))
    
    if result:
        # 保存
        safe_title = re.sub(r'[^\w\u4e00-\u9fff]+', '_', result['title'])[:50]
        filename = f"/tmp/{safe_title}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result['markdown'])
        print(f"\n📄 已保存: {filename}")
    else:
        print("\n❌ 失败")
        sys.exit(1)
