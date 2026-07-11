# Pocket Operations firmware -- reads the boot-diagnostic NVM log off the
# Uncertainty module over its USB serial (CircuitPython REPL) connection.
# Auto-finds the board's COM port, interrupts the running program (Ctrl-C),
# and asks the REPL for the last boot outcome plus the boot-attempt counter.
# Writes everything to pocket_log_result.txt next to this script.

$ErrorActionPreference = "Stop"
$outFile = Join-Path $PSScriptRoot "pocket_log_result.txt"
"=== Pocket Operations log read: $(Get-Date) ===" | Out-File -FilePath $outFile -Encoding utf8

try {
    $candidates = Get-WmiObject Win32_PnPEntity | Where-Object { $_.Name -match "\(COM\d+\)" }
    $match = $candidates | Where-Object { $_.Name -match "CircuitPython|USB Serial|Seeed|XIAO" } | Select-Object -First 1
    if (-not $match) { $match = $candidates | Select-Object -First 1 }

    if (-not $match) {
        "No COM port found. Is the board plugged in and showing up as a serial device in Device Manager?" | Out-File -FilePath $outFile -Append -Encoding utf8
        exit 1
    }

    if ($match.Name -match "\((COM\d+)\)") {
        $portName = $matches[1]
    } else {
        "Found a device but couldn't parse its COM port name from: $($match.Name)" | Out-File -FilePath $outFile -Append -Encoding utf8
        exit 1
    }

    "Using port: $portName ($($match.Name))" | Out-File -FilePath $outFile -Append -Encoding utf8

    $port = New-Object System.IO.Ports.SerialPort($portName, 115200, [System.IO.Ports.Parity]::None, 8, [System.IO.Ports.StopBits]::One)
    $port.ReadTimeout = 2000
    $port.WriteTimeout = 2000
    $port.NewLine = "`r`n"
    $port.Open()
    # USB CDC virtual ports often need DTR/RTS asserted before the device
    # will actually start sending data back -- easy to miss since real
    # UART hardware doesn't care, but CircuitPython's USB serial does.
    $port.DtrEnable = $true
    $port.RtsEnable = $true
    Start-Sleep -Milliseconds 500

    # Interrupt whatever's running (safe even if it's already idle) and
    # clear out any old buffered output before we start.
    $port.Write([string][char]3)
    Start-Sleep -Milliseconds 800
    $port.DiscardInBuffer()

    $port.Write("`r`n")
    Start-Sleep -Milliseconds 400
    $port.Write("import microcontroller`r`n")
    Start-Sleep -Milliseconds 400
    $port.Write("bytes(microcontroller.nvm[0:64]).split(b'\x00')[0]`r`n")
    Start-Sleep -Milliseconds 500
    $port.Write("int.from_bytes(microcontroller.nvm[64:68], 'little')`r`n")
    Start-Sleep -Milliseconds 800

    # Keep draining for a few full seconds -- don't bail just because one
    # instant looked quiet, the board may still be catching up.
    $result = ""
    $quietCycles = 0
    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Milliseconds 150
        if ($port.BytesToRead -gt 0) {
            $result += $port.ReadExisting()
            $quietCycles = 0
        } else {
            $quietCycles++
            if ($quietCycles -ge 10) { break }  # ~1.5s of true silence
        }
    }

    $port.Close()

    "--- REPL output (raw) ---" | Out-File -FilePath $outFile -Append -Encoding utf8
    $result | Out-File -FilePath $outFile -Append -Encoding utf8
    "--- end ---" | Out-File -FilePath $outFile -Append -Encoding utf8
}
catch {
    "ERROR: $($_.Exception.Message)" | Out-File -FilePath $outFile -Append -Encoding utf8
}

"Done. Results written to $outFile" | Out-File -FilePath $outFile -Append -Encoding utf8
