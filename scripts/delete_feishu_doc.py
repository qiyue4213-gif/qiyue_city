#!/usr/bin/env python3
"""
删除飞书文档/Wiki节点
"""

import sys
import os
import json
import urllib.request
import urllib.error

# 获取存储的token
def get_token():
    """从加密存储中读取token"""
    import subprocess
    
    # 使用OpenClaw内部命令获取token
    # 由于token是加密的，我们通过环境变量或调用内部API来获取
    
    # 暂时使用硬编码方式（实际使用时需要替换）
    # 更好的方式是通过OpenClaw的context获取
    
    # 读取加密的token文件
    token_dir = os.path.expanduser("~/.local/share/openclaw-feishu-uat/")
    
    # 找到当前用户的token文件
    enc_files = [f for f in os.listdir(token_dir) if f.endswith('.enc') and 'ou_c9f858c38d7ae8a5b5f4a8b786a040de' in f]
    
    if not enc_files:
        print("❌ 未找到token文件")
        return None
    
    # 读取master key
    with open(os.path.join(token_dir, 'master.key'), 'rb') as f:
        master_key = f.read()
    
    # 读取加密的token
    with open(os.path.join(token_dir, enc_files[0]), 'rb') as f:
        encrypted_data = f.read()
    
    # 解密
    from Crypto.Cipher import AES
    
    IV_BYTES = 12
    TAG_BYTES = 16
    
    iv = encrypted_data[:IV_BYTES]
    tag = encrypted_data[IV_BYTES:IV_BYTES + TAG_BYTES]
    enc = encrypted_data[IV_BYTES + TAG_BYTES:]
    
    cipher = AES.new(master_key, AES.MODE_GCM, nonce=iv)
    cipher.update(b"")
    try:
        decrypted = cipher.decrypt_and_verify(enc, tag)
        token_data = json.loads(decrypted.decode('utf-8'))
        return token_data.get('accessToken')
    except Exception as e:
        print(f"❌ 解密失败: {e}")
        return None

def delete_doc(doc_id):
    """删除云文档"""
    access_token = get_token()
    
    if not access_token:
        print("❌ 无法获取access token")
        return False
    
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}"
    
    req = urllib.request.Request(
        url,
        headers={'Authorization': f'Bearer {access_token}'},
        method='DELETE'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                print(f"✅ 文档删除成功: {doc_id}")
                return True
            else:
                print(f"❌ 删除失败: {result}")
                return False
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP错误: {e.code}")
        print(e.read().decode('utf-8'))
        return False

def delete_wiki_node(space_id, node_token):
    """删除Wiki节点"""
    access_token = get_token()
    
    if not access_token:
        print("❌ 无法获取access token")
        return False
    
    url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes/{node_token}"
    
    req = urllib.request.Request(
        url,
        headers={'Authorization': f'Bearer {access_token}'},
        method='DELETE'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                print(f"✅ Wiki节点删除成功: {node_token}")
                return True
            else:
                print(f"❌ 删除失败: {result}")
                return False
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP错误: {e.code}")
        print(e.read().decode('utf-8'))
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  删除云文档: python3 delete_feishu_doc.py doc <document_id>")
        print("  删除Wiki节点: python3 delete_feishu_doc.py wiki <space_id> <node_token>")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "doc" and len(sys.argv) >= 3:
        doc_id = sys.argv[2]
        delete_doc(doc_id)
    elif action == "wiki" and len(sys.argv) >= 4:
        space_id = sys.argv[2]
        node_token = sys.argv[3]
        delete_wiki_node(space_id, node_token)
    else:
        print("❌ 参数错误")
        print("使用方法:")
        print("  删除云文档: python3 delete_feishu_doc.py doc <document_id>")
        print("  删除Wiki节点: python3 delete_feishu_doc.py wiki <space_id> <node_token>")
        sys.exit(1)
