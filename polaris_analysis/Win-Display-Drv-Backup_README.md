<div align="center">

# Display Driver Backup & Restore

**One-click Windows batch scripts to back up and restore third-party display (GPU) drivers using PnPUtil.**

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)
![Language](https://img.shields.io/badge/language-Batch%20%2B%20PowerShell-4EAA25?logo=powershell&logoColor=white)

English | [فارسی](README.FA.md)

</div>

---

## Overview

Graphics driver updates sometimes go wrong: black screens, lower performance, broken control panels, or a clean Windows install with no working GPU driver. **Display Driver Backup & Restore** gives you a simple safety net.

- `Backup_Display_Driver.bat` exports your currently installed third-party **Display class** drivers (NVIDIA, AMD, Intel, etc.) into a local folder.
- `Restore_Display_Driver.bat` reinstalls those saved drivers whenever you need them.

No installation, no extra tools, no dependencies. Everything uses components already built into Windows.

## Features

- One-click operation: just double-click the script
- Automatic Administrator elevation (UAC prompt), no need to "Run as administrator" manually
- Exports **only** third-party Display class drivers (`oem*.inf`), not your whole driver store
- Restore installs every driver package found in the backup folder, including subfolders
- Clear status messages (`[INFO]`, `[WARN]`, `[ERROR]`, `[SUCCESS]`) and meaningful exit codes
- Works offline
- Plain text scripts you can read and audit in a minute

## Requirements

| Requirement | Details |
|---|---|
| Operating system | Windows 10 or Windows 11 |
| Permissions | Administrator (requested automatically) |
| Tools | `pnputil` and Windows PowerShell 5.1 (both included with Windows) |

## Quick Start

### 1. Back up your current driver

1. Download or clone this repository.
2. Double-click **`Backup_Display_Driver.bat`**.
3. Accept the UAC prompt.
4. Wait for `[SUCCESS] Display drivers backed up successfully.`

### 2. Restore it later

1. Double-click **`Restore_Display_Driver.bat`**.
2. Accept the UAC prompt.
3. Wait for `[SUCCESS] Display drivers restored successfully.`
4. **Restart your computer** to apply the changes.

## Backup Location

Both scripts use the same fixed folder on your system drive:

```
%SystemDrive%\Backup_Display_Driver
```

On most PCs this is `C:\Backup_Display_Driver`.

> **Reinstalling Windows?** Copy this folder to a USB drive or another disk *before* formatting, then copy it back to the same path on the new installation and run the restore script.

To use a different location, edit this line at the top of **both** scripts:

```bat
set "BACKUP_DIR=%SystemDrive%\Backup_Display_Driver"
```

## How It Works

**Backup**

1. Checks for Administrator rights and re-launches itself elevated if needed.
2. Creates the backup folder if it does not exist.
3. Uses PowerShell's `Get-WindowsDriver -Online` to list installed third-party drivers whose class is *Display* (GUID `{4d36e968-e325-11ce-bfc1-08002be10318}`).
4. Exports each one with `pnputil /export-driver`.

**Restore**

1. Checks for Administrator rights and re-launches itself elevated if needed.
2. Verifies that the backup folder exists and contains `.inf` files.
3. Installs everything with:

```bat
pnputil /add-driver "%BACKUP_DIR%\*.inf" /subdirs /install
```

## Exit Codes and Messages

The backup script's PowerShell step returns these codes:

| Code | Meaning |
|---|---|
| `0` | All display drivers were exported successfully |
| `1` | Reading the driver list failed, or at least one export failed |
| `2` | No third-party Display class drivers were found |

## Notes

- Only **third-party** display drivers are backed up. The built-in *Microsoft Basic Display Adapter* driver is part of Windows and is not exported.
- The restore script installs **every** driver package inside the backup folder. Keep only the drivers you actually want to restore in it.
- If the backup folder is missing or contains no `.inf` files, the restore script stops with a clear message and changes nothing.
- A restart is recommended after restoring.

## Troubleshooting

| Problem | What to try |
|---|---|
| `Get-WindowsDriver failed` | Make sure the script runs elevated and that Windows is healthy (`sfc /scannow`, `DISM /Online /Cleanup-Image /RestoreHealth`). |
| `No third-party Display class drivers found` | Your PC is probably using the generic Microsoft driver. Install the GPU vendor's driver first, then run the backup again. |
| `Display backup directory not found` | Run the backup first, or copy your saved folder back to the expected path. |
| The window closes too quickly | The scripts wait 5 seconds before closing. Run them from an open Command Prompt to keep the output on screen. |

---

## ⚖️ Absolute Legal Disclaimer, Waiver & Limitation of Liability

This project is licensed under the **Apache License, Version 2.0**. This disclaimer expressly supplements, expands, and reinforces **Section 7 (Disclaimer of Warranty)** and **Section 8 (Limitation of Liability)** of the Apache License 2.0, and shall control to the maximum extent permitted by applicable law.

**FOR EDUCATIONAL, RESEARCH, AND INFORMATIONAL PURPOSES ONLY. NO COMMERCIAL WARRANTY OR LIABILITY IS ASSUMED.**

### 1. Complete Disclaimer of All Warranties
To the maximum extent permitted by applicable law, the Software (including all code, documentation, data, and related materials) is provided strictly on an **"AS IS"** and **"AS AVAILABLE"** basis, without any warranties or conditions of any kind, whether express, implied, statutory, customary, or otherwise. This includes, without limitation, any warranties of merchantability, fitness for a particular purpose, non-infringement, title, security, accuracy, completeness, uninterrupted or error-free operation, or freedom from viruses or other harmful components. The author(s), copyright holder(s), maintainer(s), and contributor(s) expressly disclaim all such warranties.

### 2. Absolute Limitation of Liability
Under no circumstances and under no legal theory (whether in contract, tort — including negligence, gross negligence, and willful misconduct — strict liability, product liability, or otherwise) shall the author(s), maintainer(s), contributor(s), or copyright holder(s) be liable for any damages whatsoever, including but not limited to direct, indirect, incidental, special, consequential, exemplary, punitive, or any other damages (including loss of data, profits, revenue, business interruption, system failure, hardware damage, security breaches, personal injury, or any other loss), arising out of or related to the use, inability to use, modification, distribution, or reliance upon the Software, even if advised of the possibility of such damages and even if any remedy fails of its essential purpose.

### 3. Assumption of All Risk & User Responsibility
Any use, cloning, modification, deployment, distribution, or reliance upon this Software is undertaken entirely at the user’s sole risk and discretion. The user is exclusively and solely responsible for:
- Ensuring full compliance with all applicable local, national, and international laws, regulations, export controls, and third-party terms;
- Evaluating the suitability, security, and legality of the Software for any purpose;
- Any consequences arising from its use or misuse.

Nothing in this repository constitutes legal, financial, cybersecurity, medical, architectural, or any other form of professional advice.

### 4. Broad Indemnification
By accessing, downloading, cloning, forking, viewing, compiling, distributing, or using any part of this repository, you irrevocably agree to indemnify, defend, and hold harmless the author(s), contributor(s), and copyright holder(s) from and against any and all claims, demands, actions, proceedings, liabilities, damages, losses, costs, and expenses (including reasonable attorneys’ fees and legal costs) arising out of or related to your access, use, misuse, modification, distribution, or violation of this disclaimer or any applicable law.

### 5. Severability & Maximum Enforceability
If any provision of this disclaimer is held to be unenforceable or invalid under applicable law, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed. The remaining provisions shall continue in full force and effect. This disclaimer shall be interpreted to provide the maximum protection permitted by law.

### 6. No Waiver of Non-Waivable Rights
Nothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.t any and all claims, demands, liabilities, damages, judgments, losses, costs, or expenses (including reasonable attorney fees and legal costs) resulting from your access, use, misuse, or violation of this disclaimer or applicable laws.
