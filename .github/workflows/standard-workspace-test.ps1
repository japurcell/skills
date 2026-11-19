param([switch]$StandardUser, [string]$Interpreter, [string]$Scratch)
$ErrorActionPreference = 'Stop'
if ($StandardUser) {
    $env:TEMP = $Scratch
    $env:TMP = $env:TEMP
    $env:TMPDIR = $env:TEMP
    New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
    $env:PYTHONUTF8 = '1'
    $probe = & $Interpreter -c 'import tempfile; print(tempfile.mkdtemp(prefix="owner-probe-"))'
    Write-Output "Standard caller $(whoami); workspace owner $((Get-Acl -LiteralPath $probe).Owner)"
    & $Interpreter -m unittest discover -v -s skills/default/brain-install/tests
    exit $LASTEXITCODE
}
$python = (Get-Command python -CommandType Application | Select-Object -First 1).Source
$probe = & $python -c 'import tempfile; print(tempfile.mkdtemp(prefix="owner-probe-"))'
Write-Output "Elevated runner workspace owner: $((Get-Acl -LiteralPath $probe).Owner); caller: $(whoami)"
$suffix = [Guid]::NewGuid().ToString('N').Substring(0, 10)
$account = "skillci-$suffix"
$scratch = "C:\skillci-$suffix"
$secret = ConvertTo-SecureString (([Guid]::NewGuid().ToString('N')) + 'aA!2') -AsPlainText -Force
$credential = [PSCredential]::new("$env:COMPUTERNAME\$account", $secret)
$created = New-LocalUser -Name $account -Password $secret
try {
    Add-LocalGroupMember -SID 'S-1-5-32-545' -Member $created -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path $scratch | Out-Null
    & icacls $scratch /inheritance:r /grant:r ("${account}:(OI)(CI)F") '*S-1-5-32-544:(OI)(CI)F' '*S-1-5-18:(OI)(CI)F'
    if ($LASTEXITCODE) { throw 'Could not grant the standard test user its scratch directory' }
    $out = Join-Path $env:RUNNER_TEMP 'skillci.stdout'
    $err = Join-Path $env:RUNNER_TEMP 'skillci.stderr'
    $arguments = @('-NoProfile','-File', ('"{0}"' -f $PSCommandPath), '-StandardUser','-Interpreter', ('"{0}"' -f $python), '-Scratch', ('"{0}"' -f $scratch))
    $proc = Start-Process -FilePath (Get-Command pwsh).Source -Credential $credential -LoadUserProfile -WorkingDirectory $PWD.Path -ArgumentList $arguments -Wait -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
    Get-Content -LiteralPath $out
    Get-Content -LiteralPath $err
    $result = $proc.ExitCode
} finally {
    Remove-LocalUser -Name $account
    if (Test-Path -LiteralPath $scratch) { Remove-Item -LiteralPath $scratch -Recurse -Force }
}
exit $result
