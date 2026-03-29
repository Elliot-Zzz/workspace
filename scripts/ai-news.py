#!/usr/bin/env python3
"""
AI 大模型资讯 Cron 脚本
使用 Tavily API 搜索 Twitter/X.com 上的 AI 最新动态
"""

import subprocess
import json
import re
import sys
from datetime import datetime

# 读取 Tavily API Key
def get_tavily_key():
    import os
    # 优先从环境变量
    key = os.environ.get('TAVILY_API_KEY', '')
    if key:
        return key
    # 从 openclaw.json 读取
    try:
        with open('/home/elliot/.openclaw/openclaw.json') as f:
            d = json.load(f)
            for k in ['TAVILY_API_KEY', 'tavily.apiKey', 'tavily']:
                if isinstance(d.get(k), str):
                    return d[k]
                if isinstance(d.get(k), dict):
                    return d[k].get('apiKey', '')
    except:
        pass
    return None

# 调用 Tavily Search API
def search_tavily(query, count=8):
    import urllib.request
    import urllib.parse
    
    api_key = get_tavily_key()
    if not api_key:
        return None, "Tavily API Key 未配置"
    
    url = 'https://api.tavily.com/search'
    data = json.dumps({
        'api_key': api_key,
        'query': query,
        'search_depth': 'basic',
        'count': count,
        'include_answer': False,
        'include_raw_content': False,
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result, None
    except Exception as e:
        return None, str(e)

# 格式化日期
now = datetime.now().strftime('%Y-%m-%d %H:%M')
message = f"📢 **AI 大模型最新动态** ({now})\n\n"

# 搜索 queries
queries = [
    ('OpenAI', 'site:x.com OpenAI official 2026 latest'),
    ('Anthropic Claude', 'site:x.com Anthropic Claude AI 2026'),
    ('DeepSeek', 'site:x.com DeepSeek AI 2026 latest'),
    ('MiniMax', 'site:x.com MiniMax AI 2026'),
    ('Google Gemini', 'site:x.com Google Gemini AI 2026'),
    ('Meta AI', 'site:x.com Meta AI Llama 2026'),
]

all_results = []
for name, query in queries:
    result, err = search_tavily(query, count=3)
    if err:
        continue
    if result and 'results' in result:
        for r in result['results']:
            all_results.append((name, r.get('title', ''), r.get('url', ''), r.get('snippet', '')))

# 去重（按 title）
seen = set()
unique_results = []
for item in all_results:
    title = item[1]
    if title and title not in seen:
        seen.add(title)
        unique_results.append(item)

if unique_results:
    for i, (name, title, url, snippet) in enumerate(unique_results[:6], 1):
        # 清理 HTML 标签
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        snippet_clean = re.sub(r'<[^>]+>', '', snippet).strip()
        if snippet_clean:
            message += f"**{name}**：{snippet_clean[:100]}\n"
        else:
            message += f"**{name}**：{title_clean[:80]}\n"
        message += f"🔗 {url}\n\n"
else:
    message += "暂无最新动态 📭\n\n"

print(message)
