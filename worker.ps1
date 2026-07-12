$ErrorActionPreference = "Continue"

# =========================
# Codex Windows Task Worker
# =========================

$ProjectDir = $PSScriptRoot
$RootDir    = Join-Path $ProjectDir ".codex-worker"
$TaskFile   = Join-Path $ProjectDir "TASKS.md"
$DoneFile   = Join-Path $RootDir "DONE.md"
$LogFile    = Join-Path $RootDir "worker.log"
$StateFile  = Join-Path $RootDir "processed.json"
$LockFile   = Join-Path $RootDir "worker.lock"

$CheckIntervalSeconds = 10
$RetryDelaySeconds    = 60

function Write-Log {
    param([string]$Message)

    $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$time] $Message"

    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

function Get-TaskHash {
    param([string]$Task)

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Task.Trim())
    $sha256 = [System.Security.Cryptography.SHA256]::Create()

    try {
        return (
            $sha256.ComputeHash($bytes) |
            ForEach-Object { $_.ToString("x2") }
        ) -join ""
    }
    finally {
        $sha256.Dispose()
    }
}

function Load-ProcessedTasks {
    if (-not (Test-Path $StateFile)) {
        return @{}
    }

    try {
        $raw = Get-Content -Path $StateFile -Raw -Encoding UTF8

        if ([string]::IsNullOrWhiteSpace($raw)) {
            return @{}
        }

        $items = $raw | ConvertFrom-Json
        $result = @{}

        foreach ($item in @($items)) {
            if (-not [string]::IsNullOrWhiteSpace([string]$item)) {
                $result[[string]$item] = $true
            }
        }

        return $result
    }
    catch {
        Write-Log "读取 processed.json 失败，将使用空状态：$($_.Exception.Message)"
        return @{}
    }
}

function Save-ProcessedTasks {
    param([hashtable]$Processed)

    @($Processed.Keys) |
        Sort-Object |
        ConvertTo-Json |
        Set-Content -Path $StateFile -Encoding UTF8
}

function Get-Tasks {
    if (-not (Test-Path $TaskFile)) {
        return @()
    }

    try {
        $content = Get-Content -Path $TaskFile -Raw -Encoding UTF8
    }
    catch {
        Write-Log "读取 TASKS.md 失败：$($_.Exception.Message)"
        return @()
    }

    if ([string]::IsNullOrWhiteSpace($content)) {
        return @()
    }

    $pattern = '(?s)---TASK---\s*(.*?)\s*---END---'
    $matches = [regex]::Matches($content, $pattern)

    $tasks = @()

    foreach ($match in $matches) {
        $task = $match.Groups[1].Value.Trim()

        if (-not [string]::IsNullOrWhiteSpace($task)) {
            $tasks += $task
        }
    }

    return $tasks
}

function Test-CodexInstalled {
    $command = Get-Command codex -ErrorAction SilentlyContinue

    if ($null -eq $command) {
        Write-Log "没有找到 codex 命令。请先安装并登录 Codex CLI。"
        Write-Log "安装命令：npm install -g @openai/codex"
        return $false
    }

    return $true
}

function Run-CodexTask {
    param(
        [string]$Task,
        [string]$Hash
    )

    $prompt = @"
你正在 Windows 本地项目中执行一个队列任务。

项目工作目录：
$ProjectDir

本次唯一任务：
$Task

执行要求：
1. 先读取项目结构以及项目中的 AGENTS.md、README、配置文件和相关源代码。
2. 只处理本次任务，不要读取或执行 TASKS.md 中的其他任务。
3. 不要盲目覆盖已有修改。
4. 直接完成修改，不要只给操作建议。
5. 根据需要运行测试、构建、检查或格式化命令。
6. 遇到错误时先分析并尝试修复。
7. 完成后简要说明修改内容、涉及文件和测试结果。
8. 不要修改 worker.ps1、processed.json、DONE.md 或 worker.log。
"@

    Write-Log "开始执行任务：$Hash"

    Push-Location $ProjectDir

    try {
        $output = & codex exec --full-auto $prompt 2>&1 | Out-String
        $exitCode = $LASTEXITCODE

        $safeOutput = $output.TrimEnd()

        $resultBlock = @"

## 任务 $Hash

处理时间：$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

### 原始任务

$Task

### Codex 输出

````text
$safeOutput
````

退出代码：$exitCode

---

"@

        Add-Content -Path $DoneFile -Value $resultBlock -Encoding UTF8

        if ($exitCode -eq 0) {
            Write-Log "任务执行成功：$Hash"
            return $true
        }

        Write-Log "任务执行失败，退出代码：$exitCode，任务：$Hash"
        return $false
    }
    catch {
        Write-Log "调用 Codex 时发生异常：$($_.Exception.Message)"
        return $false
    }
    finally {
        Pop-Location
    }
}

# 创建目录和基础文件
New-Item -ItemType Directory -Path $RootDir -Force | Out-Null
New-Item -ItemType Directory -Path $ProjectDir -Force | Out-Null

foreach ($file in @($TaskFile, $DoneFile, $LogFile)) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Path $file -Force | Out-Null
    }
}

# 防止重复启动
if (Test-Path $LockFile) {
    try {
        $oldPid = Get-Content -Path $LockFile -Raw -ErrorAction Stop

        if ($oldPid -match '^\d+$') {
            $oldProcess = Get-Process -Id ([int]$oldPid) -ErrorAction SilentlyContinue

            if ($null -ne $oldProcess) {
                Write-Host "已有 worker.ps1 正在运行，PID：$oldPid"
                exit 1
            }
        }

        Remove-Item -Path $LockFile -Force -ErrorAction SilentlyContinue
    }
    catch {
        Remove-Item -Path $LockFile -Force -ErrorAction SilentlyContinue
    }
}

Set-Content -Path $LockFile -Value $PID -Encoding ASCII

try {
    if (-not (Test-CodexInstalled)) {
        exit 1
    }

    $processed = Load-ProcessedTasks
    $failedUntil = @{}

    Write-Log "Codex 任务监听器已启动。"
    Write-Log "项目目录：$ProjectDir"
    Write-Log "任务文件：$TaskFile"
    Write-Log "检查间隔：$CheckIntervalSeconds 秒"
    Write-Log "请使用 ---TASK--- 和 ---END--- 包围每个任务。"
    Write-Log "按 Ctrl+C 可停止监听器。"

    while ($true) {
        try {
            $tasks = Get-Tasks

            foreach ($task in $tasks) {
                $hash = Get-TaskHash -Task $task

                if ($processed.ContainsKey($hash)) {
                    continue
                }

                if ($failedUntil.ContainsKey($hash)) {
                    if ((Get-Date) -lt $failedUntil[$hash]) {
                        continue
                    }

                    $failedUntil.Remove($hash)
                }

                $success = Run-CodexTask -Task $task -Hash $hash

                if ($success) {
                    $processed[$hash] = $true
                    Save-ProcessedTasks -Processed $processed
                    $failedUntil.Remove($hash)
                }
                else {
                    $failedUntil[$hash] = (Get-Date).AddSeconds($RetryDelaySeconds)
                    Write-Log "该任务将在 $RetryDelaySeconds 秒后允许重试：$hash"
                }
            }
        }
        catch {
            Write-Log "监听循环发生异常：$($_.Exception.Message)"
        }

        Start-Sleep -Seconds $CheckIntervalSeconds
    }
}
finally {
    Remove-Item -Path $LockFile -Force -ErrorAction SilentlyContinue
    Write-Log "Codex 任务监听器已停止。"
}
