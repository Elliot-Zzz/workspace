#!/usr/bin/env python3
"""
AI 大模型资讯 Cron 脚本
使用 Tavily API 搜索 Twitter/X.com 上的 AI 最新动态
输出格式：详细摘要 + 可点击超链接（钉钉 Markdown 格式）
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
def search_tavily(query, count=5):
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

# 清理 HTML 标签
def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text).strip()
    return text

# 格式化日期
now = datetime.now().strftime('%Y-%m-%d %H:%M')

# 搜索 queries
queries = [
    ('OpenAI', 'site:x.com OR site:twitter.com OpenAI official 2026 latest announcement'),
    ('Anthropic Claude', 'site:x.com OR site:twitter.com Anthropic Claude AI 2026 latest'),
    ('DeepSeek', 'site:x.com OR site:twitter.com DeepSeek AI 2026 latest model'),
    ('MiniMax', 'site:x.com OR site:twitter.com MiniMax AI 2026 latest'),
    ('Google Gemini', 'site:x.com OR site:twitter.com Google Gemini AI 2026 latest'),
    ('Meta AI', 'site:x.com OR site:twitter.com Meta AI Llama 2026 latest'),
]

all_results = []
for name, query in queries:
    result, err = search_tavily(query, count=4)
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

# 构建消息（钉钉 Markdown 格式）
lines = []
lines.append(f"## 🤖 AI 大模型最新动态")
lines.append(f"**更新时间：** {now}")
lines.append("")

if unique_results:
    for i, (name, title, url, snippet) in enumerate(unique_results[:6], 1):
        title_clean = clean_text(title)
        snippet_clean = clean_text(snippet)

        # 标题行：可点击超链接
        lines.append(f"**{i}. 【{name}】**")
        lines.append(f"[{title_clean[:80]}]({url})")

        # 摘要内容
        if snippet_clean:
            lines.append(f"📝 {snippet_clean[:200]}")
        lines.append("")
else:
    lines.append("暂无最新动态 📭")
    lines.append("")

# 底部超链接列表
lines.append("---")
lines.append("**来源：**")
for i, (name, title, url, snippet) in enumerate(unique_results[:6], 1):
    title_clean = clean_text(title)
    lines.append(f"{i}. [{title_clean[:50]}]({url})")

message = "\n".join(lines)
print(message)
