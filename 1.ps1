# 转换指定目录下的所有 .py 和 .txt 文件到 UTF-8（保留换行符）
$directory = "E:\virtual-phone-emulator"  # 替换为你的目录路径
$extensions = @("*.py", "*.txt", "*.md", "*.ini", "*.json")  # 要转换的文件扩展名

Get-ChildItem -Path $directory -Recurse -Include $extensions | ForEach-Object {
    $filePath = $_.FullName
    $tempPath = "$filePath.temp"

    try {
        # 读取文件（自动检测编码）
        $reader = New-Object System.IO.StreamReader($filePath)
        $content = $reader.ReadToEnd()
        $reader.Close()

        # 写入为 UTF-8 编码
        $writer = New-Object System.IO.StreamWriter($tempPath, $false, [System.Text.Encoding]::UTF8)
        $writer.Write($content)
        $writer.Close()

        # 替换原始文件
        Move-Item -Path $tempPath -Destination $filePath -Force
        Write-Host "已转换: $filePath" -ForegroundColor Green
    }
    catch {
        Write-Host "转换失败: $filePath - $_" -ForegroundColor Red

        # 清理临时文件
        if (Test-Path $tempPath) {
            Remove-Item $tempPath -Force
        }
    }
}