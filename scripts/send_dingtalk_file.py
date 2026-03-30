#!/usr/bin/env python3
"""
钉钉文件发送脚本
用法: python3 send_dingtalk_file.py <file_path> [client_id] [client_secret] [robot_code] [user_id]
"""
import sys, os, json, urllib.request

def send_file(client_id, client_secret, robot_code, user_id, file_path):
    """通过钉钉REST API发送文件"""
    
    # 1. 获取新API token (header认证方式)
    req = urllib.request.Request(
        "https://api.dingtalk.com/v1.0/oauth2/accessToken",
        data=json.dumps({"appKey": client_id, "appSecret": client_secret}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        token = json.loads(resp.read())["accessToken"]

    # 2. 上传文件获取 media_id
    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lstrip('.') or 'file'
    mime = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'zip': 'application/zip',
        'mp4': 'video/mp4',
    }.get(ext, 'application/octet-stream')

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"media\"; filename=\"{filename}\"\r\n"
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    upload_url = f"https://oapi.dingtalk.com/media/upload?access_token={token}&type=file"
    req2 = urllib.request.Request(upload_url, data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req2) as resp:
        up = json.loads(resp.read())
        if up.get("errcode") != 0:
            return {"ok": False, "error": f"上传失败: {up}"}
        media_id = up["media_id"]

    # 3. 发送文件消息（用 x-acs-dingtalk-access-token header）
    send_url = "https://api.dingtalk.com/v1.0/robot/oToMessages/batchSend"
    send_data = {
        "robotCode": robot_code,
        "userIds": [user_id],
        "msgKey": "sampleFile",
        "msgParam": json.dumps({
            "mediaId": media_id,
            "fileName": filename,
            "fileType": ext
        })
    }
    req3 = urllib.request.Request(send_url, data=json.dumps(send_data).encode(),
        headers={"Content-Type": "application/json", "x-acs-dingtalk-access-token": token})
    try:
        with urllib.request.urlopen(req3) as resp:
            result = json.loads(resp.read())
            invalid = result.get("invalidStaffIdList", [])
            if invalid:
                return {"ok": False, "error": f"用户ID无效: {invalid}"}
            return {"ok": True, "media_id": media_id, "processQueryKey": result.get("processQueryKey")}
    except urllib.request.HTTPError as e:
        return {"ok": False, "error": f"发送失败({e.code}): {e.read().decode()}"}

if __name__ == "__main__":
    # 默认配置（Raj文档账号）
    DEFAULT_CLIENT_ID = "dingq6cbhz7pm5umdoh6"
    DEFAULT_CLIENT_SECRET = "7fr0w6A5r9O2Hl-w_oj-CICTPoMkLw_kgyuJAxNrVWLPSil6we2GqTTkp0M_IC7o"
    DEFAULT_ROBOT_CODE = "dingq6cbhz7pm5umdoh6"
    DEFAULT_USER_ID = "1104083318783932"  # 张煜

    args = sys.argv[1:]
    file_path = args[0] if len(args) > 0 else None
    client_id = args[1] if len(args) > 1 else DEFAULT_CLIENT_ID
    client_secret = args[2] if len(args) > 2 else DEFAULT_CLIENT_SECRET
    robot_code = args[3] if len(args) > 3 else DEFAULT_ROBOT_CODE
    user_id = args[4] if len(args) > 4 else DEFAULT_USER_ID

    if not file_path:
        print("用法: python3 send_dingtalk_file.py <file_path> [client_id] [client_secret] [robot_code] [user_id]")
        sys.exit(1)

    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 {file_path}")
        sys.exit(1)

    print(f"发送文件: {file_path}")
    print(f"目标用户: {user_id}")
    result = send_file(client_id, client_secret, robot_code, user_id, file_path)
    print(f"结果: {result}")
