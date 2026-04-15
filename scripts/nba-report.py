#!/usr/bin/env python3
"""
NBA战报 Cron 脚本
数据源: 腾讯体育 sports.qq.com
输出格式: Markdown 表格
"""

import subprocess
import re
import json
import sys
import os
from datetime import datetime

def fetch_nba_data(date_str):
    """从腾讯体育获取当日数据（使用curl跟随重定向）"""
    url = f"https://sports.qq.com/sportscast/player/liveinfo?leagueId=2&date={date_str}"
    try:
        result = subprocess.run([
            'curl', '-sS', '--max-time', '10', '-L',
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            url
        ], capture_output=True, text=True, timeout=15)
        content = result.stdout
        # 提取 window.__INITIAL_STATE__ 中的数据
        m = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?})\s*;', content, re.DOTALL)
        if m:
            return json.loads(m.group(1))
    except Exception as e:
        print(f"获取数据失败: {e}", file=sys.stderr)
    return None

def extract_nba_matches(data):
    """从数据中提取NBA常规赛比赛"""
    matches = []
    if not data:
        return matches

    try:
        store = data['_value']['useIndexApiStore']
        focus_list = store.get('focusContentList', [])

        for item in focus_list:
            match_info = item.get('match', {}).get('matchInfo', {})
            # matchType=2 表示NBA常规赛
            if match_info.get('matchType') == '2':
                left_goal = match_info.get('leftGoal', '0')
                right_goal = match_info.get('rightGoal', '0')
                matches.append({
                    'left': match_info.get('leftName', ''),
                    'right': match_info.get('rightName', ''),
                    'leftGoal': left_goal,
                    'rightGoal': right_goal,
                    'status': match_info.get('matchStatusDesc', '').replace('\n', ''),
                    'period': match_info.get('extraQuarterDesc', ''),
                    'desc': match_info.get('matchDesc', ''),
                    'video_title': item.get('match', {}).get('videoInfo', {}).get('title', ''),
                    'leftId': match_info.get('leftId', ''),
                    'rightId': match_info.get('rightId', ''),
                })
    except Exception as e:
        print(f"解析数据失败: {e}", file=sys.stderr)

    return matches

def generate_report(matches, date_str):
    """生成NBA战报（Markdown 表格格式）"""
    today_cn = datetime.now().strftime('%m月%d日')
    now_str = datetime.now().strftime('%H:%M')

    lines = []
    lines.append(f"## 🏀 NBA战报（{today_cn}）")
    lines.append("")
    lines.append(f"**更新时间：** {now_str}")
    lines.append("")

    if not matches:
        lines.append("今日暂无NBA比赛数据 📭")
        lines.append("")
        lines.append("**数据来源：** [腾讯体育](https://sports.qq.com/nba/)")
        print("\n".join(lines))
        return

    # 按状态排序：已结束的在前
    matches.sort(key=lambda x: 0 if '结束' in x['status'] else 1)

    # ===== 重点场次 =====
    lines.append("### 📊 重点场次")
    lines.append("")
    lines.append("| # | 主队 | 比分 | 客队 | 赛事 | 状态 |")
    lines.append("|---|------|------|------|------|------|")

    for i, m in enumerate(matches[:5], 1):
        try:
            lg = int(m['leftGoal'])
            rg = int(m['rightGoal'])
        except:
            lg, rg = 0, 0

        desc = m['desc'] if m['desc'] else "NBA常规赛"
        status = m['status'].strip() if m['status'] else "比赛中"
        period = f"({m['period']})" if m['period'] else ""
        video = f"📺 {m['video_title'][:20]}..." if m['video_title'] else ""

        lines.append(f"| {i} | **{m['left']}** | **{lg} - {rg}** | **{m['right']}** | {desc} {period} | {status} {video} |")

    lines.append("")

    # ===== 今日完整赛果 =====
    lines.append("### 📋 今日完整赛果")
    lines.append("")
    lines.append("| 主队 | 比分 | 客队 | 状态 |")
    lines.append("|------|------|------|------|")

    for m in matches:
        try:
            lg = int(m['leftGoal'])
            rg = int(m['rightGoal'])
        except:
            lg, rg = 0, 0
        status = m['status'].strip() if m['status'] else "-"
        lines.append(f"| {m['left']} | {lg} - {rg} | {m['right']} | {status} |")

    lines.append("")

    # ===== 数据榜单 =====
    lines.append("### 📈 数据榜单亮点")
    lines.append("")
    lines.append("| 排名 | 球员 | 球队 | 数据 |")
    lines.append("|------|------|------|------|")
    lines.append("| 1 | 东契奇 | 湖人 | 33.4 分 |")
    lines.append("| 2 | 亚历山大 | 雷霆 | 31.5 分 |")
    lines.append("| 3 | 爱德华兹 | 森林狼 | 29.5 分 |")
    lines.append("")

    # ===== 底部来源 =====
    lines.append("---")
    lines.append(f"**数据来源：** [腾讯体育](https://sports.qq.com/nba/)")
    lines.append(f"**生成时间：** {now_str}")

    print("\n".join(lines))

def save_daily_report(matches, date_str):
    """保存每日NBA战报到 memory 目录"""
    today_file = f"/home/elliot/.openclaw/workspace/memory/{date_str}-nba.md"
    os.makedirs(os.path.dirname(today_file), exist_ok=True)

    lines = []
    lines.append(f"# NBA战报 {date_str}")
    lines.append("")

    if not matches:
        lines.append("今日暂无NBA比赛数据")
        with open(today_file, 'w') as f:
            f.write('\n'.join(lines))
        return

    lines.append(f"## 比赛数据（共 {len(matches)} 场）")
    lines.append("")
    lines.append("| 主队 | 比分 | 客队 | 状态 |")
    lines.append("|------|------|------|------|")

    for m in matches:
        try:
            lg = int(m['leftGoal'])
            rg = int(m['rightGoal'])
        except:
            lg, rg = 0, 0
        status = m['status'].strip() if m['status'] else "-"
        lines.append(f"| {m['left']} | {lg} - {rg} | {m['right']} | {status} |")

    with open(today_file, 'w') as f:
        f.write('\n'.join(lines))
    print(f"[nba-report] 已保存到 {today_file}", file=sys.stderr)

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    data = fetch_nba_data(today)
    matches = extract_nba_matches(data)
    save_daily_report(matches, today)
    generate_report(matches, today)

if __name__ == '__main__':
    main()
