#!/usr/bin/env bash
# 审批短信验证码脚本（生产）
# 用途：只有管理员审批通过后，验证码才可用于注册
# 位置建议：/opt/mtm-helper/approve.sh

set -euo pipefail

API_BASE_DEFAULT="https://api.mtm-helper.com"

usage() {
  cat <<'USAGE'
用法：
  approve.sh -t <JWT> -P <手机号11位> -C <验证码> [-a <API_BASE>]
  approve.sh -u <管理员用户名> -p <管理员密码> -P <手机号11位> -C <验证码> [-a <API_BASE>]

说明：
  -t <JWT>            已登录管理员的访问令牌（推荐）。
  -u <用户名>         管理员用户名（如未提供 -t，可用 -u/-p 登录获取）。
  -p <密码>           管理员密码。
  -P <手机号>         需要审批的手机号（必须与发送验证码时一致，11位数字）。
  -C <验证码>         需要审批的验证码（来自短信）。
  -a <API_BASE>       API 基地址，默认 https://api.mtm-helper.com。
  -h                  显示本帮助。

依赖：
  - 必须安装 curl；可选 jq 或 python3（用于登录时解析 token），没有的话请用 -t 直接传入 JWT。

示例：
  1) 使用已获取的 JWT：
     ./approve.sh -t "$TOKEN" -P 13183826718 -C A30240

  2) 直接用管理员登录：
     ./approve.sh -u admin -p 'YourPassword!' -P 13183826718 -C A30240

返回：
  - 200：审批成功，验证码现在有效（在有效期内可用于注册）。
  - 400：请求体格式错误或验证码不匹配，请检查 JSON 与验证码；重新发送可能已生成新验证码。
  - 404：验证码不存在或已过期，请让用户重新获取验证码。
  - 401/403：鉴权失败或权限不足，请确认管理员身份或 JWT 有效。
USAGE
}

mask_phone() {
  local phone="$1"
  if [[ "$phone" =~ ^[0-9]{11}$ ]]; then
    echo "${phone:0:3}****${phone:7:4}"
  else
    echo "$phone"
  fi
}

TOKEN=""
USERNAME=""
PASSWORD=""
PHONE=""
CODE=""
API_BASE="${API_BASE_DEFAULT}"

while getopts ":t:u:p:P:C:a:h" opt; do
  case "$opt" in
    t) TOKEN="$OPTARG" ;;
    u) USERNAME="$OPTARG" ;;
    p) PASSWORD="$OPTARG" ;;
    P) PHONE="$OPTARG" ;;
    C) CODE="$OPTARG" ;;
    a) API_BASE="$OPTARG" ;;
    h) usage; exit 0 ;;
    *) echo "[ERROR] 无效参数：-$OPTARG"; usage; exit 2 ;;
  esac
done

if [[ -z "$PHONE" || -z "$CODE" ]]; then
  echo "[ERROR] 必须指定手机号(-P)与验证码(-C)。"
  usage
  exit 2
fi

if [[ ! "$PHONE" =~ ^[0-9]{11}$ ]]; then
  echo "[ERROR] 手机号必须为11位数字：$PHONE"
  exit 2
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "[ERROR] 未找到 curl，请安装后重试。"
  exit 2
fi

# 获取 TOKEN：优先使用 -t，其次尝试用户名密码登录
if [[ -z "$TOKEN" ]]; then
  if [[ -n "$USERNAME" && -n "$PASSWORD" ]]; then
    echo "[INFO] 使用管理员登录获取 JWT…"
    LOGIN_JSON=$(printf '{"username":"%s","password":"%s"}' "$USERNAME" "$PASSWORD")
    LOGIN_RESP=$(curl -sS -X POST "$API_BASE/api/auth/login/" \
      -H 'Content-Type: application/json' \
      --data "$LOGIN_JSON")
    if command -v jq >/dev/null 2>&1; then
      # 兼容后端返回的多种字段结构：
      # - data.tokens.access（当前后端）
      # - data.access / tokens.access / access
      # - access_token（部分历史/第三方返回）
      TOKEN=$(printf '%s' "$LOGIN_RESP" | jq -r '.data.tokens.access // .data.access // .tokens.access // .access // .data.access_token // .access_token // empty')
    elif command -v python3 >/dev/null 2>&1; then
      TOKEN=$(python3 - <<'PY'
import sys, json
try:
    d=json.loads(sys.stdin.read())
    token=(
        d.get('data',{}).get('tokens',{}).get('access') or
        d.get('data',{}).get('access') or
        d.get('tokens',{}).get('access') or
        d.get('access') or
        d.get('data',{}).get('access_token') or
        d.get('access_token') or
        ''
    )
    print(token)
except Exception:
    print('')
PY
      <<<"$LOGIN_RESP")
    else
      # 简单提取第一处 "access":"..."，适用于当前后端结构
      TOKEN=$(printf '%s' "$LOGIN_RESP" | sed -n 's/.*"access":"\([^"]*\)".*/\1/p')
    fi
    if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
      echo "[ERROR] 登录未返回有效 JWT。请检查管理员用户名/密码是否正确；若返回体中无 tokens.access 字段，请更新脚本或安装 jq/python3 以解析。"
      exit 3
    fi
  else
    echo "[ERROR] 需要提供 -t <JWT> 或 -u/-p 进行登录。"
    usage
    exit 2
  fi
fi

MASKED_PHONE=$(mask_phone "$PHONE")
TMP_BODY=$(mktemp)

echo "[INFO] 正在审批验证码：$MASKED_PHONE"

HTTP_CODE=$(printf '{"phone":"%s","code":"%s"}' "$PHONE" "$CODE" | \
  curl -sS -o "$TMP_BODY" -w '%{http_code}' "$API_BASE/api/auth/admin/approve-code/" \
    -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' \
    --data-binary @- )

BODY=$(cat "$TMP_BODY")
rm -f "$TMP_BODY"

echo "[HTTP_CODE] $HTTP_CODE"
echo "$BODY" | sed 's/\\n/\n/g'

if [[ "$HTTP_CODE" == "200" ]]; then
  echo "[SUCCESS] 已审批成功：$MASKED_PHONE。验证码在有效期内可用于注册（默认 5 分钟）。"
  exit 0
elif [[ "$HTTP_CODE" == "404" ]]; then
  echo "[WARN] 验证码不存在或已过期，请让用户重新发送验证码后再审批。"
  exit 4
elif [[ "$HTTP_CODE" == "401" || "$HTTP_CODE" == "403" ]]; then
  echo "[ERROR] 鉴权失败或权限不足，请确认管理员身份或 JWT 有效。"
  exit 5
else
  echo "[ERROR] 审批失败，请检查上面的返回体与参数是否正确。"
  exit 6
fi