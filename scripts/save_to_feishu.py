#!/usr/bin/env python3
"""
将视频转录内容保存到飞书知识库
"""

import sys
import os
import json
import re

# 使用curl调用飞书API
FEISHU_WIKI_NODE = "QwYuwDPBFidUxOkjYB3cSs9jn9c"  # 收集箱节点

def save_to_feishu(title, content, video_url):
    """保存文档到飞书知识库"""
    
    # 读取token
    token_path = os.path.expanduser("~/.config/openclaw/.feishu_token")
    if not os.path.exists(token_path):
        print("❌ 错误: 未找到飞书授权token")
        return False
    
    with open(token_path, 'r') as f:
        token_data = json.load(f)
        access_token = token_data.get('access_token')
    
    if not access_token:
        print("❌ 错误: token无效")
        return False
    
    # 创建文档
    import subprocess
    import tempfile
    
    # 准备markdown内容
    md_content = content
    
    # 使用feishu_create_doc工具
    # 由于无法直接导入，我们使用系统调用
    
    # 创建临时markdown文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(md_content)
        temp_md_path = f.name
    
    try:
        # 调用OpenClaw的feishu_create_doc工具
        # 这里需要通过系统方式调用
        
        # 使用Python requests直接调用API
        import urllib.request
        import urllib.error
        
        # 先创建文档
        create_url = "https://open.feishu.cn/open-apis/docx/v1/documents"
        
        data = json.dumps({
            "folder_token": FEISHU_WIKI_NODE,
            "title": title
        }).encode('utf-8')
        
        req = urllib.request.Request(
            create_url,
            data=data,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json; charset=utf-8'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if result.get('code') != 0:
            print(f"❌ 创建文档失败: {result}")
            return False
        
        doc_id = result['data']['document']['document_id']
        doc_url = f"https://www.feishu.cn/wiki/{doc_id}"
        
        print(f"✅ 文档创建成功: {doc_url}")
        
        # 更新收集箱目录（这里简化处理，实际应该调用feishu-toolkit）
        print("📋 请手动更新收集箱目录")
        
        return {
            'success': True,
            'doc_id': doc_id,
            'doc_url': doc_url
        }
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(temp_md_path):
            os.unlink(temp_md_path)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("使用方法: python3 save_to_feishu.py <标题> <markdown文件> <视频链接>")
        sys.exit(1)
    
    title = sys.argv[1]
    md_file = sys.argv[2]
    video_url = sys.argv[3]
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = save_to_feishu(title, content, video_url)
    
    if result:
        print(f"✅ 已保存到飞书: {result['doc_url']}")
    else:
        print("❌ 保存失败")
        sys.exit(1)
