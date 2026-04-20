#!/usr/bin/env python3
"""
文章链接抓取工具
支持知乎、公众号、简书、CSDN、掘金等平台
"""

import sys
import re
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse


def extract_content_by_rules(html_content, url):
    """
    根据不同平台规则提取正文内容
    """
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 移除脚本和样式
    for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
        script.decompose()
    
    # 识别平台
    domain = urlparse(url).netloc.lower()
    
    title = ""
    author = ""
    content = ""
    
    # 知乎
    if "zhihu.com" in domain:
        # 标题
        title_elem = soup.select_one('h1.Post-Title, h1.QuestionHeader-title, h1[class*="title"]')
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        # 作者
        author_elem = soup.select_one('.AuthorInfo-name, .UserLink-link, [class*="author"]')
        if author_elem:
            author = author_elem.get_text(strip=True)
        
        # 正文
        content_elem = soup.select_one('.Post-RichTextContainer, .RichContent-inner, .QuestionAnswer-content')
        if content_elem:
            content = content_elem.get_text(separator='\n', strip=True)
    
    # 公众号
    elif "mp.weixin.qq.com" in domain:
        title_elem = soup.select_one('#activity_name, .rich_media_title')
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        author_elem = soup.select_one('#js_name, .profile_nickname')
        if author_elem:
            author = author_elem.get_text(strip=True)
        
        content_elem = soup.select_one('#js_content, .rich_media_content')
        if content_elem:
            # 保留段落结构
            paragraphs = content_elem.find_all(['p', 'section'])
            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
    
    # 简书
    elif "jianshu.com" in domain:
        title_elem = soup.select_one('h1._1RuRku, h1.title')
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        author_elem = soup.select_one('.IWpYNd, .author .name')
        if author_elem:
            author = author_elem.get_text(strip=True)
        
        content_elem = soup.select_one('article._2rhmJa, .show-content')
        if content_elem:
            content = content_elem.get_text(separator='\n', strip=True)
    
    # CSDN
    elif "csdn.net" in domain or "blog.csdn.net" in domain:
        title_elem = soup.select_one('#articleContentId, .title-article, h1')
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        author_elem = soup.select_one('.profile-intro-name, .user-info .name, #uid')
        if author_elem:
            author = author_elem.get_text(strip=True)
        
        content_elem = soup.select_one('#content_views, .blog-content-box article, .article-content')
        if content_elem:
            content = content_elem.get_text(separator='\n', strip=True)
    
    # 掘金
    elif "juejin.cn" in domain:
        title_elem = soup.select_one('h1.article-title, h1.title')
        if title_elem:
            title = title_elem.get_text(strip=True)
        
        author_elem = soup.select_one('.username, .author-name')
        if author_elem:
            author = author_elem.get_text(strip=True)
        
        content_elem = soup.select_one('.article-content, .markdown-body, article')
        if content_elem:
            content = content_elem.get_text(separator='\n', strip=True)
    
    # 通用规则（未匹配到特定平台时）
    if not content:
        # 尝试常见的正文容器
        selectors = [
            'article',
            'main',
            '[class*="content"]',
            '[class*="article"]',
            '[class*="post"]',
            '.entry-content',
            '.post-content',
            '#content',
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and len(elem.get_text(strip=True)) > 200:
                content = elem.get_text(separator='\n', strip=True)
                break
        
        # 如果还是没找到，尝试最长的段落集合
        if not content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
    
    # 提取标题（通用）
    if not title:
        title_elem = soup.select_one('h1, title')
        if title_elem:
            title = title_elem.get_text(strip=True)
    
    return title, author, content


def clean_content(text):
    """
    清理内容，移除多余空白和广告文字
    """
    # 移除多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 移除常见广告词
    ad_patterns = [
        r'扫码关注.*?公众号',
        r'点击.*?(关注|订阅)',
        r'本文首发于',
        r'转载请注明出处',
        r'文/.*?编辑/',
        r'原标题：',
    ]
    
    for pattern in ad_patterns:
        text = re.sub(pattern, '', text)
    
    return text.strip()


def generate_markdown(title, author, url, content):
    """
    生成 Markdown 格式输出
    """
    from datetime import datetime
    
    md = f"""# {title}

> **来源：** [{urlparse(url).netloc}]({url})
"""
    if author:
        md += f"> **作者：** {author}\n"
    
    md += f"> **处理时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    md += "---\n\n"
    
    # 分段处理
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        if para.strip():
            md += f"{para.strip()}\n\n"
    
    md += "\n---\n\n*AI自动处理*"
    
    return md


async def extract_article(url, output_file=None, save_to_feishu=False):
    """
    抓取文章并提取内容
    
    Args:
        url: 文章链接
        output_file: 输出文件路径（可选）
        save_to_feishu: 是否保存到飞书（默认False）
    """
    print(f"🌐 正在抓取: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        try:
            # 访问页面
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 等待内容加载
            await asyncio.sleep(2)
            
            # 获取页面内容
            html_content = await page.content()
            
            # 提取内容
            title, author, content = extract_content_by_rules(html_content, url)
            
            if not content:
                print("❌ 未能提取到正文内容")
                await browser.close()
                return None
            
            # 清理内容
            content = clean_content(content)
            
            # 生成 Markdown
            markdown = generate_markdown(title, author, url, content)
            
            print(f"✅ 提取成功！")
            print(f"   标题: {title[:50]}...")
            print(f"   作者: {author or '未知'}")
            print(f"   字数: {len(content)}")
            
            # 保存到文件
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown)
                print(f"✅ 已保存到: {output_file}")
            
            # 保存到飞书
            if save_to_feishu:
                print("📤 正在保存到飞书...")
                import tempfile
                import subprocess
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                    f.write(markdown)
                    temp_path = f.name
                
                try:
                    result = subprocess.run(
                        ['python3', 'save_to_feishu.py', temp_path, title],
                        capture_output=True,
                        text=True,
                        cwd='/workspace/projects/workspace/skills/content-processor/scripts'
                    )
                    if result.returncode == 0:
                        print("✅ 已保存到飞书")
                    else:
                        print(f"❌ 飞书保存失败: {result.stderr}")
                finally:
                    import os
                    os.unlink(temp_path)
            
            await browser.close()
            return markdown
            
        except Exception as e:
            print(f"❌ 抓取失败: {str(e)}")
            await browser.close()
            return None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='文章链接抓取工具')
    parser.add_argument('url', help='文章链接')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-f', '--feishu', action='store_true', help='保存到飞书')
    
    args = parser.parse_args()
    
    # 如果没有指定输出文件，使用标题生成文件名
    if not args.output:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f"/tmp/article_{timestamp}.md"
    
    # 运行抓取
    result = asyncio.run(extract_article(args.url, args.output, args.feishu))
    
    if result:
        print(f"\n📄 内容预览（前500字符）:\n{'='*50}")
        print(result[:500] + "..." if len(result) > 500 else result)


if __name__ == '__main__':
    main()
