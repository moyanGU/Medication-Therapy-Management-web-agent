/**
 * 将 vapid_keys.json 中的 VAPID 公私钥安全追加到 backend/.env
 * 使用说明：先运行 gen_vapid.cjs 生成 vapid_keys.json，再运行本脚本。
 */
const fs = require('fs')
const path = require('path')

function main() {
  const projectRoot = path.resolve(__dirname, '../../')
  const jsonPath = path.join(projectRoot, 'vapid_keys.json')
  const envPath = path.join(projectRoot, 'backend', '.env')

  if (!fs.existsSync(jsonPath)) {
    console.error('缺少 vapid_keys.json，请先运行 scripts/windows/gen_vapid.cjs')
    process.exit(1)
  }

  const raw = fs.readFileSync(jsonPath, 'utf8').trim()
  let keys
  try {
    keys = JSON.parse(raw)
  } catch (e) {
    console.error('vapid_keys.json 内容不是有效 JSON：', e.message)
    process.exit(1)
  }

  const { publicKey, privateKey } = keys
  if (!publicKey || !privateKey) {
    console.error('vapid_keys.json 缺少 publicKey 或 privateKey 字段')
    process.exit(1)
  }

  const lines = [
    '',
    `VAPID_PUBLIC_KEY=${publicKey}`,
    `VAPID_PRIVATE_KEY=${privateKey}`,
    'VAPID_SUBJECT=mailto:noreply@local.dev',
    '',
  ]
  const content = lines.join('\n')

  fs.appendFileSync(envPath, content, 'utf8')
  console.log('已将 VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY 追加到 backend/.env')
}

main()