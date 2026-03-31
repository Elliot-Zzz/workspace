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

# 搜索 queries - 美国顶尖模型公司
us_queries = [
    ('OpenAI', 'OpenAI GPT-5 o3 model release 2026 latest news'),
    ('Anthropic', 'Anthropic Claude 4 2026 latest news model release'),
    ('Google DeepMind', 'Google DeepMind Gemini 2 2026 latest news'),
    ('Meta AI', 'Meta AI Llama 4 2026 latest model release'),
    ('Microsoft Copilot', 'Microsoft Copilot Azure AI 2026 latest news'),
    ('xAI', 'xAI Grok 3 model 2026 latest news'),
    ('Amazon AI', 'Amazon AWS AI Bedrock Nova 2026 latest'),
    ('Nvidia AI', 'Nvidia NeMo Megatron GPU AI 2026 latest'),
    ('Apple Intelligence', 'Apple Intelligence AI 2026 latest news'),
]

# 国内模型公司
cn_model_queries = [
    ('百度 ERNIE', '百度 文心一言 ERNIE 2026 最新消息'),
    ('阿里 Qwen', '阿里 通义千问 Qwen 2026 最新消息'),
    ('腾讯 Hunyuan', '腾讯 混元 Hunyuan 2026 最新消息'),
    ('字节 Doubao', '字节 云雀 Doubao 2026 最新消息'),
    ('华为 Pangu', '华为 盘古 Pangu 2026 最新消息'),
    ('智谱 GLM', '智谱 ChatGLM GLM-5 2026 最新消息'),
    ('讯飞 Spark', '讯飞 星火 Spark 2026 最新消息'),
    ('商汤 SenseNova', '商汤 日日新 SenseNova 2026 最新消息'),
    ('月之暗面 Kimi', '月之暗面 Kimi Moonshot 2026 最新消息'),
    ('百川智能', '百川智能 Baichuan 2026 最新消息'),
    ('MiniMax', 'MiniMax 海螺 AI 2026 最新消息'),
    ('DeepSeek', 'DeepSeek 2026 最新消息 模型发布'),
]

# AI 应用公司
ai_app_queries = [
    ('AI 搜索/助手', 'Perplexity AI Cursor AI assistant 2026 latest news'),
    ('AI 图像', 'Midjourney DALL-E Stable Diffusion 2026 latest news'),
    ('AI 视频', 'Sora Runway Pika video AI 2026 latest news'),
    ('AI 编程', 'GitHub Copilot Codeium AI coding 2026 latest'),
    ('AI 办公', 'Notion AI Gamma Tome Copilot 2026 latest'),
    ('AI 教育', 'Khan Academy Duolingo AI education 2026 latest'),
    ('AI 医疗', 'Google Health IBM Watson AI healthcare 2026 latest'),
    ('AI 汽车', 'Tesla Autopilot Wayve AI driving 2026 latest news'),
]

queries = us_queries + cn_model_queries + ai_app_queries

all_results = []
for name, query in queries:
    result, err = search_tavily(query, count=6)
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

# 按公司类型分组
us_results = [(n, t, u, s) for n, t, u, s in unique_results if any(x in n for x in ['OpenAI', 'Anthropic', 'Google', 'Meta', 'Microsoft', 'xAI', 'Amazon', 'Nvidia', 'Apple'])]
cn_results = [(n, t, u, s) for n, t, u, s in unique_results if any(x in n for x in ['百度', '阿里', '腾讯', '字节', '华为', '智谱', '讯飞', '商汤', '月之暗面', '百川', 'MiniMax', 'DeepSeek'])]
app_results = [(n, t, u, s) for n, t, u, s in unique_results if any(x in n for x in ['AI 搜索', 'AI 图像', 'AI 视频', 'AI 编程', 'AI 办公', 'AI 教育', 'AI 医疗', 'AI 汽车'])]

# 构建消息（钉钉 Markdown 格式）
lines = []
lines.append(f"## 🤖 AI 大模型 & 应用最新动态")
lines.append(f"**更新时间：** {now}")
lines.append("")

# 美国顶尖模型
if us_results:
    lines.append("### 🇺🇸 美国顶尖模型公司")
    lines.append("")
    for i, (name, title, url, snippet) in enumerate(us_results[:5], 1):
        title_clean = clean_text(title)
        snippet_clean = clean_text(snippet)
        lines.append(f"**{i}. 【{name}】**")
        lines.append(f"[{title_clean}]({url})")
        if snippet_clean:
            lines.append(f"📝 {snippet_clean}")
        lines.append("")

# 国内模型公司
if cn_results:
    lines.append("### 🇨🇳 国内模型公司")
    lines.append("")
    for i, (name, title, url, snippet) in enumerate(cn_results[:5], 1):
        title_clean = clean_text(title)
        snippet_clean = clean_text(snippet)
        lines.append(f"**{i}. 【{name}】**")
        lines.append(f"[{title_clean}]({url})")
        if snippet_clean:
            lines.append(f"📝 {snippet_clean}")
        lines.append("")

# AI 应用公司
if app_results:
    lines.append("### 🚀 AI 应用公司")
    lines.append("")
    for i, (name, title, url, snippet) in enumerate(app_results[:5], 1):
        title_clean = clean_text(title)
        snippet_clean = clean_text(snippet)
        lines.append(f"**{i}. 【{name}】**")
        lines.append(f"[{title_clean}]({url})")
        if snippet_clean:
            lines.append(f"📝 {snippet_clean}")
        lines.append("")

if not unique_results:
    lines.append("暂无最新动态 📭")
    lines.append("")

# 底部超链接列表
lines.append("---")
lines.append("**📚 来源汇总：**")
for i, (name, title, url, snippet) in enumerate(unique_results[:12], 1):
    title_clean = clean_text(title)
    lines.append(f"{i}. [{title_clean[:60]}]({url}) - {name}")

message = "\n".join(lines)
print(message)
