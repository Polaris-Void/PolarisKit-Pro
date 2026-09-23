<div align="center">

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)

English | [فارسی](README.FA.md)

</div>

# Network Troubleshooter: DNS & Proxy Reset

A lightweight, automated Windows batch utility designed to fix common network connectivity issues by resetting DNS server settings to DHCP, disabling system-wide proxies, and clearing the local DNS resolver cache.

Often, VPN clients, proxy tools (e.g., v2ray, Clash, Outline), anti-censorship software, or unexpected network crashes leave behind modified proxy configurations and static DNS addresses. These leftover settings prevent your browser and apps from accessing the internet. This script fixes all of them in a single click.

---

## ✨ Features

- **🔑 Automatic Elevation (UAC):** Checks for administrator privileges using `fsutil` and automatically prompts the UAC dialog via PowerShell if elevated rights are needed.
- **🌐 Reset DNS to DHCP:** Clears static or stuck DNS servers across **all** network adapters and resets them to automatic (DHCP) via PowerShell (`Get-NetAdapter | Set-DnsClientServerAddress -ResetServerAddresses`).
- **🚫 Disable System Proxy:** Forces `ProxyEnable = 0` in both User (`HKCU`) and System-wide (`HKLM`) Windows Registry locations to remove hanging proxy connections.
- **🧹 Flush DNS Cache:** Clears the Windows DNS resolver cache (`ipconfig /flushdns`) to apply changes immediately without requiring a system reboot.
- **⚡ Fast, Native & Clean:** Uses 100% built-in Windows tools (Batch & PowerShell) with clear status tags (`[+]`, `[-]`).

---

## 📋 Common Use Cases

- **"No Internet" after closing VPN/Proxy:** The VPN closed, but left the system proxy turned on.
- **Browser Errors:** You encounter `ERR_PROXY_CONNECTION_FAILED` or `DNS_PROBE_FINISHED_NO_INTERNET`.
- **Stuck DNS:** Network adapters are pointing to unreachable or dead DNS servers.

---

## 🚀 How to Use

1. Make sure the script file is saved with the `.bat` extension (e.g., `Reset-DNS-Proxy.bat`).
2. **Double-click** the script to run it.
3. If prompted by **User Account Control (UAC)**, click **Yes**.
4. The script will execute all steps automatically.
5. Once you see `All tasks completed successfully.`, press any key to close the window.

---

## 💻 System Requirements

- **OS:** Windows 8.1, Windows 10, or Windows 11 (32-bit & 64-bit).
- **PowerShell:** Version 5.0 or later (pre-installed on Windows 10 & 11).
- **Permissions:** Administrator access (requested automatically by the script).

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
