$ErrorActionPreference = 'Stop'
$root = 'D:\2Work\Private\Projects\ts-knowledge-agent'
$python = Join-Path $root '.venv\Scripts\python.exe'
$logDir = Join-Path $env:LOCALAPPDATA 'ts-knowledge-agent\logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$env:TS_KB_MEMBER_ID = if ($env:TS_KB_MEMBER_ID) { $env:TS_KB_MEMBER_ID } else { 'local-member' }
$env:TS_KB_SOURCE_ROOT = if ($env:TS_KB_SOURCE_ROOT) { $env:TS_KB_SOURCE_ROOT } else { 'D:\2Work\Knowledge\TS' }
$env:TS_KB_KNOWLEDGE_REPO = if ($env:TS_KB_KNOWLEDGE_REPO) { $env:TS_KB_KNOWLEDGE_REPO } else { Join-Path $env:LOCALAPPDATA 'ts-knowledge-agent\knowledge-base\ts-knowledge-base' }
Set-Location $root
& $python -m ts_knowledge_agent.cli run-once --sync *>> (Join-Path $logDir 'scheduled-run.log')
exit $LASTEXITCODE
