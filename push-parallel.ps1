# Script PowerShell para hacer push a ambos repositorios en PARALELO
# Uso: .\push-parallel.ps1 [branch]
# Ejemplo: .\push-parallel.ps1 main

param(
    [string]$Branch = "main"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Push Multi-Remote PARALELO" -ForegroundColor Cyan
Write-Host "GitHub y UCASAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Rama: $Branch" -ForegroundColor Yellow
Write-Host ""

# Verificar que estamos en un repositorio Git
if (-not (Test-Path .git)) {
    Write-Host "ERROR: No se encuentra un repositorio Git en este directorio." -ForegroundColor Red
    exit 1
}

# Verificar que la rama existe localmente
$branchExists = git rev-parse --verify "$Branch" 2>$null
if (-not $branchExists) {
    Write-Host "ERROR: La rama '$Branch' no existe localmente." -ForegroundColor Red
    Write-Host "Ramas disponibles:" -ForegroundColor Yellow
    git branch
    exit 1
}

# Variables para tracking
$results = @{
    GitHub = $null
    UCASAL = $null
}

# Función para hacer push (no usada en versión paralela, pero útil para referencia)
function Push-ToRemote {
    param(
        [string]$RemoteName,
        [string]$RemoteUrl,
        [string]$BranchName
    )
    
    Write-Host "[$RemoteName] Iniciando push..." -ForegroundColor Yellow
    Write-Host "  URL: $RemoteUrl" -ForegroundColor Gray
    
    $output = git push $RemoteName $BranchName 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[$RemoteName] Push exitoso" -ForegroundColor Green
        return $true
    } else {
        Write-Host "[$RemoteName] Push fallo" -ForegroundColor Red
        Write-Host $output -ForegroundColor Red
        return $false
    }
}

# Obtener URLs de los remotes
$originUrl = git remote get-url origin
$ucasalUrl = git remote get-url ucasal

Write-Host "Remotes configurados:" -ForegroundColor Cyan
Write-Host "  origin: $originUrl" -ForegroundColor Gray
Write-Host "  ucasal: $ucasalUrl" -ForegroundColor Gray
Write-Host ""

# Iniciar pushes en paralelo usando jobs
Write-Host "Iniciando pushes en PARALELO..." -ForegroundColor Cyan
Write-Host ""

$currentPath = Get-Location

$job1 = Start-Job -ScriptBlock {
    param($remote, $branch, $path)
    Set-Location $path
    $result = git push $remote $branch 2>&1
    Write-Output $LASTEXITCODE
    Write-Output $result
} -ArgumentList "origin", $Branch, $currentPath

$job2 = Start-Job -ScriptBlock {
    param($remote, $branch, $path)
    Set-Location $path
    $result = git push $remote $branch 2>&1
    Write-Output $LASTEXITCODE
    Write-Output $result
} -ArgumentList "ucasal", $Branch, $currentPath

# Mostrar progreso
Write-Host "Esperando que completen los pushes..." -ForegroundColor Yellow
Write-Host ""

# Esperar a que ambos jobs completen
$jobs = @($job1, $job2)
$completed = @()

while ($completed.Count -lt $jobs.Count) {
    foreach ($job in $jobs) {
        if ($job.State -eq "Completed" -and $job.Id -notin $completed) {
            $completed += $job.Id
            $output = Receive-Job -Job $job
            if ($output -and $output.Count -gt 0) {
                $exitCode = $output[0]
                $outputText = $output[1..($output.Count-1)] -join "`n"
            } else {
                $exitCode = 0
                $outputText = ""
            }
            
            if ($job.Id -eq $job1.Id) {
                $remoteName = "GitHub (origin)"
                $results.GitHub = ($exitCode -eq 0)
            } else {
                $remoteName = "UCASAL"
                $results.UCASAL = ($exitCode -eq 0)
            }
            
            if ($exitCode -eq 0) {
                Write-Host "[$remoteName] Push completado exitosamente" -ForegroundColor Green
            } else {
                Write-Host "[$remoteName] Push fallo" -ForegroundColor Red
                if ($outputText) {
                    Write-Host $outputText -ForegroundColor Red
                }
            }
        }
    }
    Start-Sleep -Milliseconds 500
}

# Limpiar jobs
Remove-Job -Job $jobs -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Resumen:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($results.GitHub) {
    Write-Host "GitHub (origin):  Exitoso" -ForegroundColor Green
} else {
    Write-Host "GitHub (origin):  Fallo" -ForegroundColor Red
}

if ($results.UCASAL) {
    Write-Host "UCASAL:           Exitoso" -ForegroundColor Green
} else {
    Write-Host "UCASAL:           Fallo" -ForegroundColor Red
}

Write-Host ""

# Determinar código de salida
if ($results.GitHub -and $results.UCASAL) {
    Write-Host "Ambos pushes completados exitosamente" -ForegroundColor Green
    exit 0
} elseif ($results.GitHub -or $results.UCASAL) {
    Write-Host "Al menos un push fue exitoso" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "Ambos pushes fallaron" -ForegroundColor Red
    exit 1
}

