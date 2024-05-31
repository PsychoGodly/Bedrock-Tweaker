# Check if the script is running with administrative privileges
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run this script as an Administrator."
    exit
}

function Has-FullControlPermissions {
    param (
        [string]$FilePath
    )
    try {
        $result = icacls $FilePath
        if ($result -match "Everyone:(F)") {
            return $true
        } else {
            return $false
        }
    } catch {
        Write-Error "Error checking permissions for $FilePath: $($_.Exception.Message)"
        return $false
    }
}

function Set-FullControlPermissions {
    param (
        [string]$FilePath
    )
    if (Has-FullControlPermissions -FilePath $FilePath) {
        Write-Output "Full control permissions already granted for $FilePath"
        return $true
    }

    try {
        $result = icacls $FilePath /grant Everyone:F /T
        Write-Output $result
        return $true
    } catch {
        Write-Error "Error setting permissions for $FilePath: $($_.Exception.Message)"
        return $false
    }
}

function Take-Ownership {
    param (
        [string]$FilePath
    )
    try {
        $result = takeown /F $FilePath /A /R /D Y
        Write-Output $result
        return $true
    } catch {
        Write-Error "Error taking ownership of $FilePath: $($_.Exception.Message)"
        return $false
    }
}

function Remove-ReadOnlyAttribute {
    param (
        [string]$FilePath
    )
    try {
        attrib -r $FilePath
        Write-Output "Read-only attribute removed from $FilePath"
        return $true
    } catch {
        Write-Error "Error removing read-only attribute from $FilePath: $($_.Exception.Message)"
        return $false
    }
}

function Copy-AndReplaceFile {
    param (
        [string]$Src,
        [string]$Dst,
        [int]$MaxRetries = 5,
        [int]$Delay = 10
    )
    if (Test-Path $Dst) {
        Write-Output "File exists at $Dst, checking and setting permissions..."
        if (-not (Set-FullControlPermissions -FilePath $Dst)) {
            Write-Warning "Failed to set permissions for $Dst, attempting to copy anyway..."
        }
        if (-not (Remove-ReadOnlyAttribute -FilePath $Dst)) {
            Write-Warning "Failed to remove read-only attribute for $Dst, attempting to copy anyway..."
        }
        if (-not (Take-Ownership -FilePath $Dst)) {
            Write-Warning "Failed to take ownership of $Dst, attempting to copy anyway..."
        }
    }

    for ($attempt = 0; $attempt -lt $MaxRetries; $attempt++) {
        try {
            Copy-Item -Path $Src -Destination $Dst -Force
            Write-Output "Copied $Src to $Dst"
            return $true
        } catch {
            if ($attempt -lt $MaxRetries - 1) {
                Write-Warning "Error copying file from $Src to $Dst: $($_.Exception.Message). Retrying in $Delay seconds..."
                Start-Sleep -Seconds $Delay
            } else {
                Write-Error "Error copying file from $Src to $Dst after $MaxRetries attempts: $($_.Exception.Message)"
                return $false
            }
        }
    }
}

$patchFolder = Join-Path -Path (Get-Location) -ChildPath "Patch Files"
$syswow64Src = Join-Path -Path $patchFolder -ChildPath "sysWOW64\Windows.ApplicationModel.Store.dll"
$system32Src = Join-Path -Path $patchFolder -ChildPath "System32\Windows.ApplicationModel.Store.dll"

$windowsFolder = $env:WINDIR
$syswow64Dst = Join-Path -Path $windowsFolder -ChildPath "SysWOW64\Windows.ApplicationModel.Store.dll"
$system32Dst = Join-Path -Path $windowsFolder -ChildPath "System32\Windows.ApplicationModel.Store.dll"

$syswow64Success = Copy-AndReplaceFile -Src $syswow64Src -Dst $syswow64Dst
$system32Success = Copy-AndReplaceFile -Src $system32Src -Dst $system32Dst

if ($syswow64Success -and $system32Success) {
    Write-Output "Successfully done."
} else {
    Write-Error "An error occurred during the file copy process. Please ensure the files are not in use and try again."
}

if ($syswow64Success -or $system32Success) {
    Write-Warning "A system reboot is required to complete the operation."
    Write-Host "Please reboot your system and run the script again to continue."
    Read-Host -Prompt "Press Enter to exit..."
}
