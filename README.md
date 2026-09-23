<div align="center">

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)

English | [فارسی](README.FA.md)

</div>

# PolarisKit-Pro ⚡

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)](#)
[![Language](https://img.shields.io/badge/Language-Python%203%20%7C%20CustomTkinter-3776AB?logo=python&logoColor=white)](#)
[![Architecture](https://img.shields.io/badge/Architecture-x64-555555)](#)
[![Portability](https://img.shields.io/badge/Portability-Single--File%20EXE-brightgreen)](#)

A centralized, single-executable administrative control hub that integrates all **Polaris-Void** native Windows utilities into a high-performance, dark-themed graphical user interface.

PolarisKit-Pro bridges the gap between lightweight low-level system scripts (Batch, PowerShell, Registry) and modern desktop software. It eliminates external console popups by streaming live execution logs internally, manages administrator elevation seamlessly, and bundles interactive documentation for all integrated modules.

---

## Key Features

* **Single Portable Executable:** Zero installation, zero external runtimes. Entire runtime, embedded scripts, and fonts are packed into a single self-contained binary.
* **Unified Single Elevation:** Automatically prompts for administrative elevation (UAC) once at launch (`requireAdministrator`). All underlying tools execute with inherited high integrity without interrupting workflows.
* **Zero Console Popups (Silent Execution):** System operations run entirely in the background via `CREATE_NO_WINDOW`. Process stdout and stderr are captured and streamed line-by-line into the integrated real-time console.
* **Byte-Exact Native Payloads:** All 11 original tools (19 `.bat`, `.reg`, and `.ico` files) are embedded within the application in Base64 encoding and staged on-demand inside `%TEMP%\PolarisKit-Pro`.
* **Integrated In-App Documentation Preview:** Built-in Markdown renderer with custom typography, syntax styling, zebra-striped tables, and clickable links for all 22 English and Persian module READMEs.
* **Bilingual Dynamic Interface:** Instant live switching between English (LTR) and Persian (RTL) with embedded **Vazirmatn** typography.
* **Process Isolation & Safe Termination:** The `STOP` control terminates child process trees cleanly via `taskkill /F /T` to prevent GUI lockups during extended background tasks.
* **Built-in Vault Inspectors:** Inspect backup folders (`C:\User Backup`, `Backup_Driver`) directly within dedicated in-app modal viewers without opening Windows Explorer.
* **Audit Log Export:** Export session execution logs with a single click to the application's working directory.

---

## Integrated Modules Matrix

PolarisKit-Pro bundles all 11 standalone Polaris-Void utilities:

| # | Module | Category | Elevation | Target Folder | Description |
|---|---|---|:---:|:---:|---|
| **01** | **NCSI // No-Internet Fix** | Network | Required | No | Resolves false "No Internet Access" alerts and manages NCSI active probing without system reboots. |
| **02** | **User Folders Backup** | Backup | Required | No | Backs up/restores 6 key user shell folders to `C:\User Backup` using dynamic registry resolution and Robocopy. |
| **03** | **Spotlight Icon Toggle** | System | None | No | Toggles the desktop "Learn about this picture" icon via current-user registry flags. |
| **04** | **OEM Driver Backup** | Drivers | Required | No | Exports and reinstalls all third-party OEM drivers natively using DISM and PnPUtil. |
| **05** | **Display Driver Backup** | Drivers | Required | No | Class-filtered graphical display driver export tool designed for safe GPU maintenance. |
| **06** | **USB Immunizer** | Storage | Required | Yes (Root) | Creates read-only decoy structures to block rogue auto-folder creation and applies custom branding. |
| **07** | **DNS + Proxy Reset** | Network | Required | No | Resets network adapters to DHCP, clears wininet proxies, and flushes local DNS resolvers. |
| **08** | **Image/Video Renamer** | Files | None | Yes | Recursively standardizes image and video extensions with collision-avoidance suffixes. |
| **09** | **Directory Tree Exporter** | Audit | None | Yes | Generates clean, UTF-8 encoded visual directory trees with human-readable file sizes and timestamps. |
| **10** | **SHA-256 Tree Auditor** | Forensics | None | Yes | Recursively generates visual trees accompanied by SHA-256 hashes for data integrity verification. |
| **11** | **Subfolder Unpacker** | Files | None | Yes | Recursively moves all nested files to the selected root directory and removes empty subdirectories. |

---

## System Requirements

* **Operating System:** Windows 10 (Build 1809+) or Windows 11 (x64 architecture).
* **Privileges:** Administrator access (requested once at startup).
* **Dependencies:** None. All required interpreters (PowerShell, Windows Command Processor, Registry tools) are standard Windows components.

---

## Installation & Usage

### Running Pre-Built Binary
1. Download the latest `PolarisKit-Pro.exe` from the [Releases](https://github.com/Polaris-Void/PolarisKit-Pro/releases) page.
2. Run the executable. Accept the User Account Control (UAC) prompt.
3. Select an operation from the **MODULES** column.
4. If the selected module requires a target path (e.g., USB Immunizer, Renamer, Auditor), use the **BROWSE** button to lock the folder.
5. Click the corresponding action button. Monitor execution in the **LIVE LOG** terminal.

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
Nothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.
