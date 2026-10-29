# Lumo ko Windows login pe apne aap chalu karne ke liye Task Scheduler task banata hai.
$root   = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\pythonw.exe"
$script = Join-Path $root "run_voice.py"

if (-not (Test-Path $python)) { Write-Error "pythonw.exe nahi mila: $python"; exit 1 }
if (-not (Test-Path $script)) { Write-Error "run_voice.py nahi mila: $script"; exit 1 }

$action   = New-ScheduledTaskAction -Execute $python -Argument "`"$script`"" -WorkingDirectory $root
$trigger  = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$trigger.Delay = "PT20S"   # login ke 20 second baad (audio/Ollama ready hone do)

# Zaroori settings: default mein task battery pe nahi chalta aur 3 din baad band ho jaata hai
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName "Lumo" -Action $action -Trigger $trigger `
    -Settings $settings -Description "Lumo voice assistant" -Force | Out-Null

Write-Host "Task 'Lumo' ban gaya. Agli login pe Lumo apne aap chalu hoga."