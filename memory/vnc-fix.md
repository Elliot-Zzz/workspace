# VNC 问题记录

## 问题症状
VNC 连接后显示 "The X session cleanly exited!"，服务器自动关闭

## 原因分析
1. **xstartup 脚本问题**：`startxfce4` 执行后立即退出，导致 VNC 认为会话结束
2. **xfce4-session 冲突**：有残留的 xfce4-session 进程占用 display

## 解决方案
1. 修改 `~/.vnc/xstartup`，让 startxfce4 在后台持续运行：
```bash
#!/bin/sh
export XDG_CURRENT_DESKTOP=XFCE
export XDG_SESSION_TYPE=x11
/usr/bin/startxfce4 &
while true; do
    sleep 10
done
```

2. 启动命令加 `-localhost no` 允许外网访问：
```bash
vncserver :1 -geometry 1280x800 -depth 24 -localhost no
```

3. 遇到旧进程残留时，先清理：
```bash
pkill -9 -u elliot xfce
rm -f /tmp/.X*-lock /tmp/.X11-unix/X*
```
