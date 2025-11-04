Param(
  [string]$Dir = "dist"
)

if (-not (Test-Path $Dir)) {
  Write-Host "[guard] 跳过：目录不存在 -> $Dir"
  exit 0
}

# 仅检查文本文件并静默返回，通过退出码控制结果，避免大规模输出刷屏
$files = Get-ChildItem -Path $Dir -Recurse -File | Where-Object { $_.Extension -in ".js", ".css", ".html", ".map" }
$matches = @()
foreach ($f in $files) {
  $res = Select-String -Path $f.FullName -Pattern '127\.0\.0\.1:8000' -SimpleMatch
  if ($res) { $matches += $res }
}

if ($matches.Count -gt 0) {
  Write-Error "[guard] ERROR: 在 $Dir 中发现硬编码 127.0.0.1:8000"
  $matches | Select-Object -First 20 | ForEach-Object { Write-Host ("$($_.Path):$($_.LineNumber):$($_.Line)") }
  exit 1
} else {
  Write-Host "[guard] OK: 未发现硬编码 127.0.0.1:8000"
  exit 0
}