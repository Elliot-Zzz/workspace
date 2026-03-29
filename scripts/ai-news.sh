#!/bin/bash
# AI 大模型资讯 Cron 脚本
# 监控: OpenClaw, MiniMax, Kimi, Claude, OpenAI, GLM 等官方动态

MESSAGE="📢 **AI 大模型最新动态** ($(date '+%Y-%m-%d %H:%M'))\n\n"

# 尝试获取各平台最新消息 (使用 web_fetch 抓取博客/公告页)

# OpenClaw
fetch_openclaw() {
    content=$(curl -sS --max-time 10 "https://github.com/openclaw/openclaw/releases" 2>/dev/null | grep -oP 'Release [0-9.]+' | head -1)
    if [ -n "$content" ]; then
        echo "🦞 **OpenClaw**: $content"
    fi
}

# OpenAI
fetch_openai() {
    content=$(curl -sS --max-time 10 "https://openai.com/blog" 2>/dev/null | grep -oP '<h1[^>]*>[^<]+</h1>' | head -1 | sed 's/<[^>]*>//g')
    if [ -n "$content" ]; then
        echo "🤖 **OpenAI**: $content"
    fi
}

# Anthropic (Claude)
fetch_claude() {
    content=$(curl -sS --max-time 10 "https://www.anthropic.com/blog" 2>/dev/null | grep -oP '<h2[^>]*>[^<]+</h2>' | head -1 | sed 's/<[^>]*>//g')
    if [ -n "$content" ]; then
        echo "🧠 **Claude**: $content"
    fi
}

# Kimi (月之暗面)
fetch_kimi() {
    content=$(curl -sS --max-time 10 "https://kimi.moonshot.cn" 2>/dev/null | grep -oP '最新动态[^<]+' | head -1)
    if [ -n "$content" ]; then
        echo "🌙 **Kimi**: $content"
    fi
}

# MiniMax
fetch_minimax() {
    content=$(curl -sS --max-time 10 "https://platform.minimaxi.me" 2>/dev/null | grep -oP '<title>[^<]+</title>' | head -1 | sed 's/<title>//g;s/<\/title>//g')
    if [ -n "$content" ]; then
        echo "⚡ **MiniMax**: $content"
    fi
}

# GLM (智谱)
fetch_glm() {
    content=$(curl -sS --max-time 10 "https://www.zhipuai.cn" 2>/dev/null | grep -oP '<title>[^<]+</title>' | head -1 | sed 's/<title>//g;s/<\/title>//g')
    if [ -n "$content" ]; then
        echo "📊 **GLM**: $content"
    fi
}

# 收集资讯
INFO=$(fetch_openclaw)
[ -n "$INFO" ] && MESSAGE="$MESSAGE$INFO\n"

INFO=$(fetch_openai)
[ -n "$INFO" ] && MESSAGE="$MESSAGE$INFO\n"

INFO=$(fetch_claude)
[ -n "$INFO" ] && MESSAGE="$MESSAGE$INFO\n"

INFO=$(fetch_kimi)
[ -n "$INFO" ] && MESSAGE="$MESSAGE$INFO\n"

INFO=$(fetch_minimax)
[ -n "$INFO" ] && MESSAGE="$MESSAGE$INFO\n"

INFO=$(fetch_glm)
[ -n "$INFO" ] && MESSAGE="$MESSAGE$INFO\n"

# 如果没有获取到任何内容
if [ "$MESSAGE" = "📢 **AI 大模型最新动态** ($(date '+%Y-%m-%d %H:%M'))\n\n" ]; then
    MESSAGE="$MESSAGE暂无最新动态 📭"
fi

# 通过 OpenClaw 发送消息到用户 (DingTalk)
echo "$MESSAGE"
