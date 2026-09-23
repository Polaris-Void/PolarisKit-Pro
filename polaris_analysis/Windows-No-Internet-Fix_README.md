<div align="center">

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)

English | [فارسی](README.FA.md)

</div>

# Windows NCSI & Internet Probing Manager

A lightweight Windows utility consisting of Registry tweaks and a self-elevating Batch script designed to manage the **Network Connectivity Status Indicator (NCSI)** Active Probing feature and restart the Network Location Awareness (`NlaSvc`) service.

It resolves common Windows issues such as false "No Internet Access" alerts (globe icon or yellow exclamation mark when the internet is actually working), eliminates unexpected captive-portal browser popups, and provides privacy control over periodic Microsoft network probing requests.

---

## 📁 Repository Contents

| File | Type | Description |
| :--- | :--- | :--- |
| **`Restart Network Service.bat`** | Batch Script | Automatically requests Administrator rights and restarts the `NlaSvc` service (and dependencies) to apply changes immediately. |
| **`Enable Internet Probing.reg`** | Registry File | Sets `EnableActiveProbing = 1` to restore the default Windows network connectivity checks. |
| **`Disable Internet Probing.reg`** | Registry File | Sets `EnableActiveProbing = 0` to stop Windows from polling `msftconnecttest.com`. |

---

## ✨ Features

- **🔑 Automatic Elevation (UAC):** The batch file detects privilege levels and automatically requests Administrator access via PowerShell.
- **⚡ Instant Effect Without Reboot:** Restarts `NlaSvc` with dependent services forced (`/y`), refreshing the system tray network indicator in seconds without restarting the computer.
- **🌐 Fixes False "No Internet" Icon:** Resolves cases where browsers and apps can connect to websites, but Windows incorrectly reports "No Internet, secured".
- **🛡️ Privacy & Telemetry Management:** Disables recurring HTTP polling to Microsoft servers (`msftconnecttest.com` and `ipv6.msftconnecttest.com`).
- **📦 Clean & Native:** 100% native Windows files with zero external dependencies.

---

## 🚀 How to Use

### Step 1: Choose Your Desired Configuration
- To **disable** internet probing (fix false captive portals / stop telemetry):  
  Double-click **`Disable Internet Probing.reg`** and click **Yes** to merge.
- To **restore default** internet probing:  
  Double-click **`Enable Internet Probing.reg`** and click **Yes** to merge.

### Step 2: Apply Changes
- Double-click **`Restart Network Service.bat`**.
- Accept the **UAC** prompt when prompted.
- The script will stop and restart the network service. The network tray icon will refresh automatically within 5 seconds.

---

## 💻 System Requirements

- **OS:** Windows 7, Windows 8.1, Windows 10, or Windows 11.
- **Permissions:** Administrator access (handled automatically by the batch script).

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
