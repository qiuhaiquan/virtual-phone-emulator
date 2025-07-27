# ת��ָ��Ŀ¼�µ����� .py �� .txt �ļ��� UTF-8���������з���
$directory = "E:\virtual-phone-emulator"  # �滻Ϊ���Ŀ¼·��
$extensions = @("*.py", "*.txt", "*.md", "*.ini", "*.json")  # Ҫת�����ļ���չ��

Get-ChildItem -Path $directory -Recurse -Include $extensions | ForEach-Object {
    $filePath = $_.FullName
    $tempPath = "$filePath.temp"

    try {
        # ��ȡ�ļ����Զ������룩
        $reader = New-Object System.IO.StreamReader($filePath)
        $content = $reader.ReadToEnd()
        $reader.Close()

        # д��Ϊ UTF-8 ����
        $writer = New-Object System.IO.StreamWriter($tempPath, $false, [System.Text.Encoding]::UTF8)
        $writer.Write($content)
        $writer.Close()

        # �滻ԭʼ�ļ�
        Move-Item -Path $tempPath -Destination $filePath -Force
        Write-Host "��ת��: $filePath" -ForegroundColor Green
    }
    catch {
        Write-Host "ת��ʧ��: $filePath - $_" -ForegroundColor Red

        # ������ʱ�ļ�
        if (Test-Path $tempPath) {
            Remove-Item $tempPath -Force
        }
    }
}