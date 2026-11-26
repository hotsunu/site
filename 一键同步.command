#!/bin/bash
# 一键同步：提交本地页面 -> 合并 GitHub 自动提交 -> 推送
# 用法：双击本文件，或在终端执行 bash 一键同步.command

cd "$(dirname "$0")" || exit 1
echo "[目录] $(pwd)"

# 0. 共享仓库由不同用户操作时，git 会报 dubious ownership，先信任当前目录
git config --global --add safe.directory "$(pwd)" 2>/dev/null

# 1. 暂存所有改动
git add -A

# 2. 有新文件就提交；没有则跳过（避免空提交报错中断）
if git diff --cached --quiet; then
  echo "[提示] 没有新的改动需要提交"
else
  git commit -m "添加新页面 $(date '+%Y-%m-%d %H:%M')"
  echo "[完成] 已提交本地改动"
fi

# 3. 关键步骤：先合并远端的自动提交，避免 fetch first 报错
echo "[步骤] 正在合并 GitHub 上的自动提交..."
if ! git pull --rebase origin main; then
  echo "[错误] 合并失败，已自动取消。请把终端内容截图发给助手处理。"
  git rebase --abort 2>/dev/null
  exit 1
fi

# 4. 推送
echo "[步骤] 正在推送到 GitHub..."
if git push origin main; then
  echo "[成功] 已推送完成，网页约 30 秒后自动更新"
else
  echo "[错误] 推送失败，请把终端内容截图发给助手处理。"
  exit 1
fi
