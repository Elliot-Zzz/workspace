#!/usr/bin/env python3
"""
NBA战报 Cron 脚本（含季后赛局势分析）
数据源: 腾讯体育 sports.qq.com
输出格式: Markdown 表格 + 季后赛分析
"""

import subprocess
import re
import json
import sys
from datetime import datetime

# ============================================================
# 2025-26 NBA 季后赛排名数据（截至4月24日）
# ============================================================
WEST_STANDINGS = [
    ("雷霆", "OKC", 64, 18, "#1"),
    ("马刺", "SAS", 62, 20, "#2"),
    ("掘金", "DEN", 54, 28, "#3"),
    ("湖人", "LAL", 53, 29, "#4"),
    ("火箭", "HOU", 52, 30, "#5"),
    ("森林狼", "MIN", 49, 33, "#6"),
    ("开拓者", "POR", 42, 40, "#7*"),
    ("太阳", "PHX", 45, 37, "#8*"),
]

EAST_STANDINGS = [
    ("活塞", "DET", 60, 22, "#1"),
    ("凯尔特人", "BOS", 56, 26, "#2"),
    ("尼克斯", "NYK", 53, 29, "#3"),
    ("骑士", "CLE", 52, 30, "#4"),
    ("猛龙", "TOR", 46, 36, "#5"),
    ("老鹰", "ATL", 46, 36, "#6"),
    ("76人", "PHI", 45, 37, "#7*"),
    ("魔术", "ORL", 45, 37, "#8*"),
]

# 首轮对阵形势（截至4月24日G3前）
# 格式：(t1_name, t1_abbr, t1_wins, t2_name, t2_abbr, t2_wins)
WEST_SERIES = [
    ("雷霆", "OKC", 2, "太阳", "PHX", 0),
    ("马刺", "SAS", 1, "开拓者", "POR", 1),
    ("掘金", "DEN", 1, "森林狼", "MIN", 2),
    ("湖人", "LAL", 2, "火箭", "HOU", 0),
]

EAST_SERIES = [
    ("活塞", "DET", 1, "魔术", "ORL", 1),
    ("凯尔特人", "BOS", 1, "76人", "PHI", 1),
    ("尼克斯", "NYK", 2, "老鹰", "ATL", 1),
    ("骑士", "CLE", 2, "猛龙", "TOR", 1),
]


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


# NBA 球队白名单（30支）
NBA_TEAMS = {
    '亚特兰大老鹰', '波士顿凯尔特人', '布鲁克林篮网', '夏洛特黄蜂', '芝加哥公牛',
    '克利夫兰骑士', '达拉斯独行侠', '丹佛掘金', '底特律活塞', '金州勇士',
    '休斯顿火箭', '印第安纳步行者', '洛杉矶快船', '洛杉矶湖人', '孟菲斯灰熊',
    '迈阿密热火', '密尔沃基雄鹿', '明尼苏达森林狼', '新奥尔良鹈鹕', '纽约尼克斯',
    '俄克拉荷马雷霆', '奥兰多魔术', '费城76人', '菲尼克斯太阳', '波特兰开拓者',
    '萨克拉门托国王', '圣安东尼奥马刺', '多伦多猛龙', '犹他爵士', '华盛顿奇才',
    'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 'Chicago Bulls',
    'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons', 'Golden State Warriors',
    'Houston Rockets', 'Indiana Pacers', 'LA Clippers', 'Los Angeles Clippers', 'Los Angeles Lakers', 'Los Angeles Lakers',
    'Memphis Grizzlies', 'Miami Heat', 'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans',
    'New York Knicks', 'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
    'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors', 'Utah Jazz', 'Washington Wizards',
    '老鹰', '凯尔特人', '篮网', '黄蜂', '公牛', '骑士', '独行侠', '掘金', '活塞', '勇士',
    '火箭', '步行者', '快船', '湖人', '灰熊', '热火', '雄鹿', '森林狼', '鹈鹕', '尼克斯',
    '雷霆', '魔术', '76人', '太阳', '开拓者', '国王', '马刺', '猛龙', '爵士', '奇才',
    ' Hawks', 'Celtics', 'Nets', 'Hornets', 'Bulls', 'Cavaliers', 'Mavericks', 'Nuggets', 'Pistons', 'Warriors',
    'Rockets', 'Pacers', 'Clippers', 'Lakers', 'Grizzlies', 'Heat', 'Bucks', 'Timberwolves', 'Pelicans',
    'Knicks', 'Thunder', 'Magic', '76ers', 'Suns', 'Trail Blazers', 'Kings', 'Spurs', 'Raptors', 'Jazz', 'Wizards',
}


def is_nba_team(name):
    """检查是否是NBA球队"""
    if not name:
        return False
    for team in NBA_TEAMS:
        if team in name:
            return True
    return False


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
                left_name = match_info.get('leftName', '')
                right_name = match_info.get('rightName', '')
                # 双重过滤：必须是NBA球队
                if not is_nba_team(left_name) or not is_nba_team(right_name):
                    continue
                left_goal = match_info.get('leftGoal', '0')
                right_goal = match_info.get('rightGoal', '0')
                matches.append({
                    'left': left_name,
                    'right': right_name,
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


def generate_standings_table():
    """生成常规赛排名表格"""
    lines = []
    lines.append("### 🏆 西部排名（2025-26赛季）")
    lines.append("")
    lines.append("| # | 球队 | 胜 | 负 | 胜率 | 战绩 | 备注 |")
    lines.append("|---|------|---|---|------|-----|------|")
    for team, abbr, wins, losses, note in WEST_STANDINGS:
        win_rate = wins / (wins + losses)
        lines.append(
            f"| {note} | **{team}** | {wins} | {losses} | {win_rate:.1%} | {wins}-{losses} | "
            f"{'附加赛晋级' if '*' in note else ''} |"
        )
    lines.append("")
    lines.append("### 🏆 东部排名（2025-26赛季）")
    lines.append("")
    lines.append("| # | 球队 | 胜 | 负 | 胜率 | 战绩 | 备注 |")
    lines.append("|---|------|---|---|------|-----|------|")
    for team, abbr, wins, losses, note in EAST_STANDINGS:
        win_rate = wins / (wins + losses)
        lines.append(
            f"| {note} | **{team}** | {wins} | {losses} | {win_rate:.1%} | {wins}-{losses} | "
            f"{'附加赛晋级' if '*' in note else ''} |"
        )
    lines.append("")
    return "\n".join(lines)


def generate_series_status():
    """生成季后赛首轮对阵形势"""
    lines = []
    lines.append("### 🔥 西部首轮对阵形势")
    lines.append("")
    lines.append("| 对阵 | 比分 | 局势分析 |")
    lines.append("|------|------|----------|")

    west_analyses = [
        ("雷霆 — 太阳", "2-0", "🔥 雷霆全面压制！SGA场均30+，场均净胜29分，目标横扫晋级"),
        ("马刺 — 开拓者", "1-1", "⚖️ 势均力敌！Wembanyama脑震荡伤退成X因素，G3关键战"),
        ("掘金 — 森林狼", "1-2", "⚠️ 森林狼反超！约基奇近两场效率骤降，卫冕冠军陷入被动"),
        ("湖人 — 火箭", "2-0", "🔥 詹姆斯+东契奇双核驱动，KD复出仍输球，火箭危在旦夕"),
    ]
    for (matchup, score, analysis), (t1, a1, s1, t2, a2, s2) in zip(west_analyses, WEST_SERIES):
        lines.append(f"| {matchup} | **{s1}-{s2}** | {analysis} |")

    lines.append("")
    lines.append("### 🔥 东部首轮对阵形势")
    lines.append("")
    lines.append("| 对阵 | 比分 | 局势分析 |")
    lines.append("|------|------|----------|")

    east_analyses = [
        ("活塞 — 魔术", "1-1", "⚖️ 活塞强势扳回一城！但进攻稳定性存隐患，G3将见真章"),
        ("凯尔特人 — 76人", "1-1", "⚖️ 76人客场爆冷掀翻绿军！大帝恩比德内线发威，逼平波士顿"),
        ("尼克斯 — 老鹰", "2-1", "⚠️ 老鹰绝杀逆袭！特雷·杨轰下关键分，系列赛悬念迭起"),
        ("骑士 — 猛龙", "2-1", "⚠️ 猛龙大胜骑士止血！系列赛仍有悬念，米切尔需挺身而出"),
    ]
    for (matchup, score, analysis), (t1, a1, s1, t2, a2, s2) in zip(east_analyses, EAST_SERIES):
        lines.append(f"| {matchup} | **{s1}-{s2}** | {analysis} |")

    lines.append("")
    return "\n".join(lines)


def generate_playoff_outlook():
    """生成季后赛形势总分析"""
    lines = []
    lines.append("### 📋 季后赛形势总览")
    lines.append("")
    lines.append("**🏆 夺冠热门：**")
    lines.append("- **雷霆（OKC）**：常规赛64胜18负，联盟第一，SGA领衔攻防一体，目标直通总决赛")
    lines.append("- **马刺（SAS）**：62胜，文班亚玛+MOP组合，西部第二但饱受伤病困扰")
    lines.append("- **活塞（DET）**：60胜，东部第一，本赛季最大黑马，青年军渴望走远")
    lines.append("")
    lines.append("**⚠️ 需关注的X因素：**")
    lines.append("- **文班亚玛伤情**：G2撞到头部引发脑震荡，缺阵G3，马刺前景蒙阴影")
    lines.append("- **约基奇状态**：卫冕FMVP近两场26中7，效率骤降，掘金危机显现")
    lines.append("- **雷霆伤情**：Jalen Williams腿筋受伤退场，可能影响次轮战力")
    lines.append("- **KD康复**：杜兰特伤愈复出表现一般，火箭0-2落后形势危急")
    lines.append("")
    lines.append("**📅 今日重点场次（4月24日）：**")
    lines.append("- 🟢 **76人 vs 凯尔特人（G3）** 07:00：76人能否在波士顿偷得客场第二胜？")
    lines.append("- 🟢 **火箭 vs 湖人（G3）** 08:00：KD主场救赎 or 詹姆斯冲击赛点？")
    lines.append("- 🟢 **开拓者 vs 马刺（G3）** 10:30：无Wembanyama，马刺青年军临危受命")
    lines.append("")
    return "\n".join(lines)


def generate_report(matches, date_str):
    """生成NBA战报（Markdown 表格格式 + 季后赛分析）"""
    today_cn = datetime.now().strftime('%m月%d日')
    now_str = datetime.now().strftime('%H:%M')

    lines = []
    lines.append(f"## 🏀 NBA战报 & 季后赛分析（{today_cn}）")
    lines.append("")
    lines.append(f"**更新时间：** {now_str}")
    lines.append("")

    if not matches:
        lines.append("今日暂无NBA比赛数据 📭")
        lines.append("")
    else:
        # 按状态排序：已结束的在前
        matches.sort(key=lambda x: 0 if '结束' in x['status'] else 1)

        # ===== 今日完整赛果 =====
        lines.append("### 📊 今日赛果")
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

    # ===== 季后赛排名 =====
    lines.append(generate_standings_table())

    # ===== 首轮对阵形势 =====
    lines.append(generate_series_status())

    # ===== 季后赛形势总览 =====
    lines.append(generate_playoff_outlook())

    # ===== 底部来源 =====
    lines.append("---")
    lines.append(f"**数据来源：** [腾讯体育](https://sports.qq.com/nba/) | [CBS Sports](https://www.cbssports.com/nba/)")
    lines.append(f"**生成时间：** {now_str}")
    print("\n".join(lines))


def main():
    today = datetime.now().strftime('%Y-%m-%d')
    data = fetch_nba_data(today)
    matches = extract_nba_matches(data)
    generate_report(matches, today)


if __name__ == '__main__':
    main()
