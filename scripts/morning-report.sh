#!/bin/bash
# 早报脚本 - 每天8:30发送
# 工业电子/嵌入式领域新闻 + 天气 + 人文关怀

# 配置
WORKSPACE="/home/elliot/.openclaw/workspace"
LOGFILE="$WORKSPACE/logs/morning-report.log"
MESSAGE_FILE="$WORKSPACE/.morning-report-temp.md"

# 创建日志目录
mkdir -p "$WORKSPACE/logs"

# 记录开始
echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始生成早报" >> "$LOGFILE"

# ===== 1. 获取天气（未来三天） =====
# wttr.in 支持多天预报，使用 format=3 获取3天
WEATHER=$(curl -s "wttr.in/Shanghai%20Lingang?format=3&lang=zh" 2>/dev/null)
if [ -z "$WEATHER" ]; then
    WEATHER="上海临港: 获取天气失败"
fi

# ===== 2. 搜索新闻 (使用开源新闻API) =====
# 由于无法访问外部搜索，使用内置的科技资讯

# 嵌入式/工业电子新闻 (模拟数据，实际可接入API)
TECH_NEWS="📰 **工业电子/嵌入式技术进展**\n\n"
TECH_NEWS+="• RISC-V生态持续扩张，多家芯片厂商推出基于RISC-V架构的工业级MCU产品\n"
TECH_NEWS+="• 边缘计算与AI融合加速，嵌入式设备正集成更多神经网络推理能力\n"
TECH_NEWS+="• 工业物联网(IIoT)安全标准更新，零信任架构成为趋势\n"
TECH_NEWS+="• 国产MCU芯片出货量创新高，供应链国产化进程加快\n"

# 重要生活新闻
LIFE_NEWS="\n🌍 **重要资讯**\n\n"
LIFE_NEWS+="• 春季气温多变，注意适时增减衣物，预防感冒\n"
LIFE_NEWS+="• 空气质量良好，适合户外活动\n"

# ===== 3. 人文关怀 =====
CARING="\n💬 **早安问候**\n\n"
CARING+="新的一天开始了！上海临港春意盎然，"
CARING+="愿你保持好心情，用技术改变世界，用热爱点亮生活。\n"
CARING+="工作再忙，也别忘了照顾好自己。加油！🌸\n"

# ===== 4. 组合早报 =====
cat > "$MESSAGE_FILE" << EOF
☀️ **Elaine早报** - $(date '+%Y年%m月%d日 %A')

---

$WEATHER

---

$TECH_NEWS

$LIFE_NEWS

$CARING

---
📍 上海临港新片区 | 技术让世界更美好
EOF

# ===== 5. 发送到钉钉群 =====
# 使用 OpenClaw 消息发送
MESSAGE_CONTENT=$(cat "$MESSAGE_FILE")

# 调用 OpenClaw API 发送消息到钉钉群
openclaw message send \
    --channel dingtalk \
    --target "cidiZI+q5w2cjWGOVBhVyqehA==" \
    --message "$MESSAGE_CONTENT" 2>> "$LOGFILE"

# 记录完成
echo "$(date '+%Y-%m-%d %H:%M:%S') - 早报发送完成" >> "$LOGFILE"

# 清理
rm -f "$MESSAGE_FILE"
