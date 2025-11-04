Param(
  [string]$ComposeFile = "docker-compose.production.yml"
)

Write-Host "[rebuild] 开始前端无缓存重建 (compose: $ComposeFile)" -ForegroundColor Cyan

# 1) 无缓存构建 frontend 镜像
docker compose -f $ComposeFile build --no-cache frontend
if ($LASTEXITCODE -ne 0) { Write-Error "[rebuild] 构建失败"; exit 1 }

# 2) 强制重建 frontend 服务（该服务仅用于写入 dist 卷，不影响线上流量）
docker compose -f $ComposeFile up -d --force-recreate --no-deps frontend
if ($LASTEXITCODE -ne 0) { Write-Error "[rebuild] 重建服务失败"; exit 1 }

# 3) 复核 Nginx 容器内是否出现硬编码（静默检查，避免刷屏）
$nginxName = (docker compose -f $ComposeFile ps --services | Select-String -Pattern '^nginx$').ToString()
if ($nginxName) {
  Write-Host "[rebuild] 开始在 nginx 容器内复核构建产物" -ForegroundColor Cyan
  $cmd = "sh -lc 'cd /var/www/app && if grep -R -I -E -q \"127\\.0\\.0\\.1:8000\" assets; then echo ERROR; exit 1; else echo OK; fi'"
  docker compose -f $ComposeFile exec -T $nginxName sh -c $cmd
  if ($LASTEXITCODE -ne 0) { Write-Error "[rebuild] 复核失败：发现硬编码"; exit 1 }
}

Write-Host "[rebuild] 完成：前端无缓存重建 + 产物复核通过" -ForegroundColor Green
exit 0