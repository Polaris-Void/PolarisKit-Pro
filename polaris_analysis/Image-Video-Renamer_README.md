<div align="center">

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)

English | [فارسی](README.FA.md)

</div>

# Media Batch Renamer (Images to JPG & Videos to MP4)

A set of high-speed, standalone Windows batch scripts designed to recursively scan directories and bulk-normalize image and video file extensions into standard **`.jpg`** and **`.mp4`** formats.

Equipped with intelligent collision prevention, these scripts guarantee that **no file is ever overwritten or lost**.

> **Note:** These utilities perform fast file extension renaming. They do not re-encode or transcode media streams.

---

## 📁 Included Scripts

| Script | Purpose | Supported Formats |
| :--- | :--- | :--- |
| **`Image to JPG Renamer.bat`** | Renames all image formats to `.jpg` | 50+ formats (PNG, WEBP, AVIF, TIFF, HEIC, PSD, Camera RAW, etc.) |
| **`Video to MP4 Renamer.bat`** | Renames all video formats to `.mp4` | 40+ formats (MKV, MOV, AVI, WEBM, FLV, TS, Pro RAW Video, etc.) |

---

## ✨ Features

- **🛡️ 100% Collision-Safe:** If a target filename already exists (e.g., `photo.jpg`), the script automatically appends an incremental suffix (`photo (1).jpg`, `photo (2).jpg`), preventing any file overwriting or data loss.
- **🔄 Deep Recursive Scan:** Processes all files in the current folder and travels through all subdirectories automatically.
- **🚫 Smart Format Exclusion:**
  - `Image to JPG Renamer` skips `.jpg` and `.gif` (preserving animated GIFs).
  - `Video to MP4 Renamer` skips files already having the `.mp4` extension.
- **🎯 Massive Format Support:**
  - **Images:** Common web formats, Apple HEIC/HEIF, Adobe PSD/AI/EPS, and Camera RAW profiles (CR2, CR3, NEF, ARW, DNG, RAF, RW2, etc.).
  - **Videos:** Standard containers, legacy formats (RMVB, VOB, WMV), modern web formats (WEBM), and professional cinematic RAW video (BRAW, R3D, ARI, CRM).
- **📊 Detailed Terminal Summary:** Real-time feedback with explicit status tags (`[OK]`, `[DUP]`, `[FAIL]`) and an audit summary showing renamed, suffixed, and failed counts.
- **⚡ Zero Dependencies:** Pure Windows Batch script (`.bat`). No Python, PowerShell, FFmpeg, or third-party binaries required.

---

## 🚀 How to Use

1. Copy the desired script (`Image to JPG Renamer.bat` or `Video to MP4 Renamer.bat`) into the root directory containing your media files.
2. **Double-click** the script to launch it.
3. The terminal will scan the folder and all subfolders, displaying the rename progress in real-time.
4. Review the final statistics report.
5. The console window will automatically close after 10 seconds (or upon pressing any key).

---

## 💻 System Requirements

- **Operating System:** Windows 7, Windows 8.1, Windows 10, or Windows 11.
- **Permissions:** Standard user permissions (Administrator rights needed only if files reside in protected system paths).

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
