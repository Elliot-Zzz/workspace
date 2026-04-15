---
name: send-dingtalk-file
description: 通过钉钉单聊（DM）发送文件给用户。使用此 skill 当用户要求发送文件、发送附件、发送 PDF、发送文档时调用。发送后用户会在钉钉单聊对话框中收到文件，而不是工作通知。
---

# 钉钉文件发送 Skill

## 核心方法

**必须使用 `scripts/send_dingtalk_file.py` 脚本，通过钉钉单聊（DM）渠道发送文件。**

此脚本支持为不同 agent 传入不同的钉钉账号凭证，实现精准的单聊发送。

## 凭证说明

每个 agent 有独立的钉钉机器人账号，发送文件时必须使用**自己的账号凭证**，否则会发送失败或发错账号。

| Agent | clientId | clientSecret | robotCode |
|-------|-----------|--------------|-----------|
| main (Elaine) | `dingvb3ebag9oqezqkni` | `9mMDZrn1yukxJwK5ZESHtZFr5wAra6SYyf7wwFDliwITxMnra2MbrJEy2FeQC6_w` | `dingvb3ebag9oqezqkni` |
| sheldon | `dingwlge731wb9fia7tv` | `_AG-FsJ7ZZ0ZDbqYGCcwpl1mDn-dH53q8W1EJvTkHeiuZru9dNYoyy6FoLLqIZYI` | `dingwlge731wb9fia7tv` |
| leonard | `dingimxik5mrakg2ky0g` | `znj6QP_v8c_s0NTWqGEjuutIlzGoXugxTqAW3Z_tsig5eAqEyhXGwtvQMwO7y3vH` | `dingimxik5mrakg2ky0g` |
| raj | `dingq6cbhz7pm5umdoh6` | `7fr0w6A5r9O2Hl-w_oj-CICTPoMkLw_kgyuJAxNrVWLPSil6we2GqTTkp0M_IC7o` | `dingq6cbhz7pm5umdoh6` |
| howard | `dingsvt5ca8yixmnmlkq` | `UEbIZ4OAluEXrDdreGNjzjujJE1F1F1jSBVEdcgRCdebEvO2s2hYVM9FZ9Pad940` | `dingsvt5ca8yixmnmlkq` |

**目标用户 ID（张煜）：** `1104083318783932`

## 使用方法

### 方式一：通过 exec 调用脚本（推荐）

```bash
python3 /home/elliot/.openclaw/workspace/scripts/send_dingtalk_file.py <file_path> <client_id> <client_secret> <robot_code> <user_id>
```

**示例（main 账号发送文件）：**
```bash
python3 /home/elliot/.openclaw/workspace/scripts/send_dingtalk_file.py /tmp/report.pdf dingvb3ebag9oqezqkni 9mMDZrn1yukxJwK5ZESHtZFr5wAra6SYyf7wwFDliwITxMnra2MbrJEy2FeQC6_w dingvb3ebag9oqezqkni 1104083318783932
```

### 方式二：通过脚本内默认凭证（仅 Raj 账号可直接调用）

Raj 账号的默认凭证已写在脚本里，可直接：
```bash
python3 /home/elliot/.openclaw/workspace/scripts/send_dingtalk_file.py <file_path>
```

**注意：** 其他 agent 必须显式传入凭证参数。

## 常见错误

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `HTTP Error 400: Bad Request` | 凭证错误或 robotCode 不匹配 | 确认使用自己账号的凭证 |
| `invalidParameter.openConversationId.invalid` | 未使用单聊接口 | 使用 `send_dingtalk_file.py` 的 DM 模式发送 |
| 文件进了工作通知栏 | 使用了旧版 API（如 topapi） | 必须用 `batchSend` + `x-acs-dingtalk-access-token` 方式 |

## 禁止事项

- **禁止**使用旧版 `oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2` 接口发送文件（会导致文件进入工作通知栏）
- **禁止**将文件 base64 编码后当文本发送（文件过大会导致正文超限）

## 脚本位置

```
/home/elliot/.openclaw/workspace/scripts/send_dingtalk_file.py
```

脚本已存在于主 workspace，所有 agent 均可通过绝对路径调用。
