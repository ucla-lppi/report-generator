# Add C:\python\ and C:\Program Files\wkhtmltopdf\bin\ to User PATH if missing
$pythonPath = "C:\python\"
$wkhtmlBin  = "C:\Program Files\wkhtmltopdf\bin"
$persistedPath = [Environment]::GetEnvironmentVariable('Path', 'User') -split ';'

foreach ($addPath in @($pythonPath, $wkhtmlBin)) {
    if ($persistedPath -notcontains $addPath) {
        $persistedPath += $addPath
    }
}

[Environment]::SetEnvironmentVariable('Path', ($persistedPath -join ';'), 'User')
Write-Output "Success! Updated PATH for web driver and wkhtmltopdf; new entries added if needed."
