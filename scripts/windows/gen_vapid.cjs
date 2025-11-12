/**
 * 生成 VAPID 公私钥并输出为 JSON（最后一行输出，便于采集）。
 * 仅用于本地开发环境，避免将密钥写入仓库文件。
 */
const webpush = require('web-push')

function main() {
  const keys = webpush.generateVAPIDKeys()
  // 统一输出为一行 JSON，避免日志截断导致丢失某一行
  console.log(JSON.stringify(keys))
}

main()