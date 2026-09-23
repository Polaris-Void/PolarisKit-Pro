<div align="center">

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)

English | [فارسی](README.FA.md)

</div>

# Directory Tree & File Metadata Auditor

A fast, lightweight, and native Windows Batch & PowerShell hybrid utility designed to recursively scan directory structures, generate clean visual directory trees, and extract detailed file metadata into a formatted UTF-8 report.

It runs out-of-the-box without requiring external tools, third-party dependencies, or administrative privileges.

---

## ✨ Features

- **🌳 Visual Directory Hierarchy:** Maps folder contents using standard Unicode box-drawing characters (`├──`, `└──`, `│`) for clear structural visualization.
- **📊 Detailed Metadata Extraction:** Captures file sizes (formatted dynamically to B, KB, MB, or GB), exact modification dates, and creation dates.
- **📐 Dynamic Column Formatting:** Automatically calculates path lengths to keep table columns aligned and readable regardless of nested folder depth.
- **📈 Statistical Summary:** Provides an audit summary displaying total folders scanned, total files processed, aggregate size (both human-readable and raw bytes), and execution time using high-precision timers.
- **🌐 Full UTF-8 Encoding:** Accurately exports international filenames, Persian/Arabic characters, special symbols, and emojis without encoding corruption.
- **🛡️ Self-Excluding Log:** Automatically ignores its own log file (`File List Log.txt`) during scanning to prevent skewed audit numbers.
- **⚡ Zero Dependencies:** 100% native Windows script using Command Prompt and PowerShell.

---

## 📄 Output Preview

The generated `File List Log.txt` creates an organized tabular report similar to this:

```text
===================================================================================================
                                DIRECTORY TREE & FILE AUDIT REPORT                                 
===================================================================================================
  Target Path  :  C:\MyProject
  Generated On :  2026-09-15 16:00:00
===================================================================================================

  PATH / TREE STRUCTURE                   SIZE         DATE MODIFIED          DATE CREATED    
  ---------------------------------   ----------   -------------------   -------------------
  .                                       <DIR>    2026-09-15 15:30:10   2026-09-15 15:30:10
  ├── src/                                <DIR>    2026-09-15 15:45:22   2026-09-15 15:30:15
  │   ├── index.js                     12.45 KB    2026-09-15 15:44:00   2026-09-15 15:31:00
  │   └── utils.js                      4.10 KB    2026-09-15 15:40:12   2026-09-15 15:31:20
  └── README.md                         1.85 KB    2026-09-15 15:50:00   2026-09-15 15:30:10
  ---------------------------------   ----------   -------------------   -------------------

===================================================================================================
                                       STATISTICAL SUMMARY                                         
===================================================================================================
  Total Folders   :  1
  Total Files     :  3
  Total File Size :  18.40 KB (18,842 Bytes)
  Execution Time  :  0.24 Seconds
===================================================================================================
```

---

## 🚀 How to Use

1. Place the script file (saved with a `.bat` extension, e.g., `Export-File-List.bat`) inside the directory you want to audit.
2. **Double-click** the script to execute it.
3. The terminal will display real-time scan progress and terminal statistics.
4. A report file named **`File List Log.txt`** will be generated in the same directory.
5. The console window will automatically close after 5 seconds (or upon pressing any key).

---

## 💻 System Requirements

- **OS:** Windows 7, Windows 8.1, Windows 10, or Windows 11.
- **PowerShell:** Version 3.0 or later (installed by default on modern Windows).
- **Permissions:** Standard user privileges (Administrator access is **not** required unless scanning protected system folders).

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
