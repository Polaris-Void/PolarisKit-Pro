<div align="center">

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)

English | [فارسی](README.FA.md)

</div>

# USB Immunizer & Customizer

A lightweight, automated Windows batch utility designed to immunize USB flash drives against automatic junk folder creation (such as `Android/`) and customize drive branding with a custom icon and volume label.

It keeps your USB storage clutter-free, stops smartphones and media devices from polluting your root directory, and makes your flash drive stand out with a professional appearance in Windows Explorer.

---

## 💡 How It Works (Folder Collision Immunity)

In standard filesystems (FAT32, exFAT, NTFS), a file and a folder **cannot share the exact same name** in the same directory.

When connecting a USB drive to an Android device (via OTG) or car multimedia system, the operating system attempts to automatically create directories like `Android/`. 

This tool creates a zero-byte **file** named `Android` marked with Hidden (`+h`) and System (`+s`) attributes. As a result, the OS is permanently blocked from generating unwanted folders in your root directory.

---

## 📁 Repository Contents

| File | Type | Description |
| :--- | :--- | :--- |
| **`Prevent Automatic Folder Creation on USB Drive.bat`** | Batch Script | Main script that creates immunity dummy files, writes `autorun.inf`, and applies hidden/system attributes. |
| **`.autorun.ico`** | Icon File | High-resolution custom flash drive icon applied to your USB drive. |

---

## ✨ Features

- **🛡️ Directory Immunity:** Blocks Android OS and external devices from creating root junk folders like `Android/`.
- **🎨 Custom Drive Branding:** Configures `autorun.inf` to display `.autorun.ico` and names the drive volume `Files` in Windows Explorer.
- **👻 Clean Root Directory:** Automatically applies Hidden and System attributes (`+h +s`) to:
  - `Android` (immunity dummy file)
  - `System Volume Information !` (immunity dummy file)
  - `autorun.inf` & `.autorun.ico`
  - `System Volume Information` & `.cm0013` (if already present)
- **🔑 Self-Elevating (UAC):** Automatically requests Administrator privileges via a temporary VBScript routine if not launched with elevated rights.
- **⚡ 100% Native & Portable:** Zero dependencies. Powered purely by Windows native utilities (`attrib`, `type`).

---

## 🚀 How to Use

1. Copy both **`Prevent Automatic Folder Creation on USB Drive.bat`** and **`.autorun.ico`** directly into the **root directory** of your USB flash drive (e.g., `E:\`).
2. **Double-click** the `.bat` file to execute.
3. Click **Yes** when prompted by the User Account Control (UAC) dialog.
4. The script will write the immunity files and apply the hidden/system flags.
5. **Safely remove and reconnect** your USB drive to see your custom drive icon and label in Windows Explorer.

---

## 💻 System Requirements

- **Operating System:** Windows 7, Windows 8.1, Windows 10, or Windows 11.
- **Filesystem:** FAT32, exFAT, or NTFS formatted USB drives.

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
