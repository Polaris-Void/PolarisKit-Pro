<div align="center">

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white)

English | [فارسی](README.FA.md)

</div>

# ⚡ PolarisKit-Pro // Windows Toolkit Hub

<div align="center">

![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Version](https://img.shields.io/badge/Version-v1.5--PRO-00F0FF?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-Apache%202.0-F59E0B?style=for-the-badge)
![UI](https://img.shields.io/badge/UI-CustomTkinter%20%7C%20Modern%20Dark-D946EF?style=for-the-badge)
![Elevation](https://img.shields.io/badge/Privileges-UAC%20Admin-DC2626?style=for-the-badge)

**All 11 Windows native maintenance, forensic, and repair tools by Polaris-Void in a single, unified, high-performance desktop suite.**

[Key Features](#-key-features) • [Module Directory](#-module-directory) • [Build from Source](#-build-from-source) • [Project Structure](#-project-structure) • [Legal Disclaimer](#-absolute-legal-disclaimer-waiver--limitation-of-liability)

</div>

---

## 🌟 Overview

**PolarisKit-Pro** is an all-in-one portable Windows hub consolidating the complete utility suite developed by **Polaris-Void (Avatar)**. Instead of juggling dozens of standalone Batch and PowerShell scripts across scattered repositories, PolarisKit-Pro encapsulates all **19 raw payloads byte-for-byte** into an elegant modern dark-themed interface.

Everything runs elevated from startup, with zero secondary popups, streaming live output directly into an internal console terminal with full Arabic/Persian and English localization.

---

## ✨ Key Features

* **🔐 Elevated at Launch (UAC Integration):** Single UAC prompt on startup (`requireAdministrator`). No subsequent elevation prompts interrupt your maintenance operations.
* **🖥️ Zero-Popup Architecture:** All underlying Batch and PowerShell scripts are dispatched silently (`CREATE_NO_WINDOW`). Output streams line-by-line in real-time within the app.
* **🛡️ Tree-Killing Process Controller:** Running tasks can be terminated instantly via `STOP`. Sub-processes (such as DISM or Robocopy) are killed cleanly via recursive process tree management (`taskkill /T /F`), eliminating UI freeze.
* **📖 Native Markdown Preview Engine:** Project Readmes are rendered natively in-app with rich typography (headings, styled monospace tables, zebra rows, inline amber code, and clickable URLs) — no raw markup strings.
* **✒️ Vazirmatn Typography & Pixel-Level Alignment:** Complete RTL/LTR bidirectional support. Custom `PButton` geometry engine eliminates font ascent/descent offsets for pixel-perfect button alignment.
* **🗃️ In-App Vault Inspector:** Check backup folders (size, file counts, and folder structure) directly inside the app without opening Windows File Explorer.
* **🧠 Operational State Log:** Step-by-step dispatch status, privilege validations, payload checksums, and exit codes displayed in real time.
* **💾 One-Click Log Export:** Export timestamped diagnostic and audit traces directly into the working directory.

---

## 🗂️ Module Directory

| # | Module Name | Scope | Admin? | Target Folder? | Core Mechanics & Purpose |
|:---:|:---|:---:|:---:|:---:|:---|
| **01** | **NCSI // No-Internet Fix** | Network | Yes | No | Clears fake "No Internet" yellow triangle / globe icons; toggles active probing and restarts `NlaSvc` on-the-fly without requiring a system reboot. |
| **02** | **User Folders Backup** | Storage | Yes | Fixed (`C:\User Backup`) | Backs up/restores 6 key user directories (`Desktop`, `Documents`, `Downloads`, `Pictures`, `Music`, `Videos`) via registry parsing and resilient Robocopy fallback. |
| **03** | **Spotlight Icon Toggle** | Desktop | No | No | Non-destructive registry toggle for the desktop "Learn about this picture" Spotlight icon via `HKCU` without disabling daily wallpapers. |
| **04** | **OEM Driver Backup** | System | Yes | Fixed (`Backup_Driver`) | Exports and reinstalls 100% of third-party OEM drivers using native Windows `DISM` and `PnPUtil`. |
| **05** | **Display Driver Backup** | Graphics | Yes | Fixed (`Backup_Display_Driver`) | Precision GPU driver backup isolated by Display class GUID (`{4d36e968-...}`) before DDU or driver clean-installs. |
| **06** | **USB Immunizer** | Removable | Yes | Yes (Root) | Immunizes flash drives using hidden dummy system folders (`System Volume Information`, `Android`) and injects branded custom `autorun.inf` and drive icons. |
| **07** | **DNS + Proxy Reset** | Network | Yes | No | Complete network triage: reverts all adapters to DHCP DNS, strips system-wide proxies (`HKCU`/`HKLM`), and flushes DNS cache. |
| **08** | **Image/Video Renamer** | Files | No | Yes | Recursive bulk media normalizer. Automatically standardizes extensions to `.jpg` and `.mp4` with zero overwrites (auto-appends duplicate counters). |
| **09** | **Directory Tree Exporter** | Audit | No | Yes | Generates clean, publication-ready UTF-8 text trees with dynamic box-drawing characters (`├──`, `└──`), human-readable file sizes, and timestamps. |
| **10** | **SHA-256 Tree Auditor** | Forensic | No | Yes | Deep cryptographic directory audit. Combines structural tree hierarchy with file metadata and per-file SHA-256 verification hashes. |
| **11** | **Subfolder Unpacker** | Files | No | Yes | Flattens messy nested directories by recursively pulling all nested files into the root folder. |

---

## 🚀 Getting Started

### Pre-Built Binary
1. Download `PolarisKit-Pro.exe` from the latest [Releases](../../releases) section.
2. Launch the application (Windows will request Administrator rights via UAC).
3. *(Optional)* If Windows SmartScreen appears due to lack of a commercial code-signing certificate: click **More info** ➔ **Run anyway**.

---

## 🛠️ Build from Source

### Prerequisites
* Windows 10 / 11 (64-bit)
* [Python 3.10+](https://www.python.org/downloads/) (Ensure `Add python.exe to PATH` is checked during installation)

### Automated 1-Click Build
1. Clone the repository:
   ```bash
   git clone https://github.com/Polaris-Void/PolarisKit-Pro.git
   cd PolarisKit-Pro/python
