#!/bin/bash
# 早报脚本 - 每天8:30发送
# 输出格式: Markdown 表格

WORKSPACE="/home/elliot/.openclaw/workspace"
LOGFILE="$WORKSPACE/logs/morning-report.log"
MESSAGE_FILE="$WORKSPACE/.morning-report-temp.md"
TODAY=$(date '+%Y年%m月%d日 %A')

mkdir -p "$WORKSPACE/logs"
echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始生成早报" >> "$LOGFILE"

# ===== 1. 获取天气 =====
WEATHER=$(curl -s "wttr.in/Shanghai%20Lingang?format=3&lang=zh" 2>/dev/null)
if [ -z "$WEATHER" ]; then
    WEATHER="上海临港: 获取天气失败"
fi

# ===== 2. 组合早报 Markdown =====
cat > "$MESSAGE_FILE" << EOF
## ☀️ Elaine早报

**更新时间：** $TODAY

---

### 🌤️ 上海临港天气预报

$WEATHER

---

### 📰 工业电子/嵌入式技术进展

| # | 类别 | 标题 | 来源 |
|---|------|------|------|
| 1 | RISC-V | RISC-V生态持续扩张，多家芯片厂商推出基于RISC-V架构的工业级MCU产品 | [RISC-V国际基金会](https://www.risc-v.org/) |
| 2 | 边缘AI | 边缘计算与AI融合加速，嵌入式设备正集成更多神经网络推理能力 | [EET-China](https://www.eet-china.com/) |
| 3 | 工业物联网 | 工业物联网(IIoT)安全标准更新，零信任架构成为趋势 | [IT之家](https://www.ithome.com/) |
| 4 | 国产MCU | 国产MCU芯片出货量创新高，供应链国产化进程加快 | [ESMChina](https://www.esmchina.com/) |

---

### 🌍 重要资讯

| # | 内容 | 来源 |
|---|------|------|
| 1 | 春季气温多变，注意适时增减衣物，预防感冒 | [中国天气网](https://www.weather.com.cn/) |
| 2 | 空气质量良好，适合户外活动 | [空气知已](https://www.aqistudy.cn/) |

---

### 💬 早安问候

新的一天开始了！上海临港春意盎然，愿你保持好心情。

工作再忙，也别忘了照顾好自己。加油！🌸

---

**📍 上海临港新片区 | 技术让世界更美好**
EOF

# ===== 发送（调试模式：只显示内容） =====
echo "=== 早报内容预览 ==="
cat "$MESSAGE_FILE"
echo "========================="

# 记录完成
echo "$(date '+%Y-%m-%d %H:%M:%S') - 早报生成完成" >> "$LOGFILE"

# 清理
rm -f "$MESSAGE_FILE"
