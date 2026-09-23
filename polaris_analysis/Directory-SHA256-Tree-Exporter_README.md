<div align="center">

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)

English | [فارسی](README.FA.md)

</div>

# Directory Tree, Metadata & SHA-256 Auditor

A high-precision, automated Windows Batch & PowerShell hybrid utility designed to recursively scan directory structures, map visual folder hierarchies, extract file metadata, and calculate cryptographic **SHA-256 hashes** for comprehensive data integrity auditing.

It outputs an organized, wide-format UTF-8 report without requiring third-party tools, external libraries, or administrator privileges.

---

## ✨ Features

- **🔒 Cryptographic SHA-256 Hashing:** Generates a unique 64-character SHA-256 checksum for every file via native PowerShell (`Get-FileHash`) to verify data integrity and detect tampering or corruption.
- **🛡️ Error Resilient (Access Denied Handling):** Gracefully catches locked or restricted files and tags them as `<ACCESS DENIED>` without halting the scan.
- **🌳 Visual Directory Hierarchy:** Renders folder structures with clean Unicode box-drawing characters (`├──`, `└──`, `│`) for clear structural visualization.
- **📊 Detailed File Metadata:** Captures human-readable file sizes (formatted dynamically to B, KB, MB, or GB), exact modification dates, and creation dates.
- **📐 Dynamic Wide-Table Formatting:** Measures path lengths and automatically aligns columns and table borders to comfortably accommodate deep folder paths and 64-character hashes.
- **📈 Statistical Summary:** Provides an audit summary displaying total folders scanned, total files processed, aggregate size (both human-readable and raw bytes), and execution time using high-precision timers.
- **🌐 Full UTF-8 Encoding:** Accurately preserves international filenames, Persian/Arabic characters, special symbols, and emojis without encoding errors.
- **🛡️ Self-Excluding Log:** Automatically ignores its own log file (`File List Log.txt`) during scanning to prevent skewed audit numbers.
- **⚡ Zero Dependencies:** 100% native Windows script using Command Prompt and PowerShell.

---

## 📄 Output Preview

The generated `File List Log.txt` creates an organized tabular report similar to this:

```text
=================================================================================================================================================================
                                                                DIRECTORY TREE & FILE AUDIT REPORT                                                               
=================================================================================================================================================================
  Target Path  :  C:\MyProject
  Generated On :  2026-09-15 16:00:00
=================================================================================================================================================================

  PATH / TREE STRUCTURE                   SIZE         DATE MODIFIED          DATE CREATED                            SHA-256 HASH                          
  ---------------------------------   ----------   -------------------   -------------------   ----------------------------------------------------------------
  .                                       <DIR>    2026-09-15 15:30:10   2026-09-15 15:30:10   -                                                               
  ├── src/                                <DIR>    2026-09-15 15:45:22   2026-09-15 15:30:15   -                                                               
  │   ├── index.js                     12.45 KB    2026-09-15 15:44:00   2026-09-15 15:31:00   A1B2C3D4E5F60718293A4B5C6D7E8F90123456789ABCDEF0123456789ABCDEF0
  │   └── utils.js                      4.10 KB    2026-09-15 15:40:12   2026-09-15 15:31:20   E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855
  └── README.md                         1.85 KB    2026-09-15 15:50:00   2026-09-15 15:30:10   8F434346648F6B96DF89DDAE13A4C7F7AB190A97A0DF161A92804CFD363D52A0
  ---------------------------------   ----------   -------------------   -------------------   ----------------------------------------------------------------

=================================================================================================================================================================
                                                                       STATISTICAL SUMMARY                                                                       
=================================================================================================================================================================
  Total Folders   :  1
  Total Files     :  3
  Total File Size :  18.40 KB (18,842 Bytes)
  Execution Time  :  0.42 Seconds
=================================================================================================================================================================
```

---

## 🚀 How to Use

1. Place the script file (saved with a `.bat` extension, e.g., `Export-File-List-SHA256.bat`) inside the directory you want to audit.
2. **Double-click** the script to execute it.
3. The terminal will display real-time scan progress and statistics.
4. A report file named **`File List Log.txt`** will be generated in the same directory.
5. The console window will automatically close after 5 seconds (or upon pressing any key).

---

## 💻 System Requirements

- **OS:** Windows 8.1, Windows 10, or Windows 11.
- **PowerShell:** Version 4.0 or later (required for `Get-FileHash`; enabled by default on Windows 8.1, 10, and 11).
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
