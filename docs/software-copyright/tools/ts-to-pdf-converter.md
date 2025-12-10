# TypeScript 转 PDF 转换指南

## 转换方法汇总

### 方法一：VS Code 原生打印（推荐）
1. 打开要转换的 `.ts` 文件
2. 按 `Ctrl+P` (Windows) 或 `Cmd+P` (Mac)
3. 选择"打印"
4. 在打印机选项中选择"Microsoft Print to PDF"
5. 点击"打印"并选择保存位置

### 方法二：使用在线转换工具
1. 访问 https://codebeautify.org/typescript-to-pdf-converter
2. 上传或粘贴 TypeScript 代码
3. 点击转换并下载 PDF

### 方法三：浏览器打印
1. 在浏览器中打开 TypeScript 文件
2. 按 `Ctrl+P` (Windows) 或 `Cmd+P` (Mac)
3. 选择"另存为 PDF"
4. 调整边距和布局设置

## 打印设置建议

### 页面设置
- 纸张大小：A4
- 方向：纵向
- 边距：普通（默认）

### 布局设置
- 缩放：100%
- 选项：✓ 背景图形
- 页眉和页脚：根据需要设置

### 代码显示优化
- 确保语法高亮开启
- 字体大小：10-12pt
- 行号：建议显示行号

## 批量转换脚本

### Windows PowerShell 脚本
```powershell
# 批量打印TS文件为PDF
$files = Get-ChildItem -Path ".\source-code\" -Filter "*.ts"

foreach ($file in $files) {
    $pdfName = $file.BaseName + ".pdf"
    # 这里需要实际打印命令
    Write-Host "需要打印: $file -> $pdfName"
}
```

### 使用 pandoc（需要安装）
```bash
# 安装 pandoc
choco install pandoc

# 转换单个文件
pandoc -f markdown -t pdf -o output.pdf input.ts

# 批量转换
for file in ./source-code/*.ts; do
    pandoc -f markdown -t pdf -o "${file%.ts}.pdf" "$file"
done
```

## 软件著作权申请打印要求

### 格式要求
- 代码清晰可读
- 页码连续编号
- 文件头信息完整
- 装订边距充足

### 内容要求
- 包含完整源代码
- 重要注释保留
- 接口定义完整
- 核心算法突出

### 装订要求
- 左侧装订
- 每份材料单独装订
- 封面页注明软件名称和版本

## 常见问题解决

### 问题：代码换行被截断
**解决方案**：调整页面边距或减小字体大小

### 问题：语法高亮丢失
**解决方案**：使用VS Code打印功能保持高亮

### 问题：中文显示乱码
**解决方案**：确保文件编码为UTF-8