# -*- coding: utf-8 -*-
"""
POLARIS-VOID // CYBER TOOLKIT  --  PRO EDITION
All 11 Polaris-Void utilities in one neon hub. Single-file, portable.

- Starts ELEVATED (UAC once at launch; frozen exe uses requireAdministrator).
- Zero popups: every tool runs HIDDEN, output streams live into the in-app log.
- UI font: Vazirmatn (bundled, loaded privately per-process, OFL-1.1).
- Bilingual EN/FA with per-paragraph RTL/LTR justification.

Run (dev):      pip install -r requirements.txt && python PolarisKit.py
Build EXE:      run Build-EXE.bat on Windows  ->  dist\\PolarisKit-Pro.exe
"""
import os, re, sys, ctypes, queue, threading, time, subprocess, webbrowser
from dataclasses import dataclass, field

# ---------------------------------------------------------------- payloads
try:
    from payloads import get_payload
except ImportError:
    print("payloads.py not found next to PolarisKit.py")
    sys.exit(1)

try:
    import customtkinter as ctk
    from tkinter import filedialog, PhotoImage
except ImportError:
    print("Need: pip install -r requirements.txt  (customtkinter missing)")
    sys.exit(1)

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAVE_BIDI = True
except ImportError:
    HAVE_BIDI = False

IS_WIN = (os.name == "nt")

# ---------------------------------------------------------------- theme
BG      = "#080a12"
PANEL   = "#0d111c"
CARD    = "#101624"
CYAN    = "#00e6ff"
MAGENTA = "#ff0080"
GREEN   = "#00ffaa"
AMBER   = "#ffb000"
TXT     = "#cddcee"
GRAY    = "#788496"
BORDER  = "#1c2740"

UI_FONT   = "Vazirmatn"   # Persian + Latin UI
MONO_FONT = "Consolas"    # neural log + ASCII tool tables

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ---------------------------------------------------------------- data
@dataclass
class Action:
    label: str
    kind: str            # script | reg | cmd | vault | link
    resid: str = ""
    admin: bool = False
    need_folder: bool = False
    copy_ico: bool = False
    cmd: str = ""
    args: str = ""
    path: str = ""       # vault dir (env-expandable) or URL
    argv: str = ""        # extra args appended when launching staged script
    confirm: str = ""    # key into CONFIRM_TEXTS: ask in-app, pipe YES to stdin

@dataclass
class Module:
    mid: str
    title: str
    cat: str
    tech: str
    en: str
    fa: str
    url: str
    acts: list = field(default_factory=list)

GITHUB = "https://github.com/Polaris-Void"
MODULES = [
    Module("NCSI-FIX", "NCSI No-Internet Fix", "NET",
        "registry tweak + NlaSvc restart",
        'Fix false "No Internet" alerts (globe icon / yellow bang while the web works), kill surprise captive-portal popups, and control Microsoft active probing telemetry.',
        "رفع خطای کاذب No Internet (آیکون کره یا علامت زرد با وجود اینترنت سالم)، توقف پاپ‌آپ‌های captive-portal و کنترل درخواست‌های دوره‌ای مایکروسافت، بدون نیاز به ریبوت.",
        GITHUB + "/Windows-No-Internet-Fix", [
            Action("DISABLE PROBING", "reg", "NCSI_DISABLE", True),
            Action("ENABLE PROBING", "reg", "NCSI_ENABLE", True),
            Action("RESTART NLA SVC", "script", "NCSI_RESTART", True, argv="admin"),
        ]),
    Module("USER-BACKUP", "User Folders Backup", "BACKUP",
        "robocopy + registry path resolution",
        "Backup Desktop, Downloads, Documents, Pictures, Music, Videos to C:\\User Backup. Resolves real paths from the registry (OneDrive aware). Restore merges back without overwriting anything.",
        "بکاپ خودکار پوشه‌های کاربر در C:\\User Backup با Robocopy؛ مسیرها از رجیستری خوانده می‌شود (سازگار با OneDrive) و بازیابی هیچ فایلی را بازنویسی نمی‌کند.",
        GITHUB + "/Win-User-Backup", [
            Action("BACKUP NOW", "script", "USERBACKUP", True),
            Action("RESTORE (MERGE)", "script", "USERRESTORE", True, confirm="restore"),
            Action("VIEW VAULT", "vault", path="C:\\User Backup"),
        ]),
    Module("SPOTLIGHT", "Spotlight Icon Toggle", "DESKTOP",
        "HKCU registry tweak",
        'Remove the annoying "Learn about this picture" desktop icon while keeping Spotlight wallpapers alive. One click to hide, one click to bring it back.',
        "حذف آیکون مزاحم «Learn about this picture» از دسکتاپ بدون غیرفعال‌کردن والپیپر Spotlight؛ مخفی یا نمایش با یک کلیک.",
        GITHUB + "/Win-Spotlight-Icon-Toggle", [
            Action("HIDE ICON", "reg", "SPOT_HIDE"),
            Action("SHOW ICON", "reg", "SPOT_SHOW"),
            Action("RESTART EXPLORER", "cmd",
                   args="taskkill /F /IM explorer.exe & timeout /t 1 >nul & start explorer.exe"),
        ]),
    Module("DRV-BACKUP", "OEM Driver Backup", "DRIVERS",
        "DISM + PnPUtil, zero dependencies",
        "Export every third-party OEM driver to a vault, and reinstall them in bulk later. The lifesaver you run before reinstalling Windows.",
        "بکاپ کامل درایورهای OEM با DISM و نصب گروهی آن‌ها هنگام بازیابی؛ نجات‌دهنده قبل از تعویض ویندوز، بدون هیچ وابستگی.",
        GITHUB + "/Win-Drv-Backup", [
            Action("BACKUP ALL OEM", "script", "DRVBACKUP", True),
            Action("RESTORE DRIVERS", "script", "DRVRESTORE", True),
            Action("VIEW VAULT", "vault", path="%SystemDrive%\\Backup_Driver"),
        ]),
    Module("DISP-BACKUP", "Display Driver Backup", "DRIVERS",
        "Get-WindowsDriver + PnPUtil export",
        "Surgical backup/restore of GPU display-class drivers only. Filters the Display class GUID and exports matching oem*.inf packages.",
        "بکاپ و بازیابی تخصصی درایور گرافیک (فقط کلاس Display) با فیلتر GUID و خروجی PnPUtil؛ سریع و تمیز.",
        GITHUB + "/Win-Display-Drv-Backup", [
            Action("BACKUP DISPLAY", "script", "DISPBACKUP", True),
            Action("RESTORE DISPLAY", "script", "DISPRESTORE", True),
            Action("VIEW VAULT", "vault", path="%SystemDrive%\\Backup_Display_Driver"),
        ]),
    Module("USB-SHIELD", "USB Immunizer", "USB",
        "decoy files + hidden/system attributes",
        "Immunize a USB stick against auto-created junk (Android, System Volume Information) using hidden decoy files, and brand it with a custom icon + label. Pick the drive root first.",
        "ایمن‌سازی فلش USB در برابر پوشه‌های زائد خودکار با فایل‌طعمه Hidden/System و برندسازی آیکون و لیبل درایو؛ ابتدا ریشه درایو را انتخاب کن.",
        GITHUB + "/USB-Immunizer-Customizer", [
            Action("IMMUNIZE TARGET", "script", "USB_TOOL", True, True, True),
        ]),
    Module("DNS-RESET", "DNS + Proxy Reset", "NET",
        "NetAdapter reset + proxy off + flushdns",
        'Reset DNS to automatic (DHCP) on all adapters, disable system proxy (HKCU+HKLM), and flush the resolver cache. First aid for "connected but nothing loads".',
        "ریست DNS به حالت خودکار (DHCP)، غیرفعال‌سازی پروکسی سیستم و Flush کش DNS؛ کمک‌های اولیه برای «وصلم ولی هیچی باز نمی‌شود».",
        GITHUB + "/Reset-DNS-Proxy", [
            Action("RESET DNS+PROXY", "script", "DNSRESET", True),
        ]),
    Module("MEDIA-RENAME", "Image + Video Renamer", "FILES",
        "recursive batch rename, collision-safe",
        "Bulk-rename 50+ image formats to .jpg and 40+ video formats to .mp4, recursively. Name clashes get auto (1), (2) suffixes - nothing is ever overwritten or deleted.",
        "تغییرنام گروهی بازگشتی: ده‌ها فرمت عکس به jpg. و ویدیو به mp4.؛ تداخل نام با پسوند خودکار حل می‌شود و هیچ فایلی بازنویسی یا حذف نمی‌شود.",
        GITHUB + "/Image-Video-Renamer", [
            Action("IMAGES -> .JPG", "script", "IMGREN", False, True),
            Action("VIDEOS -> .MP4", "script", "VIDREN", False, True),
        ]),
    Module("TREE-EXPORT", "Directory Tree Exporter", "AUDIT",
        "batch + PowerShell, UTF-8 report",
        "Map a folder into a visual tree report with sizes and creation/modification dates. Wide UTF-8 table, self-excluding log, stats summary included.",
        "تولید گزارش درختی دایرکتوری با حجم و تاریخ ساخت/تغییر در فایل UTF-8؛ مناسب مستندسازی پروژه و آرشیو.",
        GITHUB + "/Directory-Tree-Exporter", [
            Action("EXPORT TREE", "script", "TREE", False, True),
        ]),
    Module("SHA256-AUDIT", "SHA-256 Tree Auditor", "AUDIT",
        "Get-FileHash per file, tamper evidence",
        "Everything Tree Exporter does, plus a SHA-256 checksum for every file. Prove integrity, detect corruption or tampering. Locked files are tagged, never fatal.",
        "ممیزی دقیق: درخت دایرکتوری + متادیتا + هش SHA-256 تک‌تک فایل‌ها برای اثبات یکپارچگی و تشخیص دستکاری یا خرابی.",
        GITHUB + "/Directory-SHA256-Tree-Exporter", [
            Action("RUN SHA-256 AUDIT", "script", "SHA256", False, True),
        ]),
    Module("UNPACK", "Subfolder Unpacker", "FILES",
        "deep recursive move-to-parent",
        "Flatten chaos: move every file from all nested subfolders straight into the parent folder. Perfect cleanup after extracting archives or multi-folder downloads.",
        "صاف‌کردن پوشه‌ها: انتقال همه فایل‌ها از ساب‌فولدرهای تودرتو به پوشه اصلی؛ عالی برای تمیزکاری بعد از اکسترکت آرشیوها.",
        GITHUB + "/Unpack-Subfolders", [
            Action("UNPACK TO PARENT", "script", "UNPACK", False, True),
        ]),
]

STR = {
    "subtitle": {"en": "Made for Windows 10 and 11",
                 "fa": "برای ویندوز ۱۰ و ۱۱ مناسب است"},
    "modules": {"en": "MODULES", "fa": "ماژول‌ها"},
    "open_project": {"en": "OPEN PROJECT", "fa": "باز کردن پروژه"},
    "readme2fa": {"en": "READ IN PERSIAN", "fa": "خواندن به فارسی"},
    "readme2en": {"en": "READ IN ENGLISH", "fa": "خواندن به انگلیسی"},
    "target": {"en": "TARGET FOLDER:", "fa": "پوشه هدف:"},
    "browse": {"en": "BROWSE...", "fa": "انتخاب..."},
    "notarget": {"en": "(no target selected)", "fa": "(هدفی انتخاب نشده)"},
    "console": {"en": "LIVE LOG", "fa": "لاگ زنده"},
    "export": {"en": "EXPORT", "fa": "اکسپورت"},
    "clear": {"en": "CLEAR", "fa": "پاک‌سازی"},
    "stop": {"en": "STOP", "fa": "توقف"},
    "github": {"en": "GitHub", "fa": "گیت‌هاب"},
    "lang": {"en": "فارسی", "fa": "EN"},


    "st_module": {"en": "module", "fa": "ماژول"},
    "st_of": {"en": "of", "fa": "از"},
    "st_target": {"en": "target", "fa": "هدف"},
    "vault_title": {"en": "VAULT INSPECTOR", "fa": "بازرس صندوق"},
    "vault_copy": {"en": "COPY PATH", "fa": "کپی مسیر"},
    "vault_refresh": {"en": "REFRESH", "fa": "به‌روزرسانی"},
    "vault_close": {"en": "CLOSE", "fa": "بستن"},
    "confirm_title": {"en": "CONFIRM ACTION", "fa": "تأیید عملیات"},
    "yes": {"en": "YES, RUN IT", "fa": "بله، اجرا کن"},
    "no": {"en": "CANCEL", "fa": "انصراف"},
}

# Persian tech one-liners (module meta line), keyed by module id
TECH_FA = {
    "NCSI-FIX": "تغییر رجیستری + ری‌استارت NlaSvc",
    "USER-BACKUP": "Robocopy + خواندن مسیر از رجیستری",
    "SPOTLIGHT": "تغییر رجیستری HKCU",
    "DRV-BACKUP": "DISM و PnPUtil، بدون وابستگی",
    "DISP-BACKUP": "Get-WindowsDriver و خروجی PnPUtil",
    "USB-SHIELD": "فایل طعمه + اتریبیوت مخفی و سیستمی",
    "DNS-RESET": "ریست آداپتور + قطع پروکسی + flushdns",
    "MEDIA-RENAME": "تغییرنام بازگشتی، ضد تداخل",
    "TREE-EXPORT": "بچ + PowerShell، گزارش UTF-8",
    "SHA256-AUDIT": "هش SHA-256 تک‌تک فایل‌ها",
    "UNPACK": "انتقال بازگشتی به پوشه والد",
}

# Persian action labels, keyed by the English label
ACT_FA = {
    "DISABLE PROBING": "غیرفعال‌سازی پروب",
    "ENABLE PROBING": "فعال‌سازی پروب",
    "RESTART NLA SVC": "ری‌استارت سرویس NLA",
    "BACKUP NOW": "شروع بکاپ",
    "RESTORE (MERGE)": "بازیابی (ادغام)",
    "VIEW VAULT": "مشاهده صندوق",
    "HIDE ICON": "مخفی‌کردن آیکون",
    "SHOW ICON": "نمایش آیکون",
    "RESTART EXPLORER": "ری‌استارت اکسپلورر",
    "BACKUP ALL OEM": "بکاپ همه OEM",
    "RESTORE DRIVERS": "بازیابی درایورها",
    "BACKUP DISPLAY": "بکاپ گرافیک",
    "RESTORE DISPLAY": "بازیابی گرافیک",
    "IMMUNIZE TARGET": "ایمن‌سازی هدف",
    "RESET DNS+PROXY": "ریست DNS و پروکسی",
    "IMAGES -> .JPG": "عکس‌ها به JPG",
    "VIDEOS -> .MP4": "ویدیوها به MP4",
    "EXPORT TREE": "خروجی درخت",
    "RUN SHA-256 AUDIT": "اجرای ممیزی SHA-256",
    "UNPACK TO PARENT": "انتقال به پوشه اصلی",
}

CONFIRM_TEXTS = {
    "restore": {
        "en": "Merge missing files from C:\\User Backup back into your profile?\nExisting files are NEVER overwritten or deleted.",
        "fa": "فایل‌های گمشده از C:\\User Backup به پروفایل برگردانده شود؟\nفایل‌های موجود هرگز بازنویسی یا حذف نمی‌شوند.",
    },
}

# ---------------------------------------------------------------- readmes (in-app, EN default + FA toggle)
# Full README.md + README.FA.md from each GitHub repo (fetched 2026-09-22).
# Only the top HTML/badge header block is stripped for in-app readability.
READMES = {
    'NCSI-FIX': {
        "en": '# Windows NCSI & Internet Probing Manager\n\nA lightweight Windows utility consisting of Registry tweaks and a self-elevating Batch script designed to manage the **Network Connectivity Status Indicator (NCSI)** Active Probing feature and restart the Network Location Awareness (`NlaSvc`) service.\n\nIt resolves common Windows issues such as false "No Internet Access" alerts (globe icon or yellow exclamation mark when the internet is actually working), eliminates unexpected captive-portal browser popups, and provides privacy control over periodic Microsoft network probing requests.\n\n---\n\n## 📁 Repository Contents\n\n| File | Type | Description |\n| :--- | :--- | :--- |\n| **`Restart Network Service.bat`** | Batch Script | Automatically requests Administrator rights and restarts the `NlaSvc` service (and dependencies) to apply changes immediately. |\n| **`Enable Internet Probing.reg`** | Registry File | Sets `EnableActiveProbing = 1` to restore the default Windows network connectivity checks. |\n| **`Disable Internet Probing.reg`** | Registry File | Sets `EnableActiveProbing = 0` to stop Windows from polling `msftconnecttest.com`. |\n\n---\n\n## ✨ Features\n\n- **🔑 Automatic Elevation (UAC):** The batch file detects privilege levels and automatically requests Administrator access via PowerShell.\n- **⚡ Instant Effect Without Reboot:** Restarts `NlaSvc` with dependent services forced (`/y`), refreshing the system tray network indicator in seconds without restarting the computer.\n- **🌐 Fixes False "No Internet" Icon:** Resolves cases where browsers and apps can connect to websites, but Windows incorrectly reports "No Internet, secured".\n- **🛡️ Privacy & Telemetry Management:** Disables recurring HTTP polling to Microsoft servers (`msftconnecttest.com` and `ipv6.msftconnecttest.com`).\n- **📦 Clean & Native:** 100% native Windows files with zero external dependencies.\n\n---\n\n## 🚀 How to Use\n\n### Step 1: Choose Your Desired Configuration\n- To **disable** internet probing (fix false captive portals / stop telemetry):  \n  Double-click **`Disable Internet Probing.reg`** and click **Yes** to merge.\n- To **restore default** internet probing:  \n  Double-click **`Enable Internet Probing.reg`** and click **Yes** to merge.\n\n### Step 2: Apply Changes\n- Double-click **`Restart Network Service.bat`**.\n- Accept the **UAC** prompt when prompted.\n- The script will stop and restart the network service. The network tray icon will refresh automatically within 5 seconds.\n\n---\n\n## 💻 System Requirements\n\n- **OS:** Windows 7, Windows 8.1, Windows 10, or Windows 11.\n- **Permissions:** Administrator access (handled automatically by the batch script).\n\n---\n\n## ⚖️ Absolute Legal Disclaimer, Waiver & Limitation of Liability\n\nThis project is licensed under the **Apache License, Version 2.0**. This disclaimer expressly supplements, expands, and reinforces **Section 7 (Disclaimer of Warranty)** and **Section 8 (Limitation of Liability)** of the Apache License 2.0, and shall control to the maximum extent permitted by applicable law.\n\n**FOR EDUCATIONAL, RESEARCH, AND INFORMATIONAL PURPOSES ONLY. NO COMMERCIAL WARRANTY OR LIABILITY IS ASSUMED.**\n\n### 1. Complete Disclaimer of All Warranties\nTo the maximum extent permitted by applicable law, the Software (including all code, documentation, data, and related materials) is provided strictly on an **"AS IS"** and **"AS AVAILABLE"** basis, without any warranties or conditions of any kind, whether express, implied, statutory, customary, or otherwise. This includes, without limitation, any warranties of merchantability, fitness for a particular purpose, non-infringement, title, security, accuracy, completeness, uninterrupted or error-free operation, or freedom from viruses or other harmful components. The author(s), copyright holder(s), maintainer(s), and contributor(s) expressly disclaim all such warranties.\n\n### 2. Absolute Limitation of Liability\nUnder no circumstances and under no legal theory (whether in contract, tort — including negligence, gross negligence, and willful misconduct — strict liability, product liability, or otherwise) shall the author(s), maintainer(s), contributor(s), or copyright holder(s) be liable for any damages whatsoever, including but not limited to direct, indirect, incidental, special, consequential, exemplary, punitive, or any other damages (including loss of data, profits, revenue, business interruption, system failure, hardware damage, security breaches, personal injury, or any other loss), arising out of or related to the use, inability to use, modification, distribution, or reliance upon the Software, even if advised of the possibility of such damages and even if any remedy fails of its essential purpose.\n\n### 3. Assumption of All Risk & User Responsibility\nAny use, cloning, modification, deployment, distribution, or reliance upon this Software is undertaken entirely at the user’s sole risk and discretion. The user is exclusively and solely responsible for:\n- Ensuring full compliance with all applicable local, national, and international laws, regulations, export controls, and third-party terms;\n- Evaluating the suitability, security, and legality of the Software for any purpose;\n- Any consequences arising from its use or misuse.\n\nNothing in this repository constitutes legal, financial, cybersecurity, medical, architectural, or any other form of professional advice.\n\n### 4. Broad Indemnification\nBy accessing, downloading, cloning, forking, viewing, compiling, distributing, or using any part of this repository, you irrevocably agree to indemnify, defend, and hold harmless the author(s), contributor(s), and copyright holder(s) from and against any and all claims, demands, actions, proceedings, liabilities, damages, losses, costs, and expenses (including reasonable attorneys’ fees and legal costs) arising out of or related to your access, use, misuse, modification, distribution, or violation of this disclaimer or any applicable law.\n\n### 5. Severability & Maximum Enforceability\nIf any provision of this disclaimer is held to be unenforceable or invalid under applicable law, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed. The remaining provisions shall continue in full force and effect. This disclaimer shall be interpreted to provide the maximum protection permitted by law.\n\n### 6. No Waiver of Non-Waivable Rights\nNothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.\n',
        "fa": '# ابزار مدیریت NCSI و پروبینگ شبکه ویندوز\n\nیک جعبه\u200cابزار سبک و کاربردی برای ویندوز شامل فایل\u200cهای رجیستری و بچ\u200cاسکریپت خودکار جهت مدیریت قابلیت **Active Probing** در سرویس تشخیص وضعیت اتصال شبکه (**NCSI**) و راه\u200cاندازی مجدد سریع سرویس `NlaSvc`.\n\nاین ابزار برای حل مشکل آزاردهنده «نمایش آیکون کره زمین یا علامت تعجب زرد و پیام No Internet Access با وجود وصل بودن اینترنت»، جلوگیری از باز شدن خودکار مرورگر (صفحات لاگین یا Captive Portal) و کنترل پایش\u200cهای تلمتری مایکروسافت طراحی شده است.\n\n---\n\n## 📁 فایل\u200cهای موجود در پروژه\n\n| نام فایل | فرمت | عملکرد |\n| :--- | :--- | :--- |\n| **`Restart Network Service.bat`** | بچ\u200cاسکریپت | ارتقای خودکار به دسترسی ادمین و ری\u200cاستارت سریع سرویس `NlaSvc` جهت اعمال فوری تنظیمات. |\n| **`Enable Internet Probing.reg`** | فایل رجیستری | مقداردهی `EnableActiveProbing = 1` برای بازگرداندن سیستم بررسی پیش\u200cفرض ویندوز. |\n| **`Disable Internet Probing.reg`** | فایل رجیستری | مقداردهی `EnableActiveProbing = 0` برای توقف پایش مداوم و ارسال درخواست به سرورهای مایکروسافت. |\n\n---\n\n## ✨ قابلیت\u200cها و ویژگی\u200cها\n\n* 🔑 **ارتقای خودکار دسترسی ادمین:** اسکریپت سطح دسترسی را بررسی کرده و در صورت نیاز پیام تأیید UAC را از طریق پاورشل به صورت خودکار باز می\u200cکند.\n* ⚡ **اعمال تغییرات بدون ری\u200cاستارت سیستم:** ری\u200cاستارت تمیز سرویس `NlaSvc` به همراه سرویس\u200cهای وابسته (`/y`) که وضعیت آیکون شبکه را ظرف چند ثانیه بدون خاموش و روشن کردن کامپیوتر به\u200cروزرسانی می\u200cکند.\n* 🌐 **حل خطای کاذب قطع اینترنت:** رفع مشکل عدم نمایش وضعیت واقعی اتصال در تسک\u200cبار هنگامی که سایت\u200cها باز می\u200cشوند اما ویندوز وضعیت را بدون اینترنت نشان می\u200cدهد.\n* 🛡️ **کنترل تلمتری و حریم خصوصی:** جلوگیری از ارسال مداوم پینگ و درخواست\u200cهای HTTP پس\u200cزمینه به آدرس\u200cهای مایکروسافت (`msftconnecttest.com`).\n* 📦 **کاملاً بومی:** بدون نیاز به نصب هیچ ابزار خارجی؛ متکی به تنظیمات پیش\u200cفرض ویندوز.\n\n---\n\n## 🚀 راهنمای استفاده\n\n### مرحله ۱: انتخاب وضعیت مورد نظر\n* برای **غیرفعال\u200cسازی** پایش اینترنت (حل خطای کاذب یا قطع درخواست\u200cهای اضافه):  \n  روی فایل **`Disable Internet Probing.reg`** دو بار کلیک کرده و پیام تأیید را Yes بزنید.\n* برای **فعال\u200cسازی مجدد** به حالت پیش\u200cفرض ویندوز:  \n  روی فایل **`Enable Internet Probing.reg`** دو بار کلیک کرده و پیام تأیید را Yes بزنید.\n\n### مرحله ۲: اعمال فوری تنظیمات\n* روی فایل **`Restart Network Service.bat`** دو بار کلیک کنید.\n* در صورت نمایش پنجره دسترسی **UAC**، گزینه **Yes** را انتخاب کنید.\n* سرویس شبکه متوقف و مجدداً اجرا می\u200cشود و آیکون شبکه در تسک\u200cبار پس از ۵ ثانیه رفرش خواهد شد.\n\n---\n\n## 💻 پیش\u200cنیازهای سیستم\n\n* **سیستم\u200cعامل:** ویندوز 7، 8.1، 10 یا 11.\n* **سطح دسترسی:** ادمین (اسکریپت به طور خودکار آن را درخواست می\u200cکند).\n\n---\n\n## ⚖️ سلب مسئولیت مطلق قانونی، اسقاط حق و محدودیت کامل مسئولیت\n\nاین پروژه تحت مجوز **Apache License, Version 2.0** منتشر شده است. مفاد این بخش به\u200cطور صریح در راستای تقویت، گسترش و تأکید بر **بند ۷ (سلب هرگونه ضمانت)** و **بند ۸ (محدودیت کامل مسئولیت)** لایسنس Apache 2.0 تدوین شده و تا حداکثر میزان مجاز توسط قوانین حاکم، حاکم خواهد بود.\n\n**صرفاً جهت مقاصد آموزشی، پژوهشی و اطلاع\u200cرسانی. هیچ\u200cگونه ضمانت یا مسئولیت تجاری پذیرفته نمی\u200cشود.**\n\n### ۱. سلب کامل تمام ضمانت\u200cها\nبر اساس حداکثر حدود مجاز در قوانین حاکم، نرم\u200cافزار (شامل تمام کدها، مستندات، داده\u200cها و مواد مرتبط) دقیقاً بر مبنای اصل **«همان\u200cگونه که هست» (AS IS)** و **«به\u200cشرط وجود» (AS AVAILABLE)** و بدون هیچ\u200cگونه ضمانت یا شرطی (اعم از صریح، ضمنی، قانونی، عرفی یا غیره) ارائه می\u200cشود. این شامل و نه\u200cمحدود به ضمانت قابلیت فروش تجاری، تناسب برای مقصد خاص، عدم نقض حقوق ثالث، امنیت، دقت، کامل بودن، کارکرد بدون وقفه یا بدون خطا، و عاری بودن از ویروس یا اجزای مضر است. پدیدآورنده، دارندگان حق\u200cتألیف، نگهدارندگان و مشارکت\u200cکنندگان صریحاً تمام این ضمانت\u200cها را از خود سلب می\u200cنمایند.\n\n### ۲. محدودیت مطلق مسئولیت\nتحت هیچ شرایطی و بر پایهٔ هیچ نظریهٔ حقوقی (اعم از مسئولیت قراردادی، مسئولیت مدنی یا شبه\u200cجرم — شامل قصور عادی، قصور فاحش و رفتار عمدی — مسئولیت محض، مسئولیت محصول یا غیره) پدیدآورنده، نگهدارندگان، مشارکت\u200cکنندگان یا دارندگان حق\u200cتألیف در قبال هیچ\u200cگونه خسارتی (شامل خسارات مستقیم، غیرمستقیم، اتفاقی، تبعی، خاص، تنبیهی، جزایی یا هر نوع خسارت دیگر از جمله از دست رفتن داده، سود، درآمد، وقفه در کسب\u200cوکار، خرابی سیستم، آسیب سخت\u200cافزاری، رخنه امنیتی، صدمه جانی یا هر زیان دیگر) ناشی از استفاده، عدم توانایی در استفاده، تغییر، توزیع یا اتکا به نرم\u200cافزار پاسخگو نخواهند بود؛ حتی اگر از امکان وقوع چنین خساراتی مطلع شده باشند و حتی اگر هرگونه جبران خسارت از هدف اساسی خود بازبماند.\n\n### ۳. پذیرش کامل ریسک و مسئولیت انحصاری کاربر\nهرگونه استفاده، کلون، تغییر، استقرار، توزیع یا اتکا به این نرم\u200cافزار تماماً با صلاحدید و ریسک انحصاری کاربر انجام می\u200cگیرد. کاربر به\u200cطور انحصاری و کامل مسئول است برای:\n- اطمینان از انطباق کامل با کلیه قوانین و مقررات محلی، ملی و بین\u200cالمللی، کنترل\u200cهای صادراتی و شرایط اشخاص ثالث؛\n- ارزیابی مناسب بودن، امنیت و قانونی بودن نرم\u200cافزار برای هر منظوری؛\n- تمام پیامدهای ناشی از استفاده یا سوءاستفاده از آن.\n\nهیچ بخشی از این مخزن در حکم مشاوره حقوقی، مالی، سایبری، پزشکی، معماری یا هر نوع مشاوره تخصصی دیگر محسوب نمی\u200cشود.\n\n### ۴. تعهد گسترده به جبران خسارت و مصون\u200cسازی\nهر شخص یا نهادی با دسترسی، دانلود، کلون، فورک، مشاهده، کامپایل، توزیع یا استفاده از هر بخشی از این مخزن، به\u200cطور قطعی و غیرقابل بازگشت متعهد می\u200cگردد که پدیدآورنده، مشارکت\u200cکنندگان و دارندگان حق\u200cتألیف را در برابر هرگونه ادعا، درخواست، دعوی، مسئولیت، خسارت، زیان، هزینه و مخارج (شامل حق\u200cالوکاله معقول و هزینه\u200cهای دادرسی) ناشی از دسترسی، استفاده، سوءاستفاده، تغییر، توزیع یا نقض این سلب مسئولیت یا هر قانون حاکم، کاملاً مصون نگاه داشته و کلیه خسارات را جبران نماید.\n\n### ۵. قابلیت تفکیک و حداکثر قابلیت اجرا\nاگر هر یک از مفاد این سلب مسئولیت بر اساس قوانین حاکم غیرقابل اجرا یا باطل تشخیص داده شود، آن مفاد باید به حداقل میزان لازم برای قابل اجرا شدن اصلاح شود، یا در صورت عدم امکان اصلاح، حذف گردد. سایر مفاد به قوت کامل خود باقی می\u200cمانند. این سلب مسئولیت باید به گونه\u200cای تفسیر شود که حداکثر حمایت مجاز توسط قانون را فراهم آورد.\n\n### ۶. عدم اسقاط حقوق غیرقابل اسقاط\nهیچ بخشی از این سلب مسئولیت به\u200cمنظور حذف یا محدود کردن مسئولیتی که بر اساس قوانین اجباری حاکم قابل حذف یا محدود کردن نیست (از جمله مسئولیت ناشی از مرگ یا صدمه جانی ناشی از قصور در حوزه\u200cهایی که چنین محدودیتی ممنوع است) نوشته نشده است. در چنین مواردی، مسئولیت تا حداکثر میزان مجاز توسط قانون محدود می\u200cشود.\n',
    },
    'USER-BACKUP': {
        "en": '# Windows User Folders Backup & Restore Utility\n\nA fast, lightweight, and automated pair of Windows batch scripts. **`Backup.bat`** safely copies your essential user folders (Desktop, Downloads, Documents, Pictures, Music, and Videos) to `C:\\User Backup` using the high-performance **Robocopy** engine, and **`Restore.bat`** merges them back into your profile without overwriting or deleting anything.\n\nUnlike naive backup scripts that rely solely on hardcoded paths, this tool dynamically queries the Windows Registry (`User Shell Folders`) to detect custom folder locations, redirected drives, and Microsoft OneDrive synchronizations.\n\n---\n\n## ✨ Features\n\n### 📥 Backup.bat\n\n- **🔑 Automatic Elevation (UAC):** Relaunches itself as Administrator through PowerShell (`RunAs`) when needed. A guard flag prevents endless relaunch loops if elevation fails.\n- **🧠 Dynamic Registry Resolution:** Reads `HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders` to find the real folder paths. Value names containing spaces (`My Music`, `My Pictures`, `My Video`) are parsed correctly, and `%USERPROFILE%`-style variables are expanded.\n- **☁️ Smart Fallback Chain:** Registry path → standard profile folder → OneDrive sync folders (`%OneDrive%`, `%OneDriveConsumer%`, `%OneDriveCommercial%`, `%USERPROFILE%\\OneDrive`).\n- **⚡ Robust Robocopy Engine:** Uses `/E /COPY:DAT /DCOPY:DAT` to preserve files, directory structures, attributes, and timestamps. Re-runs only copy new or changed files.\n- **🛡️ Recursion & Junction Safety:** Excludes junction points (`/XJ`) and the backup folder itself (`/XD "C:\\User Backup"`).\n- **⏳ Low-Latency Retries:** `/R:1 /W:1` skips stubborn, locked files instead of freezing the backup.\n- **🚫 Zero Log Files:** No `.log` file is ever created and all Robocopy output is silenced. Any existing `*.log` files in the top level of `C:\\User Backup` are purged at launch (subfolders are never touched, so log files you backed up from your own folders stay safe).\n- **🎨 Clean, Flicker-Free Console:** Cyan theme, boxed header, and one live status line per folder with dot padding.\n- **⏱️ Non-Freezing Countdown:** A 10-second inline countdown (`10..1`) that ends instantly on any keypress and keeps running even in elevated or redirected consoles.\n\n### 📤 Restore.bat\n\n- **✅ Confirmation Prompt:** Nothing happens until you press `Y`. Pressing `N` cancels.\n- **🧩 Non-Destructive Merge:** Restores only files that are missing from your profile. Existing files are never overwritten and nothing is ever deleted (`/XC /XN /XO`, no `/MIR` or `/PURGE`).\n- **🎯 Smart Destinations:** Uses the same registry → profile → OneDrive resolution, so files land in the folders Windows actually uses. If a folder does not exist yet, it is created.\n- **⏭️ Graceful Skipping:** Folders that are not present in the backup are marked `SKIP`.\n- **🔒 Backup Stays Untouched:** `C:\\User Backup` is only read, never modified.\n- **🎨 Same Look & Feel:** Identical header, status lines, and countdown as `Backup.bat`.\n\n---\n\n## 📂 Backed-Up Folders\n\n| Folder        | Backup Location            | Registry Value Name                      |\n| ------------- | -------------------------- | ---------------------------------------- |\n| **Desktop**   | `C:\\User Backup\\Desktop`   | `Desktop`                                |\n| **Downloads** | `C:\\User Backup\\Downloads` | `{374DE290-123F-4565-9164-39C4925E467B}` |\n| **Documents** | `C:\\User Backup\\Documents` | `Personal`                               |\n| **Music**     | `C:\\User Backup\\Music`     | `My Music`                               |\n| **Pictures**  | `C:\\User Backup\\Pictures`  | `My Pictures`                            |\n| **Videos**    | `C:\\User Backup\\Videos`    | `My Video`                               |\n\n---\n\n## 🚀 How to Use\n\n### Backup\n\n1. Download `Backup.bat` (and `Restore.bat`) and save them anywhere, for example on your Desktop.\n2. **Double-click** `Backup.bat`.\n3. Confirm the **UAC** prompt when asked for Administrator permissions.\n4. Watch the live status of each folder. All data is copied to **`C:\\User Backup`**.\n5. The window closes after 10 seconds, or immediately when you press any key.\n\n### Restore\n\n1. If you are on a fresh Windows install or another PC, first copy your backup so that it is located at **`C:\\User Backup`**.\n2. **Double-click** `Restore.bat` and confirm the **UAC** prompt.\n3. Press **`Y`** to confirm the restore (or `N` to cancel).\n4. Missing files are merged back into your profile folders. The window closes after 10 seconds, or on any keypress.\n\n---\n\n## 🖥️ Console Preview\n\n```text\n+============================================================+\n|                    USER PROFILE BACKUP                     |\n+============================================================+\n\nTarget Path  : C:\\User Backup\nUser Profile : C:\\Users\\YourName\n\n[+] Desktop ....................................... [  DONE  ]\n[+] Downloads ..................................... [  DONE  ]\n[+] Documents ..................................... [  DONE  ]\n[+] Music ......................................... [  DONE  ]\n[+] Pictures ...................................... [  DONE  ]\n[+] Videos ........................................ [  SKIP  ]\n\nBackup completed successfully.\n\nClosing in  7 s ...  press any key to exit\n```\n\n| Status       | Meaning                                                                                 |\n| ------------ | --------------------------------------------------------------------------------------- |\n| `[  DONE  ]` | The folder was processed successfully.                                                  |\n| `[  SKIP  ]` | The source folder (Backup) or the backed-up folder (Restore) was not found.             |\n| `[ FAILED ]` | Robocopy reported an error (for example, files that stayed locked after the retry).     |\n\n---\n\n## ⚙️ Customization\n\n- **Change the backup location:** Edit the `BackupRoot` line near the top of **both** scripts (`set "BackupRoot=C:\\User Backup"`).\n- **Let newer backup files replace older ones on restore:** In `Restore.bat`, replace `/XC /XN /XO` with `/XO`. Existing files that are newer than the backup are still preserved.\n- **Also purge logs recursively:** In `Backup.bat`, add `/s` to the `del` command on the log-purge line. Note that this also deletes `.log` files that belong to your backed-up data.\n\n---\n\n## ⚠️ Notes & Limitations\n\n- The backup lives on your system drive by default. To protect against disk failure, copy `C:\\User Backup` to an external drive or cloud storage as well.\n- Backups are additive: files that you delete from your profile later are **not** removed from `C:\\User Backup`.\n- If OneDrive Files On-Demand is enabled, online-only files may be downloaded while they are copied.\n- Run the scripts from your own administrator account. If UAC elevates through a different account, `%USERPROFILE%` and the registry hive refer to that account instead.\n- Only the six standard folders are covered. `AppData`, browser profiles, and installed programs are not included.\n\n---\n\n## 💻 System Requirements\n\n- **OS:** Windows 7, Windows 8.1, Windows 10, or Windows 11.\n- **PowerShell:** Required for automatic UAC elevation and the countdown timer.\n- **Permissions:** Administrator access (requested automatically).\n\n---\n\n## ⚖️ Absolute Legal Disclaimer, Waiver & Limitation of Liability\n\nThis project is licensed under the **Apache License, Version 2.0**. This disclaimer expressly supplements, expands, and reinforces **Section 7 (Disclaimer of Warranty)** and **Section 8 (Limitation of Liability)** of the Apache License 2.0, and shall control to the maximum extent permitted by applicable law.\n\n**FOR EDUCATIONAL, RESEARCH, AND INFORMATIONAL PURPOSES ONLY. NO COMMERCIAL WARRANTY OR LIABILITY IS ASSUMED.**\n\n### 1. Complete Disclaimer of All Warranties\nTo the maximum extent permitted by applicable law, the Software (including all code, documentation, data, and related materials) is provided strictly on an **"AS IS"** and **"AS AVAILABLE"** basis, without any warranties or conditions of any kind, whether express, implied, statutory, customary, or otherwise. This includes, without limitation, any warranties of merchantability, fitness for a particular purpose, non-infringement, title, security, accuracy, completeness, uninterrupted or error-free operation, or freedom from viruses or other harmful components. The author(s), copyright holder(s), maintainer(s), and contributor(s) expressly disclaim all such warranties.\n\n### 2. Absolute Limitation of Liability\nUnder no circumstances and under no legal theory (whether in contract, tort — including negligence, gross negligence, and willful misconduct — strict liability, product liability, or otherwise) shall the author(s), maintainer(s), contributor(s), or copyright holder(s) be liable for any damages whatsoever, including but not limited to direct, indirect, incidental, special, consequential, exemplary, punitive, or any other damages (including loss of data, profits, revenue, business interruption, system failure, hardware damage, security breaches, personal injury, or any other loss), arising out of or related to the use, inability to use, modification, distribution, or reliance upon the Software, even if advised of the possibility of such damages and even if any remedy fails of its essential purpose.\n\n### 3. Assumption of All Risk & User Responsibility\nAny use, cloning, modification, deployment, distribution, or reliance upon this Software is undertaken entirely at the user’s sole risk and discretion. The user is exclusively and solely responsible for:\n- Ensuring full compliance with all applicable local, national, and international laws, regulations, export controls, and third-party terms;\n- Evaluating the suitability, security, and legality of the Software for any purpose;\n- Any consequences arising from its use or misuse.\n\nNothing in this repository constitutes legal, financial, cybersecurity, medical, architectural, or any other form of professional advice.\n\n### 4. Broad Indemnification\nBy accessing, downloading, cloning, forking, viewing, compiling, distributing, or using any part of this repository, you irrevocably agree to indemnify, defend, and hold harmless the author(s), contributor(s), and copyright holder(s) from and against any and all claims, demands, actions, proceedings, liabilities, damages, losses, costs, and expenses (including reasonable attorneys’ fees and legal costs) arising out of or related to your access, use, misuse, modification, distribution, or violation of this disclaimer or any applicable law.\n\n### 5. Severability & Maximum Enforceability\nIf any provision of this disclaimer is held to be unenforceable or invalid under applicable law, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed. The remaining provisions shall continue in full force and effect. This disclaimer shall be interpreted to provide the maximum protection permitted by law.\n\n### 6. No Waiver of Non-Waivable Rights\nNothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.\n',
        "fa": '# ابزار پشتیبان\u200cگیری و بازیابی پوشه\u200cهای کاربری ویندوز\n\nمجموعه\u200cای سریع، سبک و خودکار از دو اسکریپت Batch برای ویندوز. فایل **`Backup.bat`** پوشه\u200cهای اصلی کاربر (Desktop، Downloads، Documents، Pictures، Music و Videos) را با موتور پرسرعت **Robocopy** در مسیر `C:\\User Backup` پشتیبان\u200cگیری می\u200cکند و فایل **`Restore.bat`** آن\u200cها را بدون بازنویسی یا حذف هیچ فایلی به پروفایل شما برمی\u200cگرداند.\n\nبرخلاف اسکریپت\u200cهای ساده\u200cای که فقط به مسیرهای ثابت تکیه می\u200cکنند، این ابزار مسیر واقعی پوشه\u200cها را به\u200cصورت پویا از رجیستری ویندوز (`User Shell Folders`) می\u200cخواند تا پوشه\u200cهای جابه\u200cجا\u200cشده، درایوهای تغییرمسیر\u200cداده\u200cشده و پوشه\u200cهای همگام\u200cشده با Microsoft OneDrive را نیز تشخیص دهد.\n\n---\n\n## ✨ ویژگی\u200cها\n\n### 📥 Backup.bat\n\n- **🔑 ارتقای خودکار دسترسی (UAC):** در صورت نیاز، اسکریپت خودش را از طریق PowerShell (با `RunAs`) با دسترسی Administrator دوباره اجرا می\u200cکند. یک پرچم محافظ هم از ایجاد حلقه\u200cی بی\u200cپایان در صورت ناموفق بودن ارتقا جلوگیری می\u200cکند.\n- **🧠 تشخیص پویا از رجیستری:** مسیر واقعی پوشه\u200cها را از `HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders` می\u200cخواند. نام مقدارهایی که فاصله دارند (`My Music`، `My Pictures` و `My Video`) درست پردازش می\u200cشوند و متغیرهایی مثل `%USERPROFILE%` به مسیر کامل تبدیل می\u200cشوند.\n- **☁️ زنجیره\u200cی جایگزین هوشمند:** مسیر رجیستری ← پوشه\u200cی استاندارد پروفایل ← پوشه\u200cهای همگام\u200cشده\u200cی OneDrive (`%OneDrive%`، `%OneDriveConsumer%`، `%OneDriveCommercial%` و `%USERPROFILE%\\OneDrive`).\n- **⚡ موتور قدرتمند Robocopy:** با پرچم\u200cهای `/E /COPY:DAT /DCOPY:DAT` فایل\u200cها، ساختار پوشه\u200cها، ویژگی\u200cها (Attributes) و زمان\u200cها حفظ می\u200cشوند. در اجراهای بعدی فقط فایل\u200cهای جدید یا تغییرکرده کپی می\u200cشوند.\n- **🛡️ ایمنی در برابر حلقه و Junction:** نقاط اتصال (`/XJ`) و خود پوشه\u200cی پشتیبان (`/XD "C:\\User Backup"`) از کپی مستثنا می\u200cشوند.\n- **⏳ تلاش مجدد سریع:** با `/R:1 /W:1` فایل\u200cهای قفل\u200cشده به\u200cجای گیر انداختن پشتیبان\u200cگیری، رد می\u200cشوند.\n- **🚫 بدون هیچ فایل لاگ:** هیچ فایل `.log` ساخته نمی\u200cشود و خروجی Robocopy کاملاً بی\u200cصدا است. هر فایل `*.log` موجود در سطح اصلی `C:\\User Backup` هنگام شروع پاک می\u200cشود (زیرپوشه\u200cها دست\u200cنخورده می\u200cمانند؛ پس فایل\u200cهای لاگ خودتان که در پشتیبان قرار دارند حذف نمی\u200cشوند).\n- **🎨 کنسول تمیز و بدون سوسو:** تم فیروزه\u200cای، سرآیند قاب\u200cدار و یک خط وضعیت زنده با نقطه\u200cچین برای هر پوشه.\n- **⏱️ شمارش معکوس بدون قفل شدن:** شمارش معکوس ۱۰ ثانیه\u200cای (`10..1`) در همان یک خط، که با فشردن هر کلید بلافاصله تمام می\u200cشود و در کنسول\u200cهای Elevated یا Redirect شده هم متوقف نمی\u200cشود.\n\n### 📤 Restore.bat\n\n- **✅ پرسش تأیید:** تا وقتی `Y` نزنید هیچ اتفاقی نمی\u200cافتد. با `N` عملیات لغو می\u200cشود.\n- **🧩 ادغام غیرتخریبی:** فقط فایل\u200cهایی که در پروفایل شما وجود ندارند بازگردانی می\u200cشوند. هیچ فایل موجودی بازنویسی یا حذف نمی\u200cشود (`/XC /XN /XO` و بدون `/MIR` یا `/PURGE`).\n- **🎯 مقصد هوشمند:** از همان روش رجیستری ← پروفایل ← OneDrive استفاده می\u200cکند تا فایل\u200cها در پوشه\u200cهایی که ویندوز واقعاً به کار می\u200cبرد قرار بگیرند. اگر پوشه\u200cای هنوز وجود نداشته باشد، ساخته می\u200cشود.\n- **⏭️ عبور امن از موارد ناموجود:** پوشه\u200cهایی که در پشتیبان نیستند با وضعیت `SKIP` رد می\u200cشوند.\n- **🔒 پشتیبان دست\u200cنخورده:** `C:\\User Backup` فقط خوانده می\u200cشود و هرگز تغییر نمی\u200cکند.\n- **🎨 ظاهر یکسان:** سرآیند، خط\u200cهای وضعیت و شمارش معکوس دقیقاً مثل `Backup.bat` است.\n\n---\n\n## 📂 پوشه\u200cهای پشتیبان\u200cگیری\u200cشده\n\n| پوشه          | محل ذخیره در پشتیبان       | نام مقدار در رجیستری                     |\n| ------------- | -------------------------- | ---------------------------------------- |\n| **Desktop**   | `C:\\User Backup\\Desktop`   | `Desktop`                                |\n| **Downloads** | `C:\\User Backup\\Downloads` | `{374DE290-123F-4565-9164-39C4925E467B}` |\n| **Documents** | `C:\\User Backup\\Documents` | `Personal`                               |\n| **Music**     | `C:\\User Backup\\Music`     | `My Music`                               |\n| **Pictures**  | `C:\\User Backup\\Pictures`  | `My Pictures`                            |\n| **Videos**    | `C:\\User Backup\\Videos`    | `My Video`                               |\n\n---\n\n## 🚀 نحوه\u200cی استفاده\n\n### پشتیبان\u200cگیری (Backup)\n\n1. فایل\u200cهای `Backup.bat` و `Restore.bat` را دانلود کنید و در هر جایی که می\u200cخواهید (مثلاً Desktop) ذخیره کنید.\n2. روی `Backup.bat` **دوبار کلیک** کنید.\n3. در پنجره\u200cی **UAC** درخواست دسترسی Administrator را تأیید کنید.\n4. وضعیت زنده\u200cی هر پوشه را ببینید. همه\u200cی اطلاعات در **`C:\\User Backup`** کپی می\u200cشود.\n5. پنجره پس از ۱۰ ثانیه یا با فشردن هر کلید بسته می\u200cشود.\n\n### بازیابی (Restore)\n\n1. اگر ویندوز را تازه نصب کرده\u200cاید یا روی رایانه\u200cی دیگری کار می\u200cکنید، ابتدا پشتیبان را طوری کپی کنید که در مسیر **`C:\\User Backup`** قرار بگیرد.\n2. روی `Restore.bat` **دوبار کلیک** کنید و پنجره\u200cی **UAC** را تأیید کنید.\n3. برای تأیید بازیابی کلید **`Y`** را بزنید (یا با `N` لغو کنید).\n4. فایل\u200cهای ناموجود به پوشه\u200cهای پروفایل شما اضافه می\u200cشوند. پنجره پس از ۱۰ ثانیه یا با فشردن هر کلید بسته می\u200cشود.\n\n---\n\n## 🖥️ پیش\u200cنمایش کنسول\n\n```text\n+============================================================+\n|                    USER PROFILE BACKUP                     |\n+============================================================+\n\nTarget Path  : C:\\User Backup\nUser Profile : C:\\Users\\YourName\n\n[+] Desktop ....................................... [  DONE  ]\n[+] Downloads ..................................... [  DONE  ]\n[+] Documents ..................................... [  DONE  ]\n[+] Music ......................................... [  DONE  ]\n[+] Pictures ...................................... [  DONE  ]\n[+] Videos ........................................ [  SKIP  ]\n\nBackup completed successfully.\n\nClosing in  7 s ...  press any key to exit\n```\n\n| وضعیت        | معنی                                                                                     |\n| ------------ | ---------------------------------------------------------------------------------------- |\n| `[  DONE  ]` | پوشه با موفقیت پردازش شد.                                                                |\n| `[  SKIP  ]` | پوشه\u200cی مبدأ (در Backup) یا پوشه\u200cی موجود در پشتیبان (در Restore) پیدا نشد.                |\n| `[ FAILED ]` | Robocopy خطا گزارش کرد (مثلاً فایل\u200cهایی که پس از تلاش مجدد هنوز قفل بودند).              |\n\n---\n\n## ⚙️ شخصی\u200cسازی\n\n- **تغییر محل پشتیبان:** خط `BackupRoot` را در بخش بالای **هر دو** اسکریپت ویرایش کنید (`set "BackupRoot=C:\\User Backup"`).\n- **جایگزینی فایل\u200cهای قدیمی\u200cتر با نسخه\u200cی جدیدتر پشتیبان هنگام بازیابی:** در `Restore.bat` عبارت `/XC /XN /XO` را با `/XO` عوض کنید. فایل\u200cهای موجودی که از پشتیبان جدیدتر باشند همچنان حفظ می\u200cشوند.\n- **پاک\u200cسازی بازگشتی لاگ\u200cها:** در `Backup.bat` به فرمان `del` در خط پاک\u200cسازی لاگ، گزینه\u200cی `/s` را اضافه کنید. توجه کنید که این کار فایل\u200cهای `.log` مربوط به داده\u200cهای پشتیبان\u200cگیری\u200cشده\u200cی شما را هم پاک می\u200cکند.\n\n---\n\n## ⚠️ نکات و محدودیت\u200cها\n\n- پشتیبان به\u200cطور پیش\u200cفرض روی درایو سیستم ذخیره می\u200cشود. برای محافظت در برابر خرابی دیسک، پوشه\u200cی `C:\\User Backup` را روی هارد اکسترنال یا فضای ابری هم کپی کنید.\n- پشتیبان\u200cگیری افزایشی است: فایل\u200cهایی که بعداً از پروفایل خود حذف می\u200cکنید، از `C:\\User Backup` **پاک نمی\u200cشوند**.\n- اگر قابلیت Files On-Demand در OneDrive فعال باشد، فایل\u200cهای «فقط آنلاین» ممکن است هنگام کپی شدن دانلود شوند.\n- اسکریپت\u200cها را با حساب مدیر (Administrator) خودتان اجرا کنید. اگر UAC از طریق حساب دیگری ارتقا بدهد، `%USERPROFILE%` و رجیستری به همان حساب اشاره می\u200cکنند.\n- فقط شش پوشه\u200cی استاندارد پوشش داده می\u200cشود. `AppData`، پروفایل مرورگرها و برنامه\u200cهای نصب\u200cشده جزو پشتیبان نیستند.\n\n---\n\n## 💻 پیش\u200cنیازهای سیستم\n\n- **سیستم\u200cعامل:** Windows 7، Windows 8.1، Windows 10 یا Windows 11.\n- **PowerShell:** برای ارتقای خودکار UAC و شمارش معکوس لازم است.\n- **دسترسی:** دسترسی Administrator (به\u200cصورت خودکار درخواست می\u200cشود).\n\n---\n\n## ⚖️ سلب مسئولیت مطلق قانونی، اسقاط حق و محدودیت کامل مسئولیت\n\nاین پروژه تحت مجوز **Apache License, Version 2.0** منتشر شده است. مفاد این بخش به\u200cطور صریح در راستای تقویت، گسترش و تأکید بر **بند ۷ (سلب هرگونه ضمانت)** و **بند ۸ (محدودیت کامل مسئولیت)** لایسنس Apache 2.0 تدوین شده و تا حداکثر میزان مجاز توسط قوانین حاکم، حاکم خواهد بود.\n\n**صرفاً جهت مقاصد آموزشی، پژوهشی و اطلاع\u200cرسانی. هیچ\u200cگونه ضمانت یا مسئولیت تجاری پذیرفته نمی\u200cشود.**\n\n### ۱. سلب کامل تمام ضمانت\u200cها\nبر اساس حداکثر حدود مجاز در قوانین حاکم، نرم\u200cافزار (شامل تمام کدها، مستندات، داده\u200cها و مواد مرتبط) دقیقاً بر مبنای اصل **«همان\u200cگونه که هست» (AS IS)** و **«به\u200cشرط وجود» (AS AVAILABLE)** و بدون هیچ\u200cگونه ضمانت یا شرطی (اعم از صریح، ضمنی، قانونی، عرفی یا غیره) ارائه می\u200cشود. این شامل و نه\u200cمحدود به ضمانت قابلیت فروش تجاری، تناسب برای مقصد خاص، عدم نقض حقوق ثالث، امنیت، دقت، کامل بودن، کارکرد بدون وقفه یا بدون خطا، و عاری بودن از ویروس یا اجزای مضر است. پدیدآورنده، دارندگان حق\u200cتألیف، نگهدارندگان و مشارکت\u200cکنندگان صریحاً تمام این ضمانت\u200cها را از خود سلب می\u200cنمایند.\n\n### ۲. محدودیت مطلق مسئولیت\nتحت هیچ شرایطی و بر پایهٔ هیچ نظریهٔ حقوقی (اعم از مسئولیت قراردادی، مسئولیت مدنی یا شبه\u200cجرم — شامل قصور عادی، قصور فاحش و رفتار عمدی — مسئولیت محض، مسئولیت محصول یا غیره) پدیدآورنده، نگهدارندگان، مشارکت\u200cکنندگان یا دارندگان حق\u200cتألیف در قبال هیچ\u200cگونه خسارتی (شامل خسارات مستقیم، غیرمستقیم، اتفاقی، تبعی، خاص، تنبیهی، جزایی یا هر نوع خسارت دیگر از جمله از دست رفتن داده، سود، درآمد، وقفه در کسب\u200cوکار، خرابی سیستم، آسیب سخت\u200cافزاری، رخنه امنیتی، صدمه جانی یا هر زیان دیگر) ناشی از استفاده، عدم توانایی در استفاده، تغییر، توزیع یا اتکا به نرم\u200cافزار پاسخگو نخواهند بود؛ حتی اگر از امکان وقوع چنین خساراتی مطلع شده باشند و حتی اگر هرگونه جبران خسارت از هدف اساسی خود بازبماند.\n\n### ۳. پذیرش کامل ریسک و مسئولیت انحصاری کاربر\nهرگونه استفاده، کلون، تغییر، استقرار، توزیع یا اتکا به این نرم\u200cافزار تماماً با صلاحدید و ریسک انحصاری کاربر انجام می\u200cگیرد. کاربر به\u200cطور انحصاری و کامل مسئول است برای:\n- اطمینان از انطباق کامل با کلیه قوانین و مقررات محلی، ملی و بین\u200cالمللی، کنترل\u200cهای صادراتی و شرایط اشخاص ثالث؛\n- ارزیابی مناسب بودن، امنیت و قانونی بودن نرم\u200cافزار برای هر منظوری؛\n- تمام پیامدهای ناشی از استفاده یا سوءاستفاده از آن.\n\nهیچ بخشی از این مخزن در حکم مشاوره حقوقی، مالی، سایبری، پزشکی، معماری یا هر نوع مشاوره تخصصی دیگر محسوب نمی\u200cشود.\n\n### ۴. تعهد گسترده به جبران خسارت و مصون\u200cسازی\nهر شخص یا نهادی با دسترسی، دانلود، کلون، فورک، مشاهده، کامپایل، توزیع یا استفاده از هر بخشی از این مخزن، به\u200cطور قطعی و غیرقابل بازگشت متعهد می\u200cگردد که پدیدآورنده، مشارکت\u200cکنندگان و دارندگان حق\u200cتألیف را در برابر هرگونه ادعا، درخواست، دعوی، مسئولیت، خسارت، زیان، هزینه و مخارج (شامل حق\u200cالوکاله معقول و هزینه\u200cهای دادرسی) ناشی از دسترسی، استفاده، سوءاستفاده، تغییر، توزیع یا نقض این سلب مسئولیت یا هر قانون حاکم، کاملاً مصون نگاه داشته و کلیه خسارات را جبران نماید.\n\n### ۵. قابلیت تفکیک و حداکثر قابلیت اجرا\nاگر هر یک از مفاد این سلب مسئولیت بر اساس قوانین حاکم غیرقابل اجرا یا باطل تشخیص داده شود، آن مفاد باید به حداقل میزان لازم برای قابل اجرا شدن اصلاح شود، یا در صورت عدم امکان اصلاح، حذف گردد. سایر مفاد به قوت کامل خود باقی می\u200cمانند. این سلب مسئولیت باید به گونه\u200cای تفسیر شود که حداکثر حمایت مجاز توسط قانون را فراهم آورد.\n\n### ۶. عدم اسقاط حقوق غیرقابل اسقاط\nهیچ بخشی از این سلب مسئولیت به\u200cمنظور حذف یا محدود کردن مسئولیتی که بر اساس قوانین اجباری حاکم قابل حذف یا محدود کردن نیست (از جمله مسئولیت ناشی از مرگ یا صدمه جانی ناشی از قصور در حوزه\u200cهایی که چنین محدودیتی ممنوع است) نوشته نشده است. در چنین مواردی، مسئولیت تا حداکثر میزان مجاز توسط قانون محدود می\u200cشود.\n',
    },
    'SPOTLIGHT': {
        "en": '# Hide or Show "Learn about this picture" Desktop Icon\n\nWindows Spotlight automatically delivers high-quality daily wallpapers to your desktop. However, modern Windows 10 and Windows 11 updates force an unmovable **"Learn about this picture"** icon directly onto the desktop.\n\nThis repository provides simple, one-click Windows Registry (`.reg`) files to remove or restore this icon while keeping dynamic Windows Spotlight wallpapers fully functioning.\n\n---\n\n## 📁 Repository Contents\n\n| File | Registry Value | Action |\n| :--- | :--- | :--- |\n| **`Hide Learn about this picture.reg`** | `dword:00000001` | Hides the icon from the desktop. |\n| **`Show Learn about this picture.reg`** | `dword:00000000` | Restores the icon to default visibility. |\n\n---\n\n## ✨ Features\n\n- **🖼️ Keeps Spotlight Wallpapers Active:** Only the unnecessary desktop shortcut icon is hidden; your daily rotating wallpapers remain completely untouched.\n- **⚡ Instant & Native:** Uses native Windows Registry settings (`HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\HideDesktopIcons\\NewStartPanel`).\n- **🚫 Zero Background Processes:** No third-party software, utilities, or background scripts required.\n- **🔄 Fully Reversible:** Easily restore the icon at any time using the companion `.reg` file.\n- **👤 Per-User Scope:** Targets `HKEY_CURRENT_USER`, meaning it doesn\'t modify system-wide files or break system integrity.\n\n---\n\n## 🚀 How to Use\n\n1. Clone or download this repository.\n2. Choose your desired action:\n   - To **hide** the icon: Double-click **`Hide Learn about this picture.reg`**.\n   - To **show** the icon: Double-click **`Show Learn about this picture.reg`**.\n3. Click **Yes** when prompted by the Windows Registry Editor confirmation dialog.\n4. Right-click on an empty spot on your desktop and select **Refresh** (or press **F5**) to apply the changes immediately.\n\n---\n\n## 💻 System Requirements\n\n- **OS:** Windows 10 or Windows 11 (with Windows Spotlight enabled).\n\n---\n\n## ⚖️ Absolute Legal Disclaimer, Waiver & Limitation of Liability\n\nThis project is licensed under the **Apache License, Version 2.0**. This disclaimer expressly supplements, expands, and reinforces **Section 7 (Disclaimer of Warranty)** and **Section 8 (Limitation of Liability)** of the Apache License 2.0, and shall control to the maximum extent permitted by applicable law.\n\n**FOR EDUCATIONAL, RESEARCH, AND INFORMATIONAL PURPOSES ONLY. NO COMMERCIAL WARRANTY OR LIABILITY IS ASSUMED.**\n\n### 1. Complete Disclaimer of All Warranties\nTo the maximum extent permitted by applicable law, the Software (including all code, documentation, data, and related materials) is provided strictly on an **"AS IS"** and **"AS AVAILABLE"** basis, without any warranties or conditions of any kind, whether express, implied, statutory, customary, or otherwise. This includes, without limitation, any warranties of merchantability, fitness for a particular purpose, non-infringement, title, security, accuracy, completeness, uninterrupted or error-free operation, or freedom from viruses or other harmful components. The author(s), copyright holder(s), maintainer(s), and contributor(s) expressly disclaim all such warranties.\n\n### 2. Absolute Limitation of Liability\nUnder no circumstances and under no legal theory (whether in contract, tort — including negligence, gross negligence, and willful misconduct — strict liability, product liability, or otherwise) shall the author(s), maintainer(s), contributor(s), or copyright holder(s) be liable for any damages whatsoever, including but not limited to direct, indirect, incidental, special, consequential, exemplary, punitive, or any other damages (including loss of data, profits, revenue, business interruption, system failure, hardware damage, security breaches, personal injury, or any other loss), arising out of or related to the use, inability to use, modification, distribution, or reliance upon the Software, even if advised of the possibility of such damages and even if any remedy fails of its essential purpose.\n\n### 3. Assumption of All Risk & User Responsibility\nAny use, cloning, modification, deployment, distribution, or reliance upon this Software is undertaken entirely at the user’s sole risk and discretion. The user is exclusively and solely responsible for:\n- Ensuring full compliance with all applicable local, national, and international laws, regulations, export controls, and third-party terms;\n- Evaluating the suitability, security, and legality of the Software for any purpose;\n- Any consequences arising from its use or misuse.\n\nNothing in this repository constitutes legal, financial, cybersecurity, medical, architectural, or any other form of professional advice.\n\n### 4. Broad Indemnification\nBy accessing, downloading, cloning, forking, viewing, compiling, distributing, or using any part of this repository, you irrevocably agree to indemnify, defend, and hold harmless the author(s), contributor(s), and copyright holder(s) from and against any and all claims, demands, actions, proceedings, liabilities, damages, losses, costs, and expenses (including reasonable attorneys’ fees and legal costs) arising out of or related to your access, use, misuse, modification, distribution, or violation of this disclaimer or any applicable law.\n\n### 5. Severability & Maximum Enforceability\nIf any provision of this disclaimer is held to be unenforceable or invalid under applicable law, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed. The remaining provisions shall continue in full force and effect. This disclaimer shall be interpreted to provide the maximum protection permitted by law.\n\n### 6. No Waiver of Non-Waivable Rights\nNothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.\n',
        "fa": '# مخفی\u200cسازی و نمایش آیکون Learn about this picture در دسکتاپ ویندوز\n\nقابلیت Windows Spotlight تصاویر و والپیپرهای باکیفیت و متغیری را روزانه روی پس\u200cزمینه دسکتاپ قرار می\u200cدهد. با این حال، در آپدیت\u200cهای جدید ویندوز ۱۰ و ۱۱ یک آیکون دائمی به نام **"Learn about this picture"** به دسکتاپ اضافه می\u200cشود که نمی\u200cتوان آن را به روش معمولی حذف کرد.\n\nاین پروژه شامل دو فایل رجیستری ساده (`.reg`) است که به شما امکان می\u200cدهد این آیکون مزاحم را تنها با یک کلیک مخفی کنید، بدون اینکه والپیپرهای پویای ویندوز غیرفعال شوند.\n\n---\n\n## 📁 فایل\u200cهای موجود در پروژه\n\n| نام فایل | مقدار در رجیستری | عملکرد |\n| :--- | :--- | :--- |\n| **`Hide Learn about this picture.reg`** | `dword:00000001` | مخفی کردن آیکون از روی دسکتاپ. |\n| **`Show Learn about this picture.reg`** | `dword:00000000` | بازگرداندن و نمایش مجدد آیکون روی دسکتاپ. |\n\n---\n\n## ✨ قابلیت\u200cها و ویژگی\u200cها\n\n* 🖼️ **حفظ والپیپرهای پویا:** تنها آیکون اضافی از روی دسکتاپ برداشته می\u200cشود و چرخش روزانه تصاویر Spotlight دست\u200cنخورده باقی می\u200cماند.\n* ⚡ **اعمال سریع و بومی:** استفاده مستقیم از کلید رسمی رجیستری ویندوز بدون ایجاد اختلال در سیستم.\n* 🚫 **بدون نرم\u200cافزار جانبی:** بدون نیاز به نصب هرگونه برنامه اضافی یا مصرف حافظه رم در پس\u200cزمینه.\n* 🔄 **کاملاً برگشت\u200cپذیر:** هر زمان که اراده کنید می\u200cتوانید با فایل دیگر، آیکون را به حالت اول بازگردانید.\n* 👤 **محدوده سطح کاربر:** تغییرات درون شاخه `HKEY_CURRENT_USER` اعمال می\u200cشوند و ساختار کلی ویندوز دستکاری نمی\u200cشود.\n\n---\n\n## 🚀 راهنمای استفاده\n\n1. فایل\u200cهای مخزن را دانلود کنید.\n2. بسته به نیاز خود:\n   * برای **مخفی کردن** آیکون: روی فایل **`Hide Learn about this picture.reg`** دو بار کلیک کنید.\n   * برای **نمایش مجدد** آیکون: روی فایل **`Show Learn about this picture.reg`** دو بار کلیک کنید.\n3. در پنجره بازشده، پیام تأیید ویرایشگر رجیستری را با زدن **Yes** تأیید کنید.\n4. روی فضای خالی دسکتاپ راست\u200cکلیک کرده و گزینه **Refresh** را بزنید (یا کلید **F5** کیبورد را بفشارید) تا آیکون بلافاصله مخفی/نمایان شود.\n\n---\n\n## 💻 پیش\u200cنیازهای سیستم\n\n* **سیستم\u200cعامل:** ویندوز 10 یا ویندوز 11 (با قابلیت فعال بودن Windows Spotlight).\n\n---\n\n## ⚖️ سلب مسئولیت مطلق قانونی، اسقاط حق و محدودیت کامل مسئولیت\n\nاین پروژه تحت مجوز **Apache License, Version 2.0** منتشر شده است. مفاد این بخش به\u200cطور صریح در راستای تقویت، گسترش و تأکید بر **بند ۷ (سلب هرگونه ضمانت)** و **بند ۸ (محدودیت کامل مسئولیت)** لایسنس Apache 2.0 تدوین شده و تا حداکثر میزان مجاز توسط قوانین حاکم، حاکم خواهد بود.\n\n**صرفاً جهت مقاصد آموزشی، پژوهشی و اطلاع\u200cرسانی. هیچ\u200cگونه ضمانت یا مسئولیت تجاری پذیرفته نمی\u200cشود.**\n\n### ۱. سلب کامل تمام ضمانت\u200cها\nبر اساس حداکثر حدود مجاز در قوانین حاکم، نرم\u200cافزار (شامل تمام کدها، مستندات، داده\u200cها و مواد مرتبط) دقیقاً بر مبنای اصل **«همان\u200cگونه که هست» (AS IS)** و **«به\u200cشرط وجود» (AS AVAILABLE)** و بدون هیچ\u200cگونه ضمانت یا شرطی (اعم از صریح، ضمنی، قانونی، عرفی یا غیره) ارائه می\u200cشود. این شامل و نه\u200cمحدود به ضمانت قابلیت فروش تجاری، تناسب برای مقصد خاص، عدم نقض حقوق ثالث، امنیت، دقت، کامل بودن، کارکرد بدون وقفه یا بدون خطا، و عاری بودن از ویروس یا اجزای مضر است. پدیدآورنده، دارندگان حق\u200cتألیف، نگهدارندگان و مشارکت\u200cکنندگان صریحاً تمام این ضمانت\u200cها را از خود سلب می\u200cنمایند.\n\n### ۲. محدودیت مطلق مسئولیت\nتحت هیچ شرایطی و بر پایهٔ هیچ نظریهٔ حقوقی (اعم از مسئولیت قراردادی، مسئولیت مدنی یا شبه\u200cجرم — شامل قصور عادی، قصور فاحش و رفتار عمدی — مسئولیت محض، مسئولیت محصول یا غیره) پدیدآورنده، نگهدارندگان، مشارکت\u200cکنندگان یا دارندگان حق\u200cتألیف در قبال هیچ\u200cگونه خسارتی (شامل خسارات مستقیم، غیرمستقیم، اتفاقی، تبعی، خاص، تنبیهی، جزایی یا هر نوع خسارت دیگر از جمله از دست رفتن داده، سود، درآمد، وقفه در کسب\u200cوکار، خرابی سیستم، آسیب سخت\u200cافزاری، رخنه امنیتی، صدمه جانی یا هر زیان دیگر) ناشی از استفاده، عدم توانایی در استفاده، تغییر، توزیع یا اتکا به نرم\u200cافزار پاسخگو نخواهند بود؛ حتی اگر از امکان وقوع چنین خساراتی مطلع شده باشند و حتی اگر هرگونه جبران خسارت از هدف اساسی خود بازبماند.\n\n### ۳. پذیرش کامل ریسک و مسئولیت انحصاری کاربر\nهرگونه استفاده، کلون، تغییر، استقرار، توزیع یا اتکا به این نرم\u200cافزار تماماً با صلاحدید و ریسک انحصاری کاربر انجام می\u200cگیرد. کاربر به\u200cطور انحصاری و کامل مسئول است برای:\n- اطمینان از انطباق کامل با کلیه قوانین و مقررات محلی، ملی و بین\u200cالمللی، کنترل\u200cهای صادراتی و شرایط اشخاص ثالث؛\n- ارزیابی مناسب بودن، امنیت و قانونی بودن نرم\u200cافزار برای هر منظوری؛\n- تمام پیامدهای ناشی از استفاده یا سوءاستفاده از آن.\n\nهیچ بخشی از این مخزن در حکم مشاوره حقوقی، مالی، سایبری، پزشکی، معماری یا هر نوع مشاوره تخصصی دیگر محسوب نمی\u200cشود.\n\n### ۴. تعهد گسترده به جبران خسارت و مصون\u200cسازی\nهر شخص یا نهادی با دسترسی، دانلود، کلون، فورک، مشاهده، کامپایل، توزیع یا استفاده از هر بخشی از این مخزن، به\u200cطور قطعی و غیرقابل بازگشت متعهد می\u200cگردد که پدیدآورنده، مشارکت\u200cکنندگان و دارندگان حق\u200cتألیف را در برابر هرگونه ادعا، درخواست، دعوی، مسئولیت، خسارت، زیان، هزینه و مخارج (شامل حق\u200cالوکاله معقول و هزینه\u200cهای دادرسی) ناشی از دسترسی، استفاده، سوءاستفاده، تغییر، توزیع یا نقض این سلب مسئولیت یا هر قانون حاکم، کاملاً مصون نگاه داشته و کلیه خسارات را جبران نماید.\n\n### ۵. قابلیت تفکیک و حداکثر قابلیت اجرا\nاگر هر یک از مفاد این سلب مسئولیت بر اساس قوانین حاکم غیرقابل اجرا یا باطل تشخیص داده شود، آن مفاد باید به حداقل میزان لازم برای قابل اجرا شدن اصلاح شود، یا در صورت عدم امکان اصلاح، حذف گردد. سایر مفاد به قوت کامل خود باقی می\u200cمانند. این سلب مسئولیت باید به گونه\u200cای تفسیر شود که حداکثر حمایت مجاز توسط قانون را فراهم آورد.\n\n### ۶. عدم اسقاط حقوق غیرقابل اسقاط\nهیچ بخشی از این سلب مسئولیت به\u200cمنظور حذف یا محدود کردن مسئولیتی که بر اساس قوانین اجباری حاکم قابل حذف یا محدود کردن نیست (از جمله مسئولیت ناشی از مرگ یا صدمه جانی ناشی از قصور در حوزه\u200cهایی که چنین محدودیتی ممنوع است) نوشته نشده است. در چنین مواردی، مسئولیت تا حداکثر میزان مجاز توسط قانون محدود می\u200cشود.\n',
    },
    'DRV-BACKUP': {
        "en": '# Windows Driver Backup & Restore Utility\n\nA lightweight, automated Windows batch utility designed to back up and restore OEM drivers using native command-line tools (**DISM** and **PnPUtil**).\n\nZero third-party software required — 100% native, clean, and reliable.\n\n---\n\n## ✨ Features\n\n- **🛠️ 100% Native:** Relies exclusively on built-in Windows utilities (`DISM` and `PnPUtil`).\n- **🔑 Auto-Elevation:** Automatically requests administrative privileges via UAC if not launched as Administrator.\n- **📦 OEM Driver Isolation:** Backs up only installed third-party drivers, ignoring standard inbox Windows drivers to save disk space.\n- **🔄 Batch Restoration:** Recursively installs and restores all drivers from subdirectories in a single operation.\n- **🎨 Clean Terminal Output:** Formatted CLI interface with explicit status tags (`[INFO]`, `[SUCCESS]`, `[ERROR]`).\n- **🛡️ Safe & Robust:** Built-in path validation, directory existence checks, and dynamic variable handling.\n\n---\n\n## 📋 System Requirements\n\n- **Operating System:** Windows 8.1 / Windows 10 / Windows 11 (32-bit & 64-bit).\n- **Permissions:** Administrator privileges (handled automatically).\n- **PowerShell:** Required for automatic UAC elevation.\n\n---\n\n## 🚀 How to Use\n\n### 1. Back Up Drivers\n1. Run **`Backup-Drivers.bat`**.\n2. Accept the UAC prompt if prompted.\n3. The script will automatically export all OEM drivers into `C:\\Backup_Driver`.\n\n### 2. Restore Drivers\n1. Ensure the driver backup directory is located at `C:\\Backup_Driver`.\n2. Run **`Restore-Drivers.bat`**.\n3. Accept the UAC prompt if prompted.\n4. The script will recursively scan and install all `.inf` driver packages.\n5. **Reboot your system** after the restoration is complete.\n\n---\n\n## ⚙️ Configuration\n\nBy default, drivers are backed up to and restored from:\n\nC:\\Backup_Driver\n\n---\n\n## ⚖️ Absolute Legal Disclaimer, Waiver & Limitation of Liability\n\nThis project is licensed under the **Apache License, Version 2.0**. This disclaimer expressly supplements, expands, and reinforces **Section 7 (Disclaimer of Warranty)** and **Section 8 (Limitation of Liability)** of the Apache License 2.0, and shall control to the maximum extent permitted by applicable law.\n\n**FOR EDUCATIONAL, RESEARCH, AND INFORMATIONAL PURPOSES ONLY. NO COMMERCIAL WARRANTY OR LIABILITY IS ASSUMED.**\n\n### 1. Complete Disclaimer of All Warranties\nTo the maximum extent permitted by applicable law, the Software (including all code, documentation, data, and related materials) is provided strictly on an **"AS IS"** and **"AS AVAILABLE"** basis, without any warranties or conditions of any kind, whether express, implied, statutory, customary, or otherwise. This includes, without limitation, any warranties of merchantability, fitness for a particular purpose, non-infringement, title, security, accuracy, completeness, uninterrupted or error-free operation, or freedom from viruses or other harmful components. The author(s), copyright holder(s), maintainer(s), and contributor(s) expressly disclaim all such warranties.\n\n### 2. Absolute Limitation of Liability\nUnder no circumstances and under no legal theory (whether in contract, tort — including negligence, gross negligence, and willful misconduct — strict liability, product liability, or otherwise) shall the author(s), maintainer(s), contributor(s), or copyright holder(s) be liable for any damages whatsoever, including but not limited to direct, indirect, incidental, special, consequential, exemplary, punitive, or any other damages (including loss of data, profits, revenue, business interruption, system failure, hardware damage, security breaches, personal injury, or any other loss), arising out of or related to the use, inability to use, modification, distribution, or reliance upon the Software, even if advised of the possibility of such damages and even if any remedy fails of its essential purpose.\n\n### 3. Assumption of All Risk & User Responsibility\nAny use, cloning, modification, deployment, distribution, or reliance upon this Software is undertaken entirely at the user’s sole risk and discretion. The user is exclusively and solely responsible for:\n- Ensuring full compliance with all applicable local, national, and international laws, regulations, export controls, and third-party terms;\n- Evaluating the suitability, security, and legality of the Software for any purpose;\n- Any consequences arising from its use or misuse.\n\nNothing in this repository constitutes legal, financial, cybersecurity, medical, architectural, or any other form of professional advice.\n\n### 4. Broad Indemnification\nBy accessing, downloading, cloning, forking, viewing, compiling, distributing, or using any part of this repository, you irrevocably agree to indemnify, defend, and hold harmless the author(s), contributor(s), and copyright holder(s) from and against any and all claims, demands, actions, proceedings, liabilities, damages, losses, costs, and expenses (including reasonable attorneys’ fees and legal costs) arising out of or related to your access, use, misuse, modification, distribution, or violation of this disclaimer or any applicable law.\n\n### 5. Severability & Maximum Enforceability\nIf any provision of this disclaimer is held to be unenforceable or invalid under applicable law, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed. The remaining provisions shall continue in full force and effect. This disclaimer shall be interpreted to provide the maximum protection permitted by law.\n\n### 6. No Waiver of Non-Waivable Rights\nNothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.\n',
        "fa": '# ابزار پشتیبان\u200cگیری و بازیابی درایورهای ویندوز (Windows Driver Backup & Restore Utility)\n\nابزاری سبک، خودکار و بر پایه بچ\u200cاسکریپت (Batch Script) برای تهیه نسخه پشتیبان و بازیابی درایورهای OEM در سیستم\u200cعامل\u200cهای ویندوز با استفاده از ابزارهای بومی خط فرمان (**DISM** و **PnPUtil**).\n\nبدون نیاز به نصب هیچ\u200cگونه نرم\u200cافزار جانبی — ۱۰۰٪ بومی (Native)، امن و سبک.\n\n---\n\n## ✨ قابلیت\u200cها و ویژگی\u200cها\n\n* 🛠️ **۱۰۰٪ بومی و مستقل:** استفاده مستقیم از ابزارهای داخلی ویندوز (`DISM` و `PnPUtil`) بدون وابستگی خارجی.\n* 🔑 **ارتقای خودکار دسترسی (Auto-Elevation):** در صورت اجرا نشدن به صورت Administrator، پیام UAC را برای دریافت دسترسی مدیریتی به صورت خودکار باز می\u200cکند.\n* 📦 **خروجی اختصاصی درایورهای OEM:** فقط درایورهای سخت\u200cافزاری نصب\u200cشده (شخص ثالث) را بکاپ می\u200cگیرد و درایورهای پیش\u200cفرض ویندوز را نادیده می\u200cگیرد تا حجم بکاپ بیهوده سنگین نشود.\n* 🔄 **بازیابی دسته\u200cای و خودکار:** تمامی زیرپوشه\u200cها را اسکن کرده و تمام درایورها را به صورت بازگشتی (Recursive) نصب می\u200cکند.\n* 🎨 **محیط خط فرمان زیبا و شفاف:** دارای برچسب\u200cهای تفکیک\u200cشده وضعیتی (`[INFO]`، `[SUCCESS]`، `[ERROR]`).\n* 🛡️ **ایمن و مطمئن:** شامل اعتبارسنجی مسیر، بررسی وجود دایرکتوری و مدیریت داینامیک متغیرها.\n\n---\n\n## 📋 پیش\u200cنیازهای سیستم\n\n* **سیستم\u200cعامل:** ویندوز 8.1، ویندوز 10 یا ویندوز 11 (نسخه\u200cهای ۳۲ بیتی و ۶۴ بیتی).\n* **سطح دسترسی:** دسترسی Administrator (اسکریپت این کار را به صورت خودکار انجام می\u200cدهد).\n* **پاورشل (PowerShell):** برای بالا بردن خودکار دسترسی (UAC Elevation) در سیستم فعال باشد.\n\n---\n\n## 🚀 راهنمای استفاده\n\n### ۱. تهیه نسخه پشتیبان از درایورها (Backup)\n\n1. روی فایل **`Backup-Drivers.bat`** دو بار کلیک کنید.\n2. در صورت نمایش پنجره UAC، دسترسی ادمین را تأیید کنید.\n3. اسکریپت پوشه\u200cای در مسیر `C:\\Backup_Driver` ساخته و تمام درایورهای OEM را درون آن ذخیره می\u200cکند.\n\n### ۲. بازیابی درایورها (Restore)\n\n1. مطمئن شوید پوشه بکاپ در مسیر `C:\\Backup_Driver` قرار دارد.\n2. روی فایل **`Restore-Drivers.bat`** دو بار کلیک کنید.\n3. دسترسی UAC را در صورت درخواست تأیید کنید.\n4. اسکریپت تمام فایل\u200cهای `.inf` را اسکن کرده و در سیستم نصب می\u200cکند.\n5. پس از پایان عملیات، **سیستم خود را یک بار ری\u200cاستارت کنید**.\n\n---\n\n## ⚙️ شخصی\u200cسازی مسیر پیش\u200cفرض\n\nبه طور پیش\u200cفرض، عملیات پشتیبان\u200cگیری و بازیابی در این مسیر انجام می\u200cشود:\n\nC:\\Backup_Driver\n\n---\n\n## ⚖️ سلب مسئولیت مطلق قانونی، اسقاط حق و محدودیت کامل مسئولیت\n\nاین پروژه تحت مجوز **Apache License, Version 2.0** منتشر شده است. مفاد این بخش به\u200cطور صریح در راستای تقویت، گسترش و تأکید بر **بند ۷ (سلب هرگونه ضمانت)** و **بند ۸ (محدودیت کامل مسئولیت)** لایسنس Apache 2.0 تدوین شده و تا حداکثر میزان مجاز توسط قوانین حاکم، حاکم خواهد بود.\n\n**صرفاً جهت مقاصد آموزشی، پژوهشی و اطلاع\u200cرسانی. هیچ\u200cگونه ضمانت یا مسئولیت تجاری پذیرفته نمی\u200cشود.**\n\n### ۱. سلب کامل تمام ضمانت\u200cها\nبر اساس حداکثر حدود مجاز در قوانین حاکم، نرم\u200cافزار (شامل تمام کدها، مستندات، داده\u200cها و مواد مرتبط) دقیقاً بر مبنای اصل **«همان\u200cگونه که هست» (AS IS)** و **«به\u200cشرط وجود» (AS AVAILABLE)** و بدون هیچ\u200cگونه ضمانت یا شرطی (اعم از صریح، ضمنی، قانونی، عرفی یا غیره) ارائه می\u200cشود. این شامل و نه\u200cمحدود به ضمانت قابلیت فروش تجاری، تناسب برای مقصد خاص، عدم نقض حقوق ثالث، امنیت، دقت، کامل بودن، کارکرد بدون وقفه یا بدون خطا، و عاری بودن از ویروس یا اجزای مضر است. پدیدآورنده، دارندگان حق\u200cتألیف، نگهدارندگان و مشارکت\u200cکنندگان صریحاً تمام این ضمانت\u200cها را از خود سلب می\u200cنمایند.\n\n### ۲. محدودیت مطلق مسئولیت\nتحت هیچ شرایطی و بر پایهٔ هیچ نظریهٔ حقوقی (اعم از مسئولیت قراردادی، مسئولیت مدنی یا شبه\u200cجرم — شامل قصور عادی، قصور فاحش و رفتار عمدی — مسئولیت محض، مسئولیت محصول یا غیره) پدیدآورنده، نگهدارندگان، مشارکت\u200cکنندگان یا دارندگان حق\u200cتألیف در قبال هیچ\u200cگونه خسارتی (شامل خسارات مستقیم، غیرمستقیم، اتفاقی، تبعی، خاص، تنبیهی، جزایی یا هر نوع خسارت دیگر از جمله از دست رفتن داده، سود، درآمد، وقفه در کسب\u200cوکار، خرابی سیستم، آسیب سخت\u200cافزاری، رخنه امنیتی، صدمه جانی یا هر زیان دیگر) ناشی از استفاده، عدم توانایی در استفاده، تغییر، توزیع یا اتکا به نرم\u200cافزار پاسخگو نخواهند بود؛ حتی اگر از امکان وقوع چنین خساراتی مطلع شده باشند و حتی اگر هرگونه جبران خسارت از هدف اساسی خود بازبماند.\n\n### ۳. پذیرش کامل ریسک و مسئولیت انحصاری کاربر\nهرگونه استفاده، کلون، تغییر، استقرار، توزیع یا اتکا به این نرم\u200cافزار تماماً با صلاحدید و ریسک انحصاری کاربر انجام می\u200cگیرد. کاربر به\u200cطور انحصاری و کامل مسئول است برای:\n- اطمینان از انطباق کامل با کلیه قوانین و مقررات محلی، ملی و بین\u200cالمللی، کنترل\u200cهای صادراتی و شرایط اشخاص ثالث؛\n- ارزیابی مناسب بودن، امنیت و قانونی بودن نرم\u200cافزار برای هر منظوری؛\n- تمام پیامدهای ناشی از استفاده یا سوءاستفاده از آن.\n\nهیچ بخشی از این مخزن در حکم مشاوره حقوقی، مالی، سایبری، پزشکی، معماری یا هر نوع مشاوره تخصصی دیگر محسوب نمی\u200cشود.\n\n### ۴. تعهد گسترده به جبران خسارت و مصون\u200cسازی\nهر شخص یا نهادی با دسترسی، دانلود، کلون، فورک، مشاهده، کامپایل، توزیع یا استفاده از هر بخشی از این مخزن، به\u200cطور قطعی و غیرقابل بازگشت متعهد می\u200cگردد که پدیدآورنده، مشارکت\u200cکنندگان و دارندگان حق\u200cتألیف را در برابر هرگونه ادعا، درخواست، دعوی، مسئولیت، خسارت، زیان، هزینه و مخارج (شامل حق\u200cالوکاله معقول و هزینه\u200cهای دادرسی) ناشی از دسترسی، استفاده، سوءاستفاده، تغییر، توزیع یا نقض این سلب مسئولیت یا هر قانون حاکم، کاملاً مصون نگاه داشته و کلیه خسارات را جبران نماید.\n\n### ۵. قابلیت تفکیک و حداکثر قابلیت اجرا\nاگر هر یک از مفاد این سلب مسئولیت بر اساس قوانین حاکم غیرقابل اجرا یا باطل تشخیص داده شود، آن مفاد باید به حداقل میزان لازم برای قابل اجرا شدن اصلاح شود، یا در صورت عدم امکان اصلاح، حذف گردد. سایر مفاد به قوت کامل خود باقی می\u200cمانند. این سلب مسئولیت باید به گونه\u200cای تفسیر شود که حداکثر حمایت مجاز توسط قانون را فراهم آورد.\n\n### ۶. عدم اسقاط حقوق غیرقابل اسقاط\nهیچ بخشی از این سلب مسئولیت به\u200cمنظور حذف یا محدود کردن مسئولیتی که بر اساس قوانین اجباری حاکم قابل حذف یا محدود کردن نیست (از جمله مسئولیت ناشی از مرگ یا صدمه جانی ناشی از قصور در حوزه\u200cهایی که چنین محدودیتی ممنوع است) نوشته نشده است. در چنین مواردی، مسئولیت تا حداکثر میزان مجاز توسط قانون محدود می\u200cشود.\n',
    },
    'DISP-BACKUP': {
        "en": '---\n\n## Overview\n\nGraphics driver updates sometimes go wrong: black screens, lower performance, broken control panels, or a clean Windows install with no working GPU driver. **Display Driver Backup & Restore** gives you a simple safety net.\n\n- `Backup_Display_Driver.bat` exports your currently installed third-party **Display class** drivers (NVIDIA, AMD, Intel, etc.) into a local folder.\n- `Restore_Display_Driver.bat` reinstalls those saved drivers whenever you need them.\n\nNo installation, no extra tools, no dependencies. Everything uses components already built into Windows.\n\n## Features\n\n- One-click operation: just double-click the script\n- Automatic Administrator elevation (UAC prompt), no need to "Run as administrator" manually\n- Exports **only** third-party Display class drivers (`oem*.inf`), not your whole driver store\n- Restore installs every driver package found in the backup folder, including subfolders\n- Clear status messages (`[INFO]`, `[WARN]`, `[ERROR]`, `[SUCCESS]`) and meaningful exit codes\n- Works offline\n- Plain text scripts you can read and audit in a minute\n\n## Requirements\n\n| Requirement | Details |\n|---|---|\n| Operating system | Windows 10 or Windows 11 |\n| Permissions | Administrator (requested automatically) |\n| Tools | `pnputil` and Windows PowerShell 5.1 (both included with Windows) |\n\n## Quick Start\n\n### 1. Back up your current driver\n\n1. Download or clone this repository.\n2. Double-click **`Backup_Display_Driver.bat`**.\n3. Accept the UAC prompt.\n4. Wait for `[SUCCESS] Display drivers backed up successfully.`\n\n### 2. Restore it later\n\n1. Double-click **`Restore_Display_Driver.bat`**.\n2. Accept the UAC prompt.\n3. Wait for `[SUCCESS] Display drivers restored successfully.`\n4. **Restart your computer** to apply the changes.\n\n## Backup Location\n\nBoth scripts use the same fixed folder on your system drive:\n\n```\n%SystemDrive%\\Backup_Display_Driver\n```\n\nOn most PCs this is `C:\\Backup_Display_Driver`.\n\n> **Reinstalling Windows?** Copy this folder to a USB drive or another disk *before* formatting, then copy it back to the same path on the new installation and run the restore script.\n\nTo use a different location, edit this line at the top of **both** scripts:\n\n```bat\nset "BACKUP_DIR=%SystemDrive%\\Backup_Display_Driver"\n```\n\n## How It Works\n\n**Backup**\n\n1. Checks for Administrator rights and re-launches itself elevated if needed.\n2. Creates the backup folder if it does not exist.\n3. Uses PowerShell\'s `Get-WindowsDriver -Online` to list installed third-party drivers whose class is *Display* (GUID `{4d36e968-e325-11ce-bfc1-08002be10318}`).\n4. Exports each one with `pnputil /export-driver`.\n\n**Restore**\n\n1. Checks for Administrator rights and re-launches itself elevated if needed.\n2. Verifies that the backup folder exists and contains `.inf` files.\n3. Installs everything with:\n\n```bat\npnputil /add-driver "%BACKUP_DIR%\\*.inf" /subdirs /install\n```\n\n## Exit Codes and Messages\n\nThe backup script\'s PowerShell step returns these codes:\n\n| Code | Meaning |\n|---|---|\n| `0` | All display drivers were exported successfully |\n| `1` | Reading the driver list failed, or at least one export failed |\n| `2` | No third-party Display class drivers were found |\n\n## Notes\n\n- Only **third-party** display drivers are backed up. The built-in *Microsoft Basic Display Adapter* driver is part of Windows and is not exported.\n- The restore script installs **every** driver package inside the backup folder. Keep only the drivers you actually want to restore in it.\n- If the backup folder is missing or contains no `.inf` files, the restore script stops with a clear message and changes nothing.\n- A restart is recommended after restoring.\n\n## Troubleshooting\n\n| Problem | What to try |\n|---|---|\n| `Get-WindowsDriver failed` | Make sure the script runs elevated and that Windows is healthy (`sfc /scannow`, `DISM /Online /Cleanup-Image /RestoreHealth`). |\n| `No third-party Display class drivers found` | Your PC is probably using the generic Microsoft driver. Install the GPU vendor\'s driver first, then run the backup again. |\n| `Display backup directory not found` | Run the backup first, or copy your saved folder back to the expected path. |\n| The window closes too quickly | The scripts wait 5 seconds before closing. Run them from an open Command Prompt to keep the output on screen. |\n\n---\n\n## ⚖️ Absolute Legal Disclaimer, Waiver & Limitation of Liability\n\nThis project is licensed under the **Apache License, Version 2.0**. This disclaimer expressly supplements, expands, and reinforces **Section 7 (Disclaimer of Warranty)** and **Section 8 (Limitation of Liability)** of the Apache License 2.0, and shall control to the maximum extent permitted by applicable law.\n\n**FOR EDUCATIONAL, RESEARCH, AND INFORMATIONAL PURPOSES ONLY. NO COMMERCIAL WARRANTY OR LIABILITY IS ASSUMED.**\n\n### 1. Complete Disclaimer of All Warranties\nTo the maximum extent permitted by applicable law, the Software (including all code, documentation, data, and related materials) is provided strictly on an **"AS IS"** and **"AS AVAILABLE"** basis, without any warranties or conditions of any kind, whether express, implied, statutory, customary, or otherwise. This includes, without limitation, any warranties of merchantability, fitness for a particular purpose, non-infringement, title, security, accuracy, completeness, uninterrupted or error-free operation, or freedom from viruses or other harmful components. The author(s), copyright holder(s), maintainer(s), and contributor(s) expressly disclaim all such warranties.\n\n### 2. Absolute Limitation of Liability\nUnder no circumstances and under no legal theory (whether in contract, tort — including negligence, gross negligence, and willful misconduct — strict liability, product liability, or otherwise) shall the author(s), maintainer(s), contributor(s), or copyright holder(s) be liable for any damages whatsoever, including but not limited to direct, indirect, incidental, special, consequential, exemplary, punitive, or any other damages (including loss of data, profits, revenue, business interruption, system failure, hardware damage, security breaches, personal injury, or any other loss), arising out of or related to the use, inability to use, modification, distribution, or reliance upon the Software, even if advised of the possibility of such damages and even if any remedy fails of its essential purpose.\n\n### 3. Assumption of All Risk & User Responsibility\nAny use, cloning, modification, deployment, distribution, or reliance upon this Software is undertaken entirely at the user’s sole risk and discretion. The user is exclusively and solely responsible for:\n- Ensuring full compliance with all applicable local, national, and international laws, regulations, export controls, and third-party terms;\n- Evaluating the suitability, security, and legality of the Software for any purpose;\n- Any consequences arising from its use or misuse.\n\nNothing in this repository constitutes legal, financial, cybersecurity, medical, architectural, or any other form of professional advice.\n\n### 4. Broad Indemnification\nBy accessing, downloading, cloning, forking, viewing, compiling, distributing, or using any part of this repository, you irrevocably agree to indemnify, defend, and hold harmless the author(s), contributor(s), and copyright holder(s) from and against any and all claims, demands, actions, proceedings, liabilities, damages, losses, costs, and expenses (including reasonable attorneys’ fees and legal costs) arising out of or related to your access, use, misuse, modification, distribution, or violation of this disclaimer or any applicable law.\n\n### 5. Severability & Maximum Enforceability\nIf any provision of this disclaimer is held to be unenforceable or invalid under applicable law, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed. The remaining provisions shall continue in full force and effect. This disclaimer shall be interpreted to provide the maximum protection permitted by law.\n\n### 6. No Waiver of Non-Waivable Rights\nNothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.t any and all claims, demands, liabilities, damages, judgments, losses, costs, or expenses (including reasonable attorney fees and legal costs) resulting from your access, use, misuse, or violation of this disclaimer or applicable laws.\n',
        "fa": '---\n\n<div dir="rtl">\n\n## معرفی\n\nگاهی آپدیت درایور کارت گرافیک مشکل\u200cساز می\u200cشود: صفحه سیاه، افت کارایی، خراب شدن کنترل\u200cپنل، یا نصب تازه ویندوز که درایور گرافیک درستی ندارد. پروژه **Display Driver Backup & Restore** یک شبکه ایمنی ساده برای همین موقعیت\u200cهاست.\n\n- فایل `Backup_Display_Driver.bat` درایورهای شخص ثالث از کلاس **Display** (مثل NVIDIA، AMD و Intel) را که اکنون نصب هستند در یک پوشه محلی ذخیره می\u200cکند.\n- فایل `Restore_Display_Driver.bat` همان درایورهای ذخیره\u200cشده را هر زمان لازم باشد دوباره نصب می\u200cکند.\n\nنیازی به نصب برنامه یا ابزار اضافه نیست. همه چیز با ابزارهای داخلی خود ویندوز کار می\u200cکند.\n\n## ویژگی\u200cها\n\n- اجرای تک\u200cکلیکی: فقط روی اسکریپت دوبار کلیک کنید\n- درخواست خودکار دسترسی Administrator (پنجره UAC)، بدون نیاز به «Run as administrator» دستی\n- فقط درایورهای شخص ثالث کلاس Display (`oem*.inf`) پشتیبان\u200cگیری می\u200cشوند، نه کل درایور استور\n- بازیابی، همه پکیج\u200cهای درایور داخل پوشه پشتیبان (از جمله زیرپوشه\u200cها) را نصب می\u200cکند\n- پیام\u200cهای وضعیت واضح (`[INFO]`، `[WARN]`، `[ERROR]`، `[SUCCESS]`) و کد خروج استاندارد\n- بدون نیاز به اینترنت\n- اسکریپت\u200cها متن ساده\u200cاند و در چند دقیقه قابل خواندن و بررسی هستند\n\n## پیش\u200cنیازها\n\n| مورد | جزئیات |\n|---|---|\n| سیستم\u200cعامل | ویندوز ۱۰ یا ویندوز ۱۱ |\n| سطح دسترسی | Administrator (به\u200cصورت خودکار درخواست می\u200cشود) |\n| ابزارها | `pnputil` و Windows PowerShell 5.1 (هر دو همراه ویندوز هستند) |\n\n## شروع سریع\n\n### ۱. پشتیبان\u200cگیری از درایور فعلی\n\n1. این مخزن را دانلود یا کلون کنید.\n2. روی **`Backup_Display_Driver.bat`** دوبار کلیک کنید.\n3. پنجره UAC را تأیید کنید.\n4. منتظر پیام `[SUCCESS] Display drivers backed up successfully.` بمانید.\n\n### ۲. بازیابی در زمان نیاز\n\n1. روی **`Restore_Display_Driver.bat`** دوبار کلیک کنید.\n2. پنجره UAC را تأیید کنید.\n3. منتظر پیام `[SUCCESS] Display drivers restored successfully.` بمانید.\n4. **کامپیوتر را ری\u200cاستارت کنید** تا تغییرات اعمال شود.\n\n## محل پشتیبان\n\nهر دو اسکریپت از یک پوشه ثابت روی درایو سیستم استفاده می\u200cکنند:\n\n</div>\n\n```\n%SystemDrive%\\Backup_Display_Driver\n```\n\n<div dir="rtl">\n\nدر بیشتر سیستم\u200cها این مسیر `C:\\Backup_Display_Driver` است.\n\n> **قصد نصب مجدد ویندوز دارید؟** پیش از فرمت، این پوشه را روی فلش یا دیسک دیگری کپی کنید. بعد از نصب ویندوز جدید، آن را به همان مسیر برگردانید و اسکریپت بازیابی را اجرا کنید.\n\nبرای استفاده از مسیر دیگر، این خط را در ابتدای **هر دو** اسکریپت ویرایش کنید:\n\n</div>\n\n```bat\nset "BACKUP_DIR=%SystemDrive%\\Backup_Display_Driver"\n```\n\n<div dir="rtl">\n\n## نحوه کار\n\n**پشتیبان\u200cگیری**\n\n1. دسترسی Administrator را بررسی می\u200cکند و در صورت نیاز خودش را با سطح دسترسی بالا دوباره اجرا می\u200cکند.\n2. اگر پوشه پشتیبان وجود نداشته باشد آن را می\u200cسازد.\n3. با دستور `Get-WindowsDriver -Online` در PowerShell، درایورهای شخص ثالث نصب\u200cشده با کلاس *Display* (شناسه `{4d36e968-e325-11ce-bfc1-08002be10318}`) را فهرست می\u200cکند.\n4. هر کدام را با `pnputil /export-driver` خروجی می\u200cگیرد.\n\n**بازیابی**\n\n1. دسترسی Administrator را بررسی می\u200cکند و در صورت نیاز خودش را با سطح دسترسی بالا دوباره اجرا می\u200cکند.\n2. وجود پوشه پشتیبان و فایل\u200cهای `.inf` داخل آن را بررسی می\u200cکند.\n3. همه را با دستور زیر نصب می\u200cکند:\n\n</div>\n\n```bat\npnputil /add-driver "%BACKUP_DIR%\\*.inf" /subdirs /install\n```\n\n<div dir="rtl">\n\n## کدهای خروج\n\nبخش PowerShell در اسکریپت پشتیبان\u200cگیری این کدها را برمی\u200cگرداند:\n\n| کد | معنی |\n|---|---|\n| `0` | همه درایورهای Display با موفقیت پشتیبان\u200cگیری شدند |\n| `1` | خواندن فهرست درایورها ناموفق بود یا حداقل یک خروجی\u200cگیری خطا داد |\n| `2` | هیچ درایور شخص ثالث از کلاس Display پیدا نشد |\n\n## نکات مهم\n\n- فقط درایورهای **شخص ثالث** پشتیبان\u200cگیری می\u200cشوند. درایور پیش\u200cفرض ویندوز (*Microsoft Basic Display Adapter*) جزو خود ویندوز است و خروجی گرفته نمی\u200cشود.\n- اسکریپت بازیابی **همه** پکیج\u200cهای درایور داخل پوشه پشتیبان را نصب می\u200cکند. فقط درایورهایی را که واقعاً می\u200cخواهید بازیابی شوند در آن نگه دارید.\n- اگر پوشه پشتیبان وجود نداشته باشد یا فایل `.inf` نداشته باشد، اسکریپت بازیابی با یک پیام واضح متوقف می\u200cشود و هیچ تغییری نمی\u200cدهد.\n- بعد از بازیابی، ری\u200cاستارت توصیه می\u200cشود.\n\n## عیب\u200cیابی\n\n| مشکل | راه\u200cحل |\n|---|---|\n| `Get-WindowsDriver failed` | مطمئن شوید اسکریپت با دسترسی Administrator اجرا شده و ویندوز سالم است (`sfc /scannow` و `DISM /Online /Cleanup-Image /RestoreHealth`). |\n| `No third-party Display class drivers found` | احتمالاً سیستم شما از درایور عمومی مایکروسافت استفاده می\u200cکند. ابتدا درایور سازنده کارت گرافیک را نصب کنید و دوباره پشتیبان بگیرید. |\n| `Display backup directory not found` | ابتدا پشتیبان\u200cگیری کنید، یا پوشه ذخیره\u200cشده را به مسیر مورد انتظار برگردانید. |\n| پنجره خیلی سریع بسته می\u200cشود | اسکریپت\u200cها ۵ ثانیه قبل از بستن صبر می\u200cکنند. برای دیدن کامل خروجی، آن\u200cها را از داخل Command Prompt باز اجرا کنید. |\n\n---\n\n---\n\n## ⚖️ سلب مسئولیت مطلق قانونی، اسقاط حق و محدودیت کامل مسئولیت\n\nاین پروژه تحت مجوز **Apache License, Version 2.0** منتشر شده است. مفاد این بخش به\u200cطور صریح در راستای تقویت، گسترش و تأکید بر **بند ۷ (سلب هرگونه ضمانت)** و **بند ۸ (محدودیت کامل مسئولیت)** لایسنس Apache 2.0 تدوین شده و تا حداکثر میزان مجاز توسط قوانین حاکم، حاکم خواهد بود.\n\n**صرفاً جهت مقاصد آموزشی، پژوهشی و اطلاع\u200cرسانی. هیچ\u200cگونه ضمانت یا مسئولیت تجاری پذیرفته نمی\u200cشود.**\n\n### ۱. سلب کامل تمام ضمانت\u200cها\nبر اساس حداکثر حدود مجاز در قوانین حاکم، نرم\u200cافزار (شامل تمام کدها، مستندات، داده\u200cها و مواد مرتبط) دقیقاً بر مبنای اصل **«همان\u200cگونه که هست» (AS IS)** و **«به\u200cشرط وجود» (AS AVAILABLE)** و بدون هیچ\u200cگونه ضمانت یا شرطی (اعم از صریح، ضمنی، قانونی، عرفی یا غیره) ارائه می\u200cشود. این شامل و نه\u200cمحدود به ضمانت قابلیت فروش تجاری، تناسب برای مقصد خاص، عدم نقض حقوق ثالث، امنیت، دقت، کامل بودن، کارکرد بدون وقفه یا بدون خطا، و عاری بودن از ویروس یا اجزای مضر است. پدیدآورنده، دارندگان حق\u200cتألیف، نگهدارندگان و مشارکت\u200cکنندگان صریحاً تمام این ضمانت\u200cها را از خود سلب می\u200cنمایند.\n\n### ۲. محدودیت مطلق مسئولیت\nتحت هیچ شرایطی و بر پایهٔ هیچ نظریهٔ حقوقی (اعم از مسئولیت قراردادی، مسئولیت مدنی یا شبه\u200cجرم — شامل قصور عادی، قصور فاحش و رفتار عمدی — مسئولیت محض، مسئولیت محصول یا غیره) پدیدآورنده، نگهدارندگان، مشارکت\u200cکنندگان یا دارندگان حق\u200cتألیف در قبال هیچ\u200cگونه خسارتی (شامل خسارات مستقیم، غیرمستقیم، اتفاقی، تبعی، خاص، تنبیهی، جزایی یا هر نوع خسارت دیگر از جمله از دست رفتن داده، سود، درآمد، وقفه در کسب\u200cوکار، خرابی سیستم، آسیب سخت\u200cافزاری، رخنه امنیتی، صدمه جانی یا هر زیان دیگر) ناشی از استفاده، عدم توانایی در استفاده، تغییر، توزیع یا اتکا به نرم\u200cافزار پاسخگو نخواهند بود؛ حتی اگر از امکان وقوع چنین خساراتی مطلع شده باشند و حتی اگر هرگونه جبران خسارت از هدف اساسی خود بازبماند.\n\n### ۳. پذیرش کامل ریسک و مسئولیت انحصاری کاربر\nهرگونه استفاده، کلون، تغییر، استقرار، توزیع یا اتکا به این نرم\u200cافزار تماماً با صلاحدید و ریسک انحصاری کاربر انجام می\u200cگیرد. کاربر به\u200cطور انحصاری و کامل مسئول است برای:\n- اطمینان از انطباق کامل با کلیه قوانین و مقررات محلی، ملی و بین\u200cالمللی، کنترل\u200cهای صادراتی و شرایط اشخاص ثالث؛\n- ارزیابی مناسب بودن، امنیت و قانونی بودن نرم\u200cافزار برای هر منظوری؛\n- تمام پیامدهای ناشی از استفاده یا سوءاستفاده از آن.\n\nهیچ بخشی از این مخزن در حکم مشاوره حقوقی، مالی، سایبری، پزشکی، معماری یا هر نوع مشاوره تخصصی دیگر محسوب نمی\u200cشود.\n\n### ۴. تعهد گسترده به جبران خسارت و مصون\u200cسازی\nهر شخص یا نهادی با دسترسی، دانلود، کلون، فورک، مشاهده، کامپایل، توزیع یا استفاده از هر بخشی از این مخزن، به\u200cطور قطعی و غیرقابل بازگشت متعهد می\u200cگردد که پدیدآورنده، مشارکت\u200cکنندگان و دارندگان حق\u200cتألیف را در برابر هرگونه ادعا، درخواست، دعوی، مسئولیت، خسارت، زیان، هزینه و مخارج (شامل حق\u200cالوکاله معقول و هزینه\u200cهای دادرسی) ناشی از دسترسی، استفاده، سوءاستفاده، تغییر، توزیع یا نقض این سلب مسئولیت یا هر قانون حاکم، کاملاً مصون نگاه داشته و کلیه خسارات را جبران نماید.\n\n### ۵. قابلیت تفکیک و حداکثر قابلیت اجرا\nاگر هر یک از مفاد این سلب مسئولیت بر اساس قوانین حاکم غیرقابل اجرا یا باطل تشخیص داده شود، آن مفاد باید به حداقل میزان لازم برای قابل اجرا شدن اصلاح شود، یا در صورت عدم امکان اصلاح، حذف گردد. سایر مفاد به قوت کامل خود باقی می\u200cمانند. این سلب مسئولیت باید به گونه\u200cای تفسیر شود که حداکثر حمایت مجاز توسط قانون را فراهم آورد.\n\n### ۶. عدم اسقاط حقوق غیرقابل اسقاط\nهیچ بخشی از این سلب مسئولیت به\u200cمنظور حذف یا محدود کردن مسئولیتی که بر اساس قوانین اجباری حاکم قابل حذف یا محدود کردن نیست (از جمله مسئولیت ناشی از مرگ یا صدمه جانی ناشی از قصور در حوزه\u200cهایی که چنین محدودیتی ممنوع است) نوشته نشده است. در چنین مواردی، مسئولیت تا حداکثر میزان مجاز توسط قانون محدود می\u200cشود.\n',
    },
    'USB-SHIELD': {
        "en": '# USB Immunizer & Customizer\n\nA lightweight, automated Windows batch utility designed to immunize USB flash drives against automatic junk folder creation (such as `Android/`) and customize drive branding with a custom icon and volume label.\n\nIt keeps your USB storage clutter-free, stops smartphones and media devices from polluting your root directory, and makes your flash drive stand out with a professional appearance in Windows Explorer.\n\n---\n\n## 💡 How It Works (Folder Collision Immunity)\n\nIn standard filesystems (FAT32, exFAT, NTFS), a file and a folder **cannot share the exact same name** in the same directory.\n\nWhen connecting a USB drive to an Android device (via OTG) or car multimedia system, the operating system attempts to automatically create directories like `Android/`. \n\nThis tool creates a zero-byte **file** named `Android` marked with Hidden (`+h`) and System (`+s`) attributes. As a result, the OS is permanently blocked from generating unwanted folders in your root directory.\n\n---\n\n## 📁 Repository Contents\n\n| File | Type | Description |\n| :--- | :--- | :--- |\n| **`Prevent Automatic Folder Creation on USB Drive.bat`** | Batch Script | Main script that creates immunity dummy files, writes `autorun.inf`, and applies hidden/system attributes. |\n| **`.autorun.ico`** | Icon File | High-resolution custom flash drive icon applied to your USB drive. |\n\n---\n\n## ✨ Features\n\n- **🛡️ Directory Immunity:** Blocks Android OS and external devices from creating root junk folders like `Android/`.\n- **🎨 Custom Drive Branding:** Configures `autorun.inf` to display `.autorun.ico` and names the drive volume `Files` in Windows Explorer.\n- **👻 Clean Root Directory:** Automatically applies Hidden and System attributes (`+h +s`) to:\n  - `Android` (immunity dummy file)\n  - `System Volume Information !` (immunity dummy file)\n  - `autorun.inf` & `.autorun.ico`\n  - `System Volume Information` & `.cm0013` (if already present)\n- **🔑 Self-Elevating (UAC):** Automatically requests Administrator privileges via a temporary VBScript routine if not launched with elevated rights.\n- **⚡ 100% Native & Portable:** Zero dependencies. Powered purely by Windows native utilities (`attrib`, `type`).\n\n---\n\n## 🚀 How to Use\n\n1. Copy both **`Prevent Automatic Folder Creation on USB Drive.bat`** and **`.autorun.ico`** directly into the **root directory** of your USB flash drive (e.g., `E:\\`).\n2. **Double-click** the `.bat` file to execute.\n3. Click **Yes** when prompted by the User Account Control (UAC) dialog.\n4. The script will write the immunity files and apply the hidden/system flags.\n5. **Safely remove and reconnect** your USB drive to see your custom drive icon and label in Windows Explorer.\n\n---\n\n## 💻 System Requirements\n\n- **Operating System:** Windows 7, Windows 8.1, Windows 10, or Windows 11.\n- **Filesystem:** FAT32, exFAT, or NTFS formatted USB drives.\n\n---\n\n## ⚖️ Absolute Legal Disclaimer, Waiver & Limitation of Liability\n\nThis project is licensed under the **Apache License, Version 2.0**. This disclaimer expressly supplements, expands, and reinforces **Section 7 (Disclaimer of Warranty)** and **Section 8 (Limitation of Liability)** of the Apache License 2.0, and shall control to the maximum extent permitted by applicable law.\n\n**FOR EDUCATIONAL, RESEARCH, AND INFORMATIONAL PURPOSES ONLY. NO COMMERCIAL WARRANTY OR LIABILITY IS ASSUMED.**\n\n### 1. Complete Disclaimer of All Warranties\nTo the maximum extent permitted by applicable law, the Software (including all code, documentation, data, and related materials) is provided strictly on an **"AS IS"** and **"AS AVAILABLE"** basis, without any warranties or conditions of any kind, whether express, implied, statutory, customary, or otherwise. This includes, without limitation, any warranties of merchantability, fitness for a particular purpose, non-infringement, title, security, accuracy, completeness, uninterrupted or error-free operation, or freedom from viruses or other harmful components. The author(s), copyright holder(s), maintainer(s), and contributor(s) expressly disclaim all such warranties.\n\n### 2. Absolute Limitation of Liability\nUnder no circumstances and under no legal theory (whether in contract, tort — including negligence, gross negligence, and willful misconduct — strict liability, product liability, or otherwise) shall the author(s), maintainer(s), contributor(s), or copyright holder(s) be liable for any damages whatsoever, including but not limited to direct, indirect, incidental, special, consequential, exemplary, punitive, or any other damages (including loss of data, profits, revenue, business interruption, system failure, hardware damage, security breaches, personal injury, or any other loss), arising out of or related to the use, inability to use, modification, distribution, or reliance upon the Software, even if advised of the possibility of such damages and even if any remedy fails of its essential purpose.\n\n### 3. Assumption of All Risk & User Responsibility\nAny use, cloning, modification, deployment, distribution, or reliance upon this Software is undertaken entirely at the user’s sole risk and discretion. The user is exclusively and solely responsible for:\n- Ensuring full compliance with all applicable local, national, and international laws, regulations, export controls, and third-party terms;\n- Evaluating the suitability, security, and legality of the Software for any purpose;\n- Any consequences arising from its use or misuse.\n\nNothing in this repository constitutes legal, financial, cybersecurity, medical, architectural, or any other form of professional advice.\n\n### 4. Broad Indemnification\nBy accessing, downloading, cloning, forking, viewing, compiling, distributing, or using any part of this repository, you irrevocably agree to indemnify, defend, and hold harmless the author(s), contributor(s), and copyright holder(s) from and against any and all claims, demands, actions, proceedings, liabilities, damages, losses, costs, and expenses (including reasonable attorneys’ fees and legal costs) arising out of or related to your access, use, misuse, modification, distribution, or violation of this disclaimer or any applicable law.\n\n### 5. Severability & Maximum Enforceability\nIf any provision of this disclaimer is held to be unenforceable or invalid under applicable law, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed. The remaining provisions shall continue in full force and effect. This disclaimer shall be interpreted to provide the maximum protection permitted by law.\n\n### 6. No Waiver of Non-Waivable Rights\nNothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.\n',
        "fa": '# ابزار ایمن\u200cسازی و شخصی\u200cسازی فلش\u200cمموری (USB Immunizer & Customizer)\n\nیک ابزار سبک، خودکار و کاملاً بومی بر پایه بچ\u200cاسکریپت ویندوز (Batch Script) جهت ایمن\u200cسازی درایوهای فلش USB در برابر ساخته شدن خودکار پوشه\u200cهای مزاحم (مانند پوشه `Android`) و شخصی\u200cسازی کامل نام و آیکون درایو در محیط ویندوز.\n\nاین ابزار ریشه درایو فلش شما را تمیز و خلوت نگه می\u200cدارد، از ایجاد فایل\u200cها و پوشه\u200cهای اضافی توسط گوشی\u200cهای موبایل و ضبط خودرو جلوگیری کرده و با اختصاص یک آیکون شیک، ظاهری اختصاصی به درایو شما می\u200cبخشد.\n\n---\n\n## 💡 مکانیزم ایمن\u200cسازی پوشه\u200cها چگونه کار می\u200cکند؟\n\nدر فایل\u200cسیستم\u200cهای استاندارد (مانند FAT32، exFAT و NTFS)، ساختن همزمان یک «پوشه» و یک «فایل» با نام کاملاً یکسان در یک مسیر امکان\u200cپذیر نیست.\n\nهنگامی که فلش\u200cمموری را از طریق OTG به گوشی اندرویدی یا دستگاه\u200cهای پخش متصل می\u200cکنید، دستگاه بلافاصله پوشه\u200cای با نام `Android/` می\u200cسازد. این اسکریپت یک **فایل** با حجم صفر بایت با همان نام ایجاد کرده و به آن ویژگی\u200cهای مخفی و سیستمی (`+h +s`) می\u200cدهد. در نتیجه، سیستم\u200cعامل دیگر قادر به ساخت پوشه مزاحم نخواهد بود و فضای فلش شما کاملاً تمیز باقی می\u200cماند.\n\n---\n\n## 📁 فایل\u200cهای موجود در پروژه\n\n| نام فایل | نوع | عملکرد |\n| :--- | :--- | :--- |\n| **`Prevent Automatic Folder Creation on USB Drive.bat`** | بچ\u200cاسکریپت | اسکریپت اصلی برای ساخت فایل\u200cهای مسدودساز، ایجاد `autorun.inf` و مخفی\u200cسازی سیستمی. |\n| **`.autorun.ico`** | فایل آیکون | آیکون اختصاصی و باکیفیت فلش\u200cمموری برای نمایش به جای آیکون پیش\u200cفرض ویندوز. |\n\n---\n\n## ✨ قابلیت\u200cها و ویژگی\u200cها\n\n* 🛡️ **ایمن\u200cسازی در برابر ساخت پوشه:** جلوگیری از ساخت پوشه مزاحم `Android/` توسط گوشی\u200cها و دستگاه\u200cهای چندرسانه\u200cای.\n* 🎨 **شخصی\u200cسازی آیکون و نام درایو:** ایجاد فایل `autorun.inf` جهت نمایش آیکون زیبای `.autorun.ico` و تنظیم برچسب درایو با عنوان `Files`.\n* 👻 **خلوت\u200cسازی کامل ریشه فلش:** اعمال صفات سیستمی و مخفی (`+h +s`) به فایل\u200cهای اضافی شامل:\n  * فایل مسدودکننده `Android`\n  * فایل `System Volume Information !`\n  * فایل\u200cهای اتوران `autorun.inf` و `.autorun.ico`\n  * پوشه `System Volume Information` و فایل\u200cهای کش ضبط خودرو مانند `.cm0013`\n* 🔑 **ارتقای خودکار دسترسی ادمین (UAC):** فراخوانی خودکار تایید دسترسی ادمین در صورت نیاز با اسکریپت موقت VBS.\n* ⚡ **۱۰۰٪ بومی و سبک:** اجرا فقط با دستورات پیش\u200cفرض ویندوز (`attrib` و `type`) بدون نیاز به ابزارهای جانبی.\n\n---\n\n## 🚀 راهنمای استفاده\n\n1. هر دو فایل **`Prevent Automatic Folder Creation on USB Drive.bat`** و **`.autorun.ico`** را مستقیماً در **ریشه اصلی فلش مموری** خود (مثلاً درایو `:E` یا `:F`) کپی کنید.\n2. روی فایل اسکریپت **دو بار کلیک** کنید.\n3. در پنجره بازشده، دسترسی **UAC** را با زدن **Yes** تأیید کنید.\n4. اسکریپت فایل\u200cهای مسدودساز را ساخته و فایل\u200cهای مشخص\u200cشده را مخفی و سیستمی می\u200cکند.\n5. فلش\u200cمموری را یک بار جدا کرده (Eject) و مجدداً وصل کنید تا آیکون و برچسب جدید در My Computer ظاهر شوند.\n\n---\n\n## 💻 پیش\u200cنیازهای سیستم\n\n* **سیستم\u200cعامل:** ویندوز 7، 8.1، 10 یا 11.\n* **فایل\u200cسیستم:** درایوهای USB فرمت\u200cشده با FAT32، exFAT یا NTFS.\n\n---\n\n## ⚖️ سلب مسئولیت مطلق قانونی، اسقاط حق و محدودیت کامل مسئولیت\n\nاین پروژه تحت مجوز **Apache License, Version 2.0** منتشر شده است. مفاد این بخش به\u200cطور صریح در راستای تقویت، گسترش و تأکید بر **بند ۷ (سلب هرگونه ضمانت)** و **بند ۸ (محدودیت کامل مسئولیت)** لایسنس Apache 2.0 تدوین شده و تا حداکثر میزان مجاز توسط قوانین حاکم، حاکم خواهد بود.\n\n**صرفاً جهت مقاصد آموزشی، پژوهشی و اطلاع\u200cرسانی. هیچ\u200cگونه ضمانت یا مسئولیت تجاری پذیرفته نمی\u200cشود.**\n\n### ۱. سلب کامل تمام ضمانت\u200cها\nبر اساس حداکثر حدود مجاز در قوانین حاکم، نرم\u200cافزار (شامل تمام کدها، مستندات، داده\u200cها و مواد مرتبط) دقیقاً بر مبنای اصل **«همان\u200cگونه که هست» (AS IS)** و **«به\u200cشرط وجود» (AS AVAILABLE)** و بدون هیچ\u200cگونه ضمانت یا شرطی (اعم از صریح، ضمنی، قانونی، عرفی یا غیره) ارائه می\u200cشود. این شامل و نه\u200cمحدود به ضمانت قابلیت فروش تجاری، تناسب برای مقصد خاص، عدم نقض حقوق ثالث، امنیت، دقت، کامل بودن، کارکرد بدون وقفه یا بدون خطا، و عاری بودن از ویروس یا اجزای مضر است. پدیدآورنده، دارندگان حق\u200cتألیف، نگهدارندگان و مشارکت\u200cکنندگان صریحاً تمام این ضمانت\u200cها را از خود سلب می\u200cنمایند.\n\n### ۲. محدودیت مطلق مسئولیت\nتحت هیچ شرایطی و بر پایهٔ هیچ نظریهٔ حقوقی (اعم از مسئولیت قراردادی، مسئولیت مدنی یا شبه\u200cجرم — شامل قصور عادی، قصور فاحش و رفتار عمدی — مسئولیت محض، مسئولیت محصول یا غیره) پدیدآورنده، نگهدارندگان، مشارکت\u200cکنندگان یا دارندگان حق\u200cتألیف در قبال هیچ\u200cگونه خسارتی (شامل خسارات مستقیم، غیرمستقیم، اتفاقی، تبعی، خاص، تنبیهی، جزایی یا هر نوع خسارت دیگر از جمله از دست رفتن داده، سود، درآمد، وقفه در کسب\u200cوکار، خرابی سیستم، آسیب سخت\u200cافزاری، رخنه امنیتی، صدمه جانی یا هر زیان دیگر) ناشی از استفاده، عدم توانایی در استفاده، تغییر، توزیع یا اتکا به نرم\u200cافزار پاسخگو نخواهند بود؛ حتی اگر از امکان وقوع چنین خساراتی مطلع شده باشند و حتی اگر هرگونه جبران خسارت از هدف اساسی خود بازبماند.\n\n### ۳. پذیرش کامل ریسک و مسئولیت انحصاری کاربر\nهرگونه استفاده، کلون، تغییر، استقرار، توزیع یا اتکا به این نرم\u200cافزار تماماً با صلاحدید و ریسک انحصاری کاربر انجام می\u200cگیرد. کاربر به\u200cطور انحصاری و کامل مسئول است برای:\n- اطمینان از انطباق کامل با کلیه قوانین و مقررات محلی، ملی و بین\u200cالمللی، کنترل\u200cهای صادراتی و شرایط اشخاص ثالث؛\n- ارزیابی مناسب بودن، امنیت و قانونی بودن نرم\u200cافزار برای هر منظوری؛\n- تمام پیامدهای ناشی از استفاده یا سوءاستفاده از آن.\n\nهیچ بخشی از این مخزن در حکم مشاوره حقوقی، مالی، سایبری، پزشکی، معماری یا هر نوع مشاوره تخصصی دیگر محسوب نمی\u200cشود.\n\n### ۴. تعهد گسترده به جبران خسارت و مصون\u200cسازی\nهر شخص یا نهادی با دسترسی، دانلود، کلون، فورک، مشاهده، کامپایل، توزیع یا استفاده از هر بخشی از این مخزن، به\u200cطور قطعی و غیرقابل بازگشت متعهد می\u200cگردد که پدیدآورنده، مشارکت\u200cکنندگان و دارندگان حق\u200cتألیف را در برابر هرگونه ادعا، درخواست، دعوی، مسئولیت، خسارت، زیان، هزینه و مخارج (شامل حق\u200cالوکاله معقول و هزینه\u200cهای دادرسی) ناشی از دسترسی، استفاده، سوءاستفاده، تغییر، توزیع یا نقض این سلب مسئولیت یا هر قانون حاکم، کاملاً مصون نگاه داشته و کلیه خسارات را جبران نماید.\n\n### ۵. قابلیت تفکیک و حداکثر قابلیت اجرا\nاگر هر یک از مفاد این سلب مسئولیت بر اساس قوانین حاکم غیرقابل اجرا یا باطل تشخیص داده شود، آن مفاد باید به حداقل میزان لازم برای قابل اجرا شدن اصلاح شود، یا در صورت عدم امکان اصلاح، حذف گردد. سایر مفاد به قوت کامل خود باقی می\u200cمانند. این سلب مسئولیت باید به گونه\u200cای تفسیر شود که حداکثر حمایت مجاز توسط قانون را فراهم آورد.\n\n### ۶. عدم اسقاط حقوق غیرقابل اسقاط\nهیچ بخشی از این سلب مسئولیت به\u200cمنظور حذف یا محدود کردن مسئولیتی که بر اساس قوانین اجباری حاکم قابل حذف یا محدود کردن نیست (از جمله مسئولیت ناشی از مرگ یا صدمه جانی ناشی از قصور در حوزه\u200cهایی که چنین محدودیتی ممنوع است) نوشته نشده است. در چنین مواردی، مسئولیت تا حداکثر میزان مجاز توسط قانون محدود می\u200cشود.\n',
    },
    'DNS-RESET': {
        "en": '# Network Troubleshooter: DNS & Proxy Reset\n\nA lightweight, automated Windows batch utility designed to fix common network connectivity issues by resetting DNS server settings to DHCP, disabling system-wide proxies, and clearing the local DNS resolver cache.\n\nOften, VPN clients, proxy tools (e.g., v2ray, Clash, Outline), anti-censorship software, or unexpected network crashes leave behind modified proxy configurations and static DNS addresses. These leftover settings prevent your browser and apps from accessing the internet. This script fixes all of them in a single click.\n\n---\n\n## ✨ Features\n\n- **🔑 Automatic Elevation (UAC):** Checks for administrator privileges using `fsutil` and automatically prompts the UAC dialog via PowerShell if elevated rights are needed.\n- **🌐 Reset DNS to DHCP:** Clears static or stuck DNS servers across **all** network adapters and resets them to automatic (DHCP) via PowerShell (`Get-NetAdapter | Set-DnsClientServerAddress -ResetServerAddresses`).\n- **🚫 Disable System Proxy:** Forces `ProxyEnable = 0` in both User (`HKCU`) and System-wide (`HKLM`) Windows Registry locations to remove hanging proxy connections.\n- **🧹 Flush DNS Cache:** Clears the Windows DNS resolver cache (`ipconfig /flushdns`) to apply changes immediately without requiring a system reboot.\n- **⚡ Fast, Native & Clean:** Uses 100% built-in Windows tools (Batch & PowerShell) with clear status tags (`[+]`, `[-]`).\n\n---\n\n## 📋 Common Use Cases\n\n- **"No Internet" after closing VPN/Proxy:** The VPN closed, but left the system proxy turned on.\n- **Browser Errors:** You encounter `ERR_PROXY_CONNECTION_FAILED` or `DNS_PROBE_FINISHED_NO_INTERNET`.\n- **Stuck DNS:** Network adapters are pointing to unreachable or dead DNS servers.\n\n---\n\n## 🚀 How to Use\n\n1. Make sure the script file is saved with the `.bat` extension (e.g., `Reset-DNS-Proxy.bat`).\n2. **Double-click** the script to run it.\n3. If prompted by **User Account Control (UAC)**, click **Yes**.\n4. The script will execute all steps automatically.\n5. Once you see `All tasks completed successfully.`, press any key to close the window.\n\n---\n\n## 💻 System Requirements\n\n- **OS:** Windows 8.1, Windows 10, or Windows 11 (32-bit & 64-bit).\n- **PowerShell:** Version 5.0 or later (pre-installed on Windows 10 & 11).\n- **Permissions:** Administrator access (requested automatically by the script).\n\n---\n\n## ⚖️ Absolute Legal Disclaimer, Waiver & Limitation of Liability\n\nThis project is licensed under the **Apache License, Version 2.0**. This disclaimer expressly supplements, expands, and reinforces **Section 7 (Disclaimer of Warranty)** and **Section 8 (Limitation of Liability)** of the Apache License 2.0, and shall control to the maximum extent permitted by applicable law.\n\n**FOR EDUCATIONAL, RESEARCH, AND INFORMATIONAL PURPOSES ONLY. NO COMMERCIAL WARRANTY OR LIABILITY IS ASSUMED.**\n\n### 1. Complete Disclaimer of All Warranties\nTo the maximum extent permitted by applicable law, the Software (including all code, documentation, data, and related materials) is provided strictly on an **"AS IS"** and **"AS AVAILABLE"** basis, without any warranties or conditions of any kind, whether express, implied, statutory, customary, or otherwise. This includes, without limitation, any warranties of merchantability, fitness for a particular purpose, non-infringement, title, security, accuracy, completeness, uninterrupted or error-free operation, or freedom from viruses or other harmful components. The author(s), copyright holder(s), maintainer(s), and contributor(s) expressly disclaim all such warranties.\n\n### 2. Absolute Limitation of Liability\nUnder no circumstances and under no legal theory (whether in contract, tort — including negligence, gross negligence, and willful misconduct — strict liability, product liability, or otherwise) shall the author(s), maintainer(s), contributor(s), or copyright holder(s) be liable for any damages whatsoever, including but not limited to direct, indirect, incidental, special, consequential, exemplary, punitive, or any other damages (including loss of data, profits, revenue, business interruption, system failure, hardware damage, security breaches, personal injury, or any other loss), arising out of or related to the use, inability to use, modification, distribution, or reliance upon the Software, even if advised of the possibility of such damages and even if any remedy fails of its essential purpose.\n\n### 3. Assumption of All Risk & User Responsibility\nAny use, cloning, modification, deployment, distribution, or reliance upon this Software is undertaken entirely at the user’s sole risk and discretion. The user is exclusively and solely responsible for:\n- Ensuring full compliance with all applicable local, national, and international laws, regulations, export controls, and third-party terms;\n- Evaluating the suitability, security, and legality of the Software for any purpose;\n- Any consequences arising from its use or misuse.\n\nNothing in this repository constitutes legal, financial, cybersecurity, medical, architectural, or any other form of professional advice.\n\n### 4. Broad Indemnification\nBy accessing, downloading, cloning, forking, viewing, compiling, distributing, or using any part of this repository, you irrevocably agree to indemnify, defend, and hold harmless the author(s), contributor(s), and copyright holder(s) from and against any and all claims, demands, actions, proceedings, liabilities, damages, losses, costs, and expenses (including reasonable attorneys’ fees and legal costs) arising out of or related to your access, use, misuse, modification, distribution, or violation of this disclaimer or any applicable law.\n\n### 5. Severability & Maximum Enforceability\nIf any provision of this disclaimer is held to be unenforceable or invalid under applicable law, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed. The remaining provisions shall continue in full force and effect. This disclaimer shall be interpreted to provide the maximum protection permitted by law.\n\n### 6. No Waiver of Non-Waivable Rights\nNothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.\n',
        "fa": '# عیب\u200cیاب شبکه: بازنشانی DNS و غیرفعال\u200cسازی پروکسی\n\nیک ابزار سبک، سریع و خودکار بر پایه بچ\u200cاسکریپت (Batch Script) در ویندوز جهت رفع اختلالات رایج اتصال به اینترنت از طریق تنظیم مجدد DNS به حالت خودکار (DHCP)، غیرفعال\u200cسازی پروکسی سیستمی و پاک\u200cسازی حافظه کش DNS.\n\nدر بسیاری از مواقع پس از قطع اتصال فیلترشکن\u200cها، ابزارهای پروکسی (مانند v2ray، Clash، Outline و...) یا قطع ناگهانی برنامه\u200cها، تنظیمات پروکسی یا آدرس\u200cهای DNS تغییر یافته به حالت اولیه بازنمی\u200cگردند؛ این موضوع باعث قطع کامل دسترسی مرورگر و برنامه\u200cها به اینترنت می\u200cشود. این اسکریپت با یک کلیک تمامی این مشکلات را برطرف می\u200cکند.\n\n---\n\n## ✨ قابلیت\u200cها و ویژگی\u200cها\n\n* 🔑 **دریافت خودکار دسترسی Administrator:** بدون نیاز به کلیک راست و انتخاب «Run as administrator»، اسکریپت با استفاده از `fsutil` سطح دسترسی را بررسی کرده و در صورت نیاز پنجره UAC را به صورت خودکار بالا می\u200cآورد.\n* 🌐 **بازنشانی DNS تمام آداپتورها به DHCP:** حذف کامل DNSهای دستی یا مسدودشده از روی تمام کارت\u200cهای شبکه و برگرداندن آن\u200cها به حالت خودکار از طریق دستور بومی پاورشل (`Set-DnsClientServerAddress`).\n* 🚫 **غیرفعال\u200cسازی کامل پروکسی سیستمی:** صفر کردن مقدار `ProxyEnable` در رجیستری ویندوز برای هر دو بخش کاربر جاری (`HKCU`) و سطح کل سیستم (`HKLM`).\n* 🧹 **پاک\u200cسازی کش DNS (Flush DNS):** اجرای دستور `ipconfig /flushdns` برای حذف رکوردهای ذخیره\u200cشده و اعمال فوری تنظیمات بدون نیاز به ری\u200cاستارت سیستم.\n* ⚡ **بومی، تمیز و سبک:** متکی به ابزارهای داخلی ویندوز بدون نیاز به نصب هرگونه نرم\u200cافزار یا کتابخانه جانبی، همراه با خروجی خط فرمان شفاف با برچسب\u200cهای وضعیت (`[+]`, `[-]`).\n\n---\n\n## 📋 چه زمانی از این اسکریپت استفاده کنیم؟\n\n* زمانی که فیلترشکن یا پروکسی را بسته\u200cاید ولی اینترنت سیستم وصل نمی\u200cشود.\n* مواجهه با خطاهای معروفی مثل `ERR_PROXY_CONNECTION_FAILED` یا `DNS_PROBE_FINISHED_NO_INTERNET` در مرورگرها.\n* تنظیم ماندن یک DNS نامعتبر روی کارت شبکه که مانع ترجمه آدرس سایت\u200cها می\u200cشود.\n\n---\n\n## 🚀 راهنمای استفاده\n\n1. اسکریپت را با پسوند **`.bat`** ذخیره کنید (مثلاً `Reset-DNS-Proxy.bat`).\n2. روی فایل دو بار کلیک کنید.\n3. در صورت نمایش پنجره درخواست دسترسی (UAC)، گزینه **Yes** را انتخاب کنید.\n4. منتظر بمانید تا فرایند انجام شود و پیام `All tasks completed successfully.` نمایش داده شود.\n5. یک کلید را فشار دهید تا پنجره بسته شود. اکنون اینترنت شما آماده استفاده است.\n\n---\n\n## 💻 پیش\u200cنیازهای سیستم\n\n* **سیستم\u200cعامل:** ویندوز 8.1، ویندوز 10 یا ویندوز 11 (نسخه\u200cهای ۳۲ و ۶۴ بیتی).\n* **پاورشل (PowerShell):** نسخه 5.0 یا بالاتر (به صورت پیش\u200cفرض در ویندوز 10 و 11 فعال است).\n* **سطح دسترسی:** ادمین (اسکریپت به صورت خودکار درخواست می\u200cکند).\n\n---\n\n## ⚖️ سلب مسئولیت مطلق قانونی، اسقاط حق و محدودیت کامل مسئولیت\n\nاین پروژه تحت مجوز **Apache License, Version 2.0** منتشر شده است. مفاد این بخش به\u200cطور صریح در راستای تقویت، گسترش و تأکید بر **بند ۷ (سلب هرگونه ضمانت)** و **بند ۸ (محدودیت کامل مسئولیت)** لایسنس Apache 2.0 تدوین شده و تا حداکثر میزان مجاز توسط قوانین حاکم، حاکم خواهد بود.\n\n**صرفاً جهت مقاصد آموزشی، پژوهشی و اطلاع\u200cرسانی. هیچ\u200cگونه ضمانت یا مسئولیت تجاری پذیرفته نمی\u200cشود.**\n\n### ۱. سلب کامل تمام ضمانت\u200cها\nبر اساس حداکثر حدود مجاز در قوانین حاکم، نرم\u200cافزار (شامل تمام کدها، مستندات، داده\u200cها و مواد مرتبط) دقیقاً بر مبنای اصل **«همان\u200cگونه که هست» (AS IS)** و **«به\u200cشرط وجود» (AS AVAILABLE)** و بدون هیچ\u200cگونه ضمانت یا شرطی (اعم از صریح، ضمنی، قانونی، عرفی یا غیره) ارائه می\u200cشود. این شامل و نه\u200cمحدود به ضمانت قابلیت فروش تجاری، تناسب برای مقصد خاص، عدم نقض حقوق ثالث، امنیت، دقت، کامل بودن، کارکرد بدون وقفه یا بدون خطا، و عاری بودن از ویروس یا اجزای مضر است. پدیدآورنده، دارندگان حق\u200cتألیف، نگهدارندگان و مشارکت\u200cکنندگان صریحاً تمام این ضمانت\u200cها را از خود سلب می\u200cنمایند.\n\n### ۲. محدودیت مطلق مسئولیت\nتحت هیچ شرایطی و بر پایهٔ هیچ نظریهٔ حقوقی (اعم از مسئولیت قراردادی، مسئولیت مدنی یا شبه\u200cجرم — شامل قصور عادی، قصور فاحش و رفتار عمدی — مسئولیت محض، مسئولیت محصول یا غیره) پدیدآورنده، نگهدارندگان، مشارکت\u200cکنندگان یا دارندگان حق\u200cتألیف در قبال هیچ\u200cگونه خسارتی (شامل خسارات مستقیم، غیرمستقیم، اتفاقی، تبعی، خاص، تنبیهی، جزایی یا هر نوع خسارت دیگر از جمله از دست رفتن داده، سود، درآمد، وقفه در کسب\u200cوکار، خرابی سیستم، آسیب سخت\u200cافزاری، رخنه امنیتی، صدمه جانی یا هر زیان دیگر) ناشی از استفاده، عدم توانایی در استفاده، تغییر، توزیع یا اتکا به نرم\u200cافزار پاسخگو نخواهند بود؛ حتی اگر از امکان وقوع چنین خساراتی مطلع شده باشند و حتی اگر هرگونه جبران خسارت از هدف اساسی خود بازبماند.\n\n### ۳. پذیرش کامل ریسک و مسئولیت انحصاری کاربر\nهرگونه استفاده، کلون، تغییر، استقرار، توزیع یا اتکا به این نرم\u200cافزار تماماً با صلاحدید و ریسک انحصاری کاربر انجام می\u200cگیرد. کاربر به\u200cطور انحصاری و کامل مسئول است برای:\n- اطمینان از انطباق کامل با کلیه قوانین و مقررات محلی، ملی و بین\u200cالمللی، کنترل\u200cهای صادراتی و شرایط اشخاص ثالث؛\n- ارزیابی مناسب بودن، امنیت و قانونی بودن نرم\u200cافزار برای هر منظوری؛\n- تمام پیامدهای ناشی از استفاده یا سوءاستفاده از آن.\n\nهیچ بخشی از این مخزن در حکم مشاوره حقوقی، مالی، سایبری، پزشکی، معماری یا هر نوع مشاوره تخصصی دیگر محسوب نمی\u200cشود.\n\n### ۴. تعهد گسترده به جبران خسارت و مصون\u200cسازی\nهر شخص یا نهادی با دسترسی، دانلود، کلون، فورک، مشاهده، کامپایل، توزیع یا استفاده از هر بخشی از این مخزن، به\u200cطور قطعی و غیرقابل بازگشت متعهد می\u200cگردد که پدیدآورنده، مشارکت\u200cکنندگان و دارندگان حق\u200cتألیف را در برابر هرگونه ادعا، درخواست، دعوی، مسئولیت، خسارت، زیان، هزینه و مخارج (شامل حق\u200cالوکاله معقول و هزینه\u200cهای دادرسی) ناشی از دسترسی، استفاده، سوءاستفاده، تغییر، توزیع یا نقض این سلب مسئولیت یا هر قانون حاکم، کاملاً مصون نگاه داشته و کلیه خسارات را جبران نماید.\n\n### ۵. قابلیت تفکیک و حداکثر قابلیت اجرا\nاگر هر یک از مفاد این سلب مسئولیت بر اساس قوانین حاکم غیرقابل اجرا یا باطل تشخیص داده شود، آن مفاد باید به حداقل میزان لازم برای قابل اجرا شدن اصلاح شود، یا در صورت عدم امکان اصلاح، حذف گردد. سایر مفاد به قوت کامل خود باقی می\u200cمانند. این سلب مسئولیت باید به گونه\u200cای تفسیر شود که حداکثر حمایت مجاز توسط قانون را فراهم آورد.\n\n### ۶. عدم اسقاط حقوق غیرقابل اسقاط\nهیچ بخشی از این سلب مسئولیت به\u200cمنظور حذف یا محدود کردن مسئولیتی که بر اساس قوانین اجباری حاکم قابل حذف یا محدود کردن نیست (از جمله مسئولیت ناشی از مرگ یا صدمه جانی ناشی از قصور در حوزه\u200cهایی که چنین محدودیتی ممنوع است) نوشته نشده است. در چنین مواردی، مسئولیت تا حداکثر میزان مجاز توسط قانون محدود می\u200cشود.\n',
    },
    'MEDIA-RENAME': {
        "en": '# Media Batch Renamer (Images to JPG & Videos to MP4)\n\nA set of high-speed, standalone Windows batch scripts designed to recursively scan directories and bulk-normalize image and video file extensions into standard **`.jpg`** and **`.mp4`** formats.\n\nEquipped with intelligent collision prevention, these scripts guarantee that **no file is ever overwritten or lost**.\n\n> **Note:** These utilities perform fast file extension renaming. They do not re-encode or transcode media streams.\n\n---\n\n## 📁 Included Scripts\n\n| Script | Purpose | Supported Formats |\n| :--- | :--- | :--- |\n| **`Image to JPG Renamer.bat`** | Renames all image formats to `.jpg` | 50+ formats (PNG, WEBP, AVIF, TIFF, HEIC, PSD, Camera RAW, etc.) |\n| **`Video to MP4 Renamer.bat`** | Renames all video formats to `.mp4` | 40+ formats (MKV, MOV, AVI, WEBM, FLV, TS, Pro RAW Video, etc.) |\n\n---\n\n## ✨ Features\n\n- **🛡️ 100% Collision-Safe:** If a target filename already exists (e.g., `photo.jpg`), the script automatically appends an incremental suffix (`photo (1).jpg`, `photo (2).jpg`), preventing any file overwriting or data loss.\n- **🔄 Deep Recursive Scan:** Processes all files in the current folder and travels through all subdirectories automatically.\n- **🚫 Smart Format Exclusion:**\n  - `Image to JPG Renamer` skips `.jpg` and `.gif` (preserving animated GIFs).\n  - `Video to MP4 Renamer` skips files already having the `.mp4` extension.\n- **🎯 Massive Format Support:**\n  - **Images:** Common web formats, Apple HEIC/HEIF, Adobe PSD/AI/EPS, and Camera RAW profiles (CR2, CR3, NEF, ARW, DNG, RAF, RW2, etc.).\n  - **Videos:** Standard containers, legacy formats (RMVB, VOB, WMV), modern web formats (WEBM), and professional cinematic RAW video (BRAW, R3D, ARI, CRM).\n- **📊 Detailed Terminal Summary:** Real-time feedback with explicit status tags (`[OK]`, `[DUP]`, `[FAIL]`) and an audit summary showing renamed, suffixed, and failed counts.\n- **⚡ Zero Dependencies:** Pure Windows Batch script (`.bat`). No Python, PowerShell, FFmpeg, or third-party binaries required.\n\n---\n\n## 🚀 How to Use\n\n1. Copy the desired script (`Image to JPG Renamer.bat` or `Video to MP4 Renamer.bat`) into the root directory containing your media files.\n2. **Double-click** the script to launch it.\n3. The terminal will scan the folder and all subfolders, displaying the rename progress in real-time.\n4. Review the final statistics report.\n5. The console window will automatically close after 10 seconds (or upon pressing any key).\n\n---\n\n## 💻 System Requirements\n\n- **Operating System:** Windows 7, Windows 8.1, Windows 10, or Windows 11.\n- **Permissions:** Standard user permissions (Administrator rights needed only if files reside in protected system paths).\n\n---\n\n## ⚖️ Absolute Legal Disclaimer, Waiver & Limitation of Liability\n\nThis project is licensed under the **Apache License, Version 2.0**. This disclaimer expressly supplements, expands, and reinforces **Section 7 (Disclaimer of Warranty)** and **Section 8 (Limitation of Liability)** of the Apache License 2.0, and shall control to the maximum extent permitted by applicable law.\n\n**FOR EDUCATIONAL, RESEARCH, AND INFORMATIONAL PURPOSES ONLY. NO COMMERCIAL WARRANTY OR LIABILITY IS ASSUMED.**\n\n### 1. Complete Disclaimer of All Warranties\nTo the maximum extent permitted by applicable law, the Software (including all code, documentation, data, and related materials) is provided strictly on an **"AS IS"** and **"AS AVAILABLE"** basis, without any warranties or conditions of any kind, whether express, implied, statutory, customary, or otherwise. This includes, without limitation, any warranties of merchantability, fitness for a particular purpose, non-infringement, title, security, accuracy, completeness, uninterrupted or error-free operation, or freedom from viruses or other harmful components. The author(s), copyright holder(s), maintainer(s), and contributor(s) expressly disclaim all such warranties.\n\n### 2. Absolute Limitation of Liability\nUnder no circumstances and under no legal theory (whether in contract, tort — including negligence, gross negligence, and willful misconduct — strict liability, product liability, or otherwise) shall the author(s), maintainer(s), contributor(s), or copyright holder(s) be liable for any damages whatsoever, including but not limited to direct, indirect, incidental, special, consequential, exemplary, punitive, or any other damages (including loss of data, profits, revenue, business interruption, system failure, hardware damage, security breaches, personal injury, or any other loss), arising out of or related to the use, inability to use, modification, distribution, or reliance upon the Software, even if advised of the possibility of such damages and even if any remedy fails of its essential purpose.\n\n### 3. Assumption of All Risk & User Responsibility\nAny use, cloning, modification, deployment, distribution, or reliance upon this Software is undertaken entirely at the user’s sole risk and discretion. The user is exclusively and solely responsible for:\n- Ensuring full compliance with all applicable local, national, and international laws, regulations, export controls, and third-party terms;\n- Evaluating the suitability, security, and legality of the Software for any purpose;\n- Any consequences arising from its use or misuse.\n\nNothing in this repository constitutes legal, financial, cybersecurity, medical, architectural, or any other form of professional advice.\n\n### 4. Broad Indemnification\nBy accessing, downloading, cloning, forking, viewing, compiling, distributing, or using any part of this repository, you irrevocably agree to indemnify, defend, and hold harmless the author(s), contributor(s), and copyright holder(s) from and against any and all claims, demands, actions, proceedings, liabilities, damages, losses, costs, and expenses (including reasonable attorneys’ fees and legal costs) arising out of or related to your access, use, misuse, modification, distribution, or violation of this disclaimer or any applicable law.\n\n### 5. Severability & Maximum Enforceability\nIf any provision of this disclaimer is held to be unenforceable or invalid under applicable law, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed. The remaining provisions shall continue in full force and effect. This disclaimer shall be interpreted to provide the maximum protection permitted by law.\n\n### 6. No Waiver of Non-Waivable Rights\nNothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.\n',
        "fa": '# ابزار تغییر نام دسته\u200cای فایل\u200cهای رسانه\u200cای (تصاویر به JPG و ویدیوها به MP4)\n\nمجموعه\u200cای از اسکریپت\u200cهای سبک، پرسرعت و مستقل بر پایه بچ\u200cاسکریپت ویندوز (Batch Script) جهت اسکن خودکار و بازگشتی پوشه\u200cها و یکپارچه\u200cسازی پسوند فایل\u200cهای تصویری و ویدیویی به فرمت\u200cهای استاندارد **`.jpg`** و **`.mp4`**.\n\nاین اسکریپت\u200cها مجهز به سیستم هوشمند جلوگیری از تداخل نام هستند و تضمین می\u200cکنند که **هیچ فایلی بازنویسی (Overwrite) یا پاک نخواهد شد**.\n\n> **توجه:** این ابزارها صرفاً عملیات تغییر سریع پسوند (Rename) را انجام می\u200cدهند و فایل\u200cها را انکود یا فشرده\u200cسازی مجدد نمی\u200cکنند.\n\n---\n\n## 📁 اسکریپت\u200cهای موجود در پروژه\n\n| نام اسکریپت | هدف | فرمت\u200cهای تحت پوشش |\n| :--- | :--- | :--- |\n| **`Image to JPG Renamer.bat`** | تغییر پسوند انواع تصاویر به `.jpg` | بیش از ۵۰ فرمت مختلف (PNG، WEBP، AVIF، TIFF، HEIC، PSD، فرمت\u200cهای RAW دوربین\u200cها و...) |\n| **`Video to MP4 Renamer.bat`** | تغییر پسوند انواع ویدیوها به `.mp4` | بیش از ۴۰ فرمت مختلف (MKV، MOV، AVI، WEBM، FLV، TS، ویدیوهای خام سینمایی و...) |\n\n---\n\n## ✨ قابلیت\u200cها و ویژگی\u200cها\n\n* 🛡️ **۱۰۰٪ ایمن در برابر تداخل نام\u200cها:** در صورتی که فایلی با همان نام و پسوند جدید وجود داشته باشد، اسکریپت به صورت خودکار یک شماره به انتهای آن اضافه می\u200cکند (مانند `photo (1).jpg` و `photo (2).jpg`) تا هیچ داده\u200cای رونویسی یا پاک نشود.\n* 🔄 **اسکن بازگشتی و عمیق پوشه\u200cها:** شناسایی و پردازش تمامی فایل\u200cهای موجود در پوشه جاری و تمام زیرپوشه\u200cهای تودرتو به صورت خودکار.\n* 🚫 **استثناهای هوشمند:**\n  * در اسکریپت تصاویر، فایل\u200cهای با پسوند `.jpg` و فایل\u200cهای گیف (`.gif` جهت حفظ انیمیشن) نادیده گرفته می\u200cشوند.\n  * در اسکریپت ویدیوها، فایل\u200cهایی که از قبل دارای پسوند `.mp4` هستند بررسی مجدد نمی\u200cشوند.\n* 🎯 **پشتیبانی گسترده از انواع فرمت\u200cها:**\n  * **تصاویر:** فرمت\u200cهای رایج وب، تصاویر اپل (HEIC/HEIF)، فایل\u200cهای گرافیکی لایه\u200cباز (PSD/AI) و فایل\u200cهای خام دوربین\u200cهای عکاسی حرفه\u200cای (CR2، CR3، NEF، ARW، DNG، RAF و...).\n  * **ویدیوها:** کانتینرهای رایج (MKV، MOV، AVI)، فرمت\u200cهای قدیمی (VOB، WMV، RMVB) و فرمت\u200cهای ویدئویی سینمایی (BRAW، R3D، ARI و...).\n* 📊 **گزارش آماری دقیق در کنسول:** نمایش وضعیت لحظه\u200cای با برچسب\u200cهای واضح (`[OK]` موفق، `[DUP]` نام تکراری مدیریت\u200cشده، `[FAIL]` ناموفق) همراه با گزارش نهایی تعداد فایل\u200cها.\n* ⚡ **کاملاً بومی و مستقل:** بدون نیاز به پایتون، پاورشل، نرم\u200cافزار FFmpeg یا برنامه\u200cهای جانبی.\n\n---\n\n## 🚀 راهنمای استفاده\n\n1. اسکریپت مورد نظر (`Image to JPG Renamer.bat` یا `Video to MP4 Renamer.bat`) را داخل پوشه\u200cای که فایل\u200cهای مدیا در آن قرار دارند کپی کنید.\n2. روی فایل اسکریپت **دو بار کلیک** کنید.\n3. عملیات اسکن شروع شده و تغییر نام فایل\u200cها به صورت لحظه\u200cای در محیط خط فرمان نمایش داده می\u200cشود.\n4. در انتها، جدول آماری فایل\u200cهای تغییریافته را مشاهده خواهید کرد.\n5. پنجره اسکریپت پس از ۱۰ ثانیه به صورت خودکار بسته می\u200cشود (یا می\u200cتوانید کلیدی را برای بستن فوری فشار دهید).\n\n---\n\n## 💻 پیش\u200cنیازهای سیستم\n\n* **سیستم\u200cعامل:** ویندوز 7، 8.1، 10 یا 11.\n* **سطح دسترسی:** کاربر عادی (دسترسی Administrator تنها در صورتی نیاز است که فایل\u200cها در پوشه\u200cهای محافظت\u200cشده ویندوز قرار داشته باشند).\n\n---\n\n## ⚖️ سلب مسئولیت مطلق قانونی، اسقاط حق و محدودیت کامل مسئولیت\n\nاین پروژه تحت مجوز **Apache License, Version 2.0** منتشر شده است. مفاد این بخش به\u200cطور صریح در راستای تقویت، گسترش و تأکید بر **بند ۷ (سلب هرگونه ضمانت)** و **بند ۸ (محدودیت کامل مسئولیت)** لایسنس Apache 2.0 تدوین شده و تا حداکثر میزان مجاز توسط قوانین حاکم، حاکم خواهد بود.\n\n**صرفاً جهت مقاصد آموزشی، پژوهشی و اطلاع\u200cرسانی. هیچ\u200cگونه ضمانت یا مسئولیت تجاری پذیرفته نمی\u200cشود.**\n\n### ۱. سلب کامل تمام ضمانت\u200cها\nبر اساس حداکثر حدود مجاز در قوانین حاکم، نرم\u200cافزار (شامل تمام کدها، مستندات، داده\u200cها و مواد مرتبط) دقیقاً بر مبنای اصل **«همان\u200cگونه که هست» (AS IS)** و **«به\u200cشرط وجود» (AS AVAILABLE)** و بدون هیچ\u200cگونه ضمانت یا شرطی (اعم از صریح، ضمنی، قانونی، عرفی یا غیره) ارائه می\u200cشود. این شامل و نه\u200cمحدود به ضمانت قابلیت فروش تجاری، تناسب برای مقصد خاص، عدم نقض حقوق ثالث، امنیت، دقت، کامل بودن، کارکرد بدون وقفه یا بدون خطا، و عاری بودن از ویروس یا اجزای مضر است. پدیدآورنده، دارندگان حق\u200cتألیف، نگهدارندگان و مشارکت\u200cکنندگان صریحاً تمام این ضمانت\u200cها را از خود سلب می\u200cنمایند.\n\n### ۲. محدودیت مطلق مسئولیت\nتحت هیچ شرایطی و بر پایهٔ هیچ نظریهٔ حقوقی (اعم از مسئولیت قراردادی، مسئولیت مدنی یا شبه\u200cجرم — شامل قصور عادی، قصور فاحش و رفتار عمدی — مسئولیت محض، مسئولیت محصول یا غیره) پدیدآورنده، نگهدارندگان، مشارکت\u200cکنندگان یا دارندگان حق\u200cتألیف در قبال هیچ\u200cگونه خسارتی (شامل خسارات مستقیم، غیرمستقیم، اتفاقی، تبعی، خاص، تنبیهی، جزایی یا هر نوع خسارت دیگر از جمله از دست رفتن داده، سود، درآمد، وقفه در کسب\u200cوکار، خرابی سیستم، آسیب سخت\u200cافزاری، رخنه امنیتی، صدمه جانی یا هر زیان دیگر) ناشی از استفاده، عدم توانایی در استفاده، تغییر، توزیع یا اتکا به نرم\u200cافزار پاسخگو نخواهند بود؛ حتی اگر از امکان وقوع چنین خساراتی مطلع شده باشند و حتی اگر هرگونه جبران خسارت از هدف اساسی خود بازبماند.\n\n### ۳. پذیرش کامل ریسک و مسئولیت انحصاری کاربر\nهرگونه استفاده، کلون، تغییر، استقرار، توزیع یا اتکا به این نرم\u200cافزار تماماً با صلاحدید و ریسک انحصاری کاربر انجام می\u200cگیرد. کاربر به\u200cطور انحصاری و کامل مسئول است برای:\n- اطمینان از انطباق کامل با کلیه قوانین و مقررات محلی، ملی و بین\u200cالمللی، کنترل\u200cهای صادراتی و شرایط اشخاص ثالث؛\n- ارزیابی مناسب بودن، امنیت و قانونی بودن نرم\u200cافزار برای هر منظوری؛\n- تمام پیامدهای ناشی از استفاده یا سوءاستفاده از آن.\n\nهیچ بخشی از این مخزن در حکم مشاوره حقوقی، مالی، سایبری، پزشکی، معماری یا هر نوع مشاوره تخصصی دیگر محسوب نمی\u200cشود.\n\n### ۴. تعهد گسترده به جبران خسارت و مصون\u200cسازی\nهر شخص یا نهادی با دسترسی، دانلود، کلون، فورک، مشاهده، کامپایل، توزیع یا استفاده از هر بخشی از این مخزن، به\u200cطور قطعی و غیرقابل بازگشت متعهد می\u200cگردد که پدیدآورنده، مشارکت\u200cکنندگان و دارندگان حق\u200cتألیف را در برابر هرگونه ادعا، درخواست، دعوی، مسئولیت، خسارت، زیان، هزینه و مخارج (شامل حق\u200cالوکاله معقول و هزینه\u200cهای دادرسی) ناشی از دسترسی، استفاده، سوءاستفاده، تغییر، توزیع یا نقض این سلب مسئولیت یا هر قانون حاکم، کاملاً مصون نگاه داشته و کلیه خسارات را جبران نماید.\n\n### ۵. قابلیت تفکیک و حداکثر قابلیت اجرا\nاگر هر یک از مفاد این سلب مسئولیت بر اساس قوانین حاکم غیرقابل اجرا یا باطل تشخیص داده شود، آن مفاد باید به حداقل میزان لازم برای قابل اجرا شدن اصلاح شود، یا در صورت عدم امکان اصلاح، حذف گردد. سایر مفاد به قوت کامل خود باقی می\u200cمانند. این سلب مسئولیت باید به گونه\u200cای تفسیر شود که حداکثر حمایت مجاز توسط قانون را فراهم آورد.\n\n### ۶. عدم اسقاط حقوق غیرقابل اسقاط\nهیچ بخشی از این سلب مسئولیت به\u200cمنظور حذف یا محدود کردن مسئولیتی که بر اساس قوانین اجباری حاکم قابل حذف یا محدود کردن نیست (از جمله مسئولیت ناشی از مرگ یا صدمه جانی ناشی از قصور در حوزه\u200cهایی که چنین محدودیتی ممنوع است) نوشته نشده است. در چنین مواردی، مسئولیت تا حداکثر میزان مجاز توسط قانون محدود می\u200cشود.\n',
    },
    'TREE-EXPORT': {
        "en": '# Directory Tree & File Metadata Auditor\n\nA fast, lightweight, and native Windows Batch & PowerShell hybrid utility designed to recursively scan directory structures, generate clean visual directory trees, and extract detailed file metadata into a formatted UTF-8 report.\n\nIt runs out-of-the-box without requiring external tools, third-party dependencies, or administrative privileges.\n\n---\n\n## ✨ Features\n\n- **🌳 Visual Directory Hierarchy:** Maps folder contents using standard Unicode box-drawing characters (`├──`, `└──`, `│`) for clear structural visualization.\n- **📊 Detailed Metadata Extraction:** Captures file sizes (formatted dynamically to B, KB, MB, or GB), exact modification dates, and creation dates.\n- **📐 Dynamic Column Formatting:** Automatically calculates path lengths to keep table columns aligned and readable regardless of nested folder depth.\n- **📈 Statistical Summary:** Provides an audit summary displaying total folders scanned, total files processed, aggregate size (both human-readable and raw bytes), and execution time using high-precision timers.\n- **🌐 Full UTF-8 Encoding:** Accurately exports international filenames, Persian/Arabic characters, special symbols, and emojis without encoding corruption.\n- **🛡️ Self-Excluding Log:** Automatically ignores its own log file (`File List Log.txt`) during scanning to prevent skewed audit numbers.\n- **⚡ Zero Dependencies:** 100% native Windows script using Command Prompt and PowerShell.\n\n---\n\n## 📄 Output Preview\n\nThe generated `File List Log.txt` creates an organized tabular report similar to this:\n\n```text\n===================================================================================================\n                                DIRECTORY TREE & FILE AUDIT REPORT                                 \n===================================================================================================\n  Target Path  :  C:\\MyProject\n  Generated On :  2026-09-15 16:00:00\n===================================================================================================\n\n  PATH / TREE STRUCTURE                   SIZE         DATE MODIFIED          DATE CREATED    \n  ---------------------------------   ----------   -------------------   -------------------\n  .                                       <DIR>    2026-09-15 15:30:10   2026-09-15 15:30:10\n  ├── src/                                <DIR>    2026-09-15 15:45:22   2026-09-15 15:30:15\n  │   ├── index.js                     12.45 KB    2026-09-15 15:44:00   2026-09-15 15:31:00\n  │   └── utils.js                      4.10 KB    2026-09-15 15:40:12   2026-09-15 15:31:20\n  └── README.md                         1.85 KB    2026-09-15 15:50:00   2026-09-15 15:30:10\n  ---------------------------------   ----------   -------------------   -------------------\n\n===================================================================================================\n                                       STATISTICAL SUMMARY                                         \n===================================================================================================\n  Total Folders   :  1\n  Total Files     :  3\n  Total File Size :  18.40 KB (18,842 Bytes)\n  Execution Time  :  0.24 Seconds\n===================================================================================================\n```\n\n---\n\n## 🚀 How to Use\n\n1. Place the script file (saved with a `.bat` extension, e.g., `Export-File-List.bat`) inside the directory you want to audit.\n2. **Double-click** the script to execute it.\n3. The terminal will display real-time scan progress and terminal statistics.\n4. A report file named **`File List Log.txt`** will be generated in the same directory.\n5. The console window will automatically close after 5 seconds (or upon pressing any key).\n\n---\n\n## 💻 System Requirements\n\n- **OS:** Windows 7, Windows 8.1, Windows 10, or Windows 11.\n- **PowerShell:** Version 3.0 or later (installed by default on modern Windows).\n- **Permissions:** Standard user privileges (Administrator access is **not** required unless scanning protected system folders).\n\n---\n\n## ⚖️ Absolute Legal Disclaimer, Waiver & Limitation of Liability\n\nThis project is licensed under the **Apache License, Version 2.0**. This disclaimer expressly supplements, expands, and reinforces **Section 7 (Disclaimer of Warranty)** and **Section 8 (Limitation of Liability)** of the Apache License 2.0, and shall control to the maximum extent permitted by applicable law.\n\n**FOR EDUCATIONAL, RESEARCH, AND INFORMATIONAL PURPOSES ONLY. NO COMMERCIAL WARRANTY OR LIABILITY IS ASSUMED.**\n\n### 1. Complete Disclaimer of All Warranties\nTo the maximum extent permitted by applicable law, the Software (including all code, documentation, data, and related materials) is provided strictly on an **"AS IS"** and **"AS AVAILABLE"** basis, without any warranties or conditions of any kind, whether express, implied, statutory, customary, or otherwise. This includes, without limitation, any warranties of merchantability, fitness for a particular purpose, non-infringement, title, security, accuracy, completeness, uninterrupted or error-free operation, or freedom from viruses or other harmful components. The author(s), copyright holder(s), maintainer(s), and contributor(s) expressly disclaim all such warranties.\n\n### 2. Absolute Limitation of Liability\nUnder no circumstances and under no legal theory (whether in contract, tort — including negligence, gross negligence, and willful misconduct — strict liability, product liability, or otherwise) shall the author(s), maintainer(s), contributor(s), or copyright holder(s) be liable for any damages whatsoever, including but not limited to direct, indirect, incidental, special, consequential, exemplary, punitive, or any other damages (including loss of data, profits, revenue, business interruption, system failure, hardware damage, security breaches, personal injury, or any other loss), arising out of or related to the use, inability to use, modification, distribution, or reliance upon the Software, even if advised of the possibility of such damages and even if any remedy fails of its essential purpose.\n\n### 3. Assumption of All Risk & User Responsibility\nAny use, cloning, modification, deployment, distribution, or reliance upon this Software is undertaken entirely at the user’s sole risk and discretion. The user is exclusively and solely responsible for:\n- Ensuring full compliance with all applicable local, national, and international laws, regulations, export controls, and third-party terms;\n- Evaluating the suitability, security, and legality of the Software for any purpose;\n- Any consequences arising from its use or misuse.\n\nNothing in this repository constitutes legal, financial, cybersecurity, medical, architectural, or any other form of professional advice.\n\n### 4. Broad Indemnification\nBy accessing, downloading, cloning, forking, viewing, compiling, distributing, or using any part of this repository, you irrevocably agree to indemnify, defend, and hold harmless the author(s), contributor(s), and copyright holder(s) from and against any and all claims, demands, actions, proceedings, liabilities, damages, losses, costs, and expenses (including reasonable attorneys’ fees and legal costs) arising out of or related to your access, use, misuse, modification, distribution, or violation of this disclaimer or any applicable law.\n\n### 5. Severability & Maximum Enforceability\nIf any provision of this disclaimer is held to be unenforceable or invalid under applicable law, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed. The remaining provisions shall continue in full force and effect. This disclaimer shall be interpreted to provide the maximum protection permitted by law.\n\n### 6. No Waiver of Non-Waivable Rights\nNothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.\n',
        "fa": '# ابزار گزارش\u200cگیری ساختار درختی و متادیتای فایل\u200cها\n\nیک ابزار سبک، سریع و کاملاً بومی بر پایه ترکیب خط فرمان ویندوز (Batch) و پاورشل (PowerShell) جهت اسکن بازگشتی پوشه\u200cها، رسم سلسله\u200cمراتب درختی (Directory Tree) و استخراج متادیتای دقیق فایل\u200cها در قالب یک گزارش متنی مرتب با انکودینگ UTF-8.\n\nاین ابزار بدون نیاز به نرم\u200cافزارهای جانبی، پکیج\u200cهای اضافی یا دسترسی ادمین به صورت پیش\u200cفرض در تمام نسخه\u200cهای مدرن ویندوز اجرا می\u200cشود.\n\n---\n\n## ✨ قابلیت\u200cها و ویژگی\u200cها\n\n* 🌳 **رسم بصری سلسله\u200cمراتب پوشه\u200cها:** نمایش شاخه\u200cبندی پوشه\u200cها و فایل\u200cها با استفاده از کاراکترهای استاندارد جعبه\u200cای یونیکد (`├──`، `└──`، `│`).\n* 📊 **استخراج متادیتای دقیق:** محاسبه حجم فایل\u200cها (با تبدیل هوشمند و خوانا به B، KB، MB یا GB)، ثبت تاریخ دقیق آخرین ویرایش (Date Modified) و تاریخ ایجاد (Date Created).\n* 📐 **تراز داینامیک و هوشمند ستون\u200cها:** محاسبه خودکار طولانی\u200cترین مسیرها برای تراز نگه\u200cداشتن ستون\u200cهای جدول بدون توجه به عمق پوشه\u200cها.\n* 📈 **خلاصه آماری جامع:** شمارش دقیق تعداد پوشه\u200cها، تعداد فایل\u200cها، مجموع حجم داده\u200cها (به بایت و واحد خوانا) و زمان دقیق اجرای اسکریپت با تایمر اختصاصی.\n* 🌐 **پشتیبانی کامل از UTF-8:** ثبت صحیح نام\u200cهای فارسی، حروف غیرانگلیسی، کاراکترهای خاص و ایموجی\u200cها بدون به\u200cهم\u200cریختگی انکودینگ.\n* 🛡️ **فیلتر خودکار فایل گزارش:** نادیده گرفتن خودکار فایل خروجی (`File List Log.txt`) حین اسکن تا در محاسبات آماری تداخلی ایجاد نشود.\n* ⚡ **۱۰۰٪ بومی و سبک:** اجرا صرفاً با ابزارهای داخلی خط فرمان و پاورشل ویندوز.\n\n---\n\n## 📄 پیش\u200cنمایش خروجی\n\nفایل ایجادشده با نام `File List Log.txt` گزارشی مرتب با ساختار زیر تحویل می\u200cدهد:\n\n```text\n===================================================================================================\n                                DIRECTORY TREE & FILE AUDIT REPORT                                 \n===================================================================================================\n  Target Path  :  C:\\MyProject\n  Generated On :  2026-09-15 16:00:00\n===================================================================================================\n\n  PATH / TREE STRUCTURE                   SIZE         DATE MODIFIED          DATE CREATED    \n  ---------------------------------   ----------   -------------------   -------------------\n  .                                       <DIR>    2026-09-15 15:30:10   2026-09-15 15:30:10\n  ├── src/                                <DIR>    2026-09-15 15:45:22   2026-09-15 15:30:15\n  │   ├── index.js                     12.45 KB    2026-09-15 15:44:00   2026-09-15 15:31:00\n  │   └── utils.js                      4.10 KB    2026-09-15 15:40:12   2026-09-15 15:31:20\n  └── README.md                         1.85 KB    2026-09-15 15:50:00   2026-09-15 15:30:10\n  ---------------------------------   ----------   -------------------   -------------------\n\n===================================================================================================\n                                       STATISTICAL SUMMARY                                         \n===================================================================================================\n  Total Folders   :  1\n  Total Files     :  3\n  Total File Size :  18.40 KB (18,842 Bytes)\n  Execution Time  :  0.24 Seconds\n===================================================================================================\n```\n\n---\n\n## 🚀 راهنمای استفاده\n\n1. اسکریپت را با پسوند **`.bat`** ذخیره کنید (مثلاً `Export-File-List.bat`) و آن را درون پوشه\u200cای که قصد بررسی آن را دارید قرار دهید.\n2. روی فایل **دو بار کلیک** کنید.\n3. عملیات اسکن شروع شده و آمار لحظه\u200cای درون خط فرمان نمایش داده می\u200cشود.\n4. گزارش متنی کامل با نام **`File List Log.txt`** در همان پوشه ایجاد خواهد شد.\n5. پنجره اسکریپت پس از ۵ ثانیه به صورت خودکار بسته می\u200cشود (یا می\u200cتوانید کلیدی را برای بستن سریع\u200cتر بزنید).\n\n---\n\n## 💻 پیش\u200cنیازهای سیستم\n\n* **سیستم\u200cعامل:** ویندوز 7، 8.1، 10 یا 11.\n* **پاورشل (PowerShell):** نسخه 3.0 یا بالاتر (به\u200cصورت پیش\u200cفرض در ویندوزهای جدید فعال است).\n* **سطح دسترسی:** کاربر معمولی (نیازی به دسترسی ادمین نیست، مگر برای اسکن پوشه\u200cهای محافظت\u200cشده سیستم).\n\n---\n\n## ⚖️ سلب مسئولیت مطلق قانونی، اسقاط حق و محدودیت کامل مسئولیت\n\nاین پروژه تحت مجوز **Apache License, Version 2.0** منتشر شده است. مفاد این بخش به\u200cطور صریح در راستای تقویت، گسترش و تأکید بر **بند ۷ (سلب هرگونه ضمانت)** و **بند ۸ (محدودیت کامل مسئولیت)** لایسنس Apache 2.0 تدوین شده و تا حداکثر میزان مجاز توسط قوانین حاکم، حاکم خواهد بود.\n\n**صرفاً جهت مقاصد آموزشی، پژوهشی و اطلاع\u200cرسانی. هیچ\u200cگونه ضمانت یا مسئولیت تجاری پذیرفته نمی\u200cشود.**\n\n### ۱. سلب کامل تمام ضمانت\u200cها\nبر اساس حداکثر حدود مجاز در قوانین حاکم، نرم\u200cافزار (شامل تمام کدها، مستندات، داده\u200cها و مواد مرتبط) دقیقاً بر مبنای اصل **«همان\u200cگونه که هست» (AS IS)** و **«به\u200cشرط وجود» (AS AVAILABLE)** و بدون هیچ\u200cگونه ضمانت یا شرطی (اعم از صریح، ضمنی، قانونی، عرفی یا غیره) ارائه می\u200cشود. این شامل و نه\u200cمحدود به ضمانت قابلیت فروش تجاری، تناسب برای مقصد خاص، عدم نقض حقوق ثالث، امنیت، دقت، کامل بودن، کارکرد بدون وقفه یا بدون خطا، و عاری بودن از ویروس یا اجزای مضر است. پدیدآورنده، دارندگان حق\u200cتألیف، نگهدارندگان و مشارکت\u200cکنندگان صریحاً تمام این ضمانت\u200cها را از خود سلب می\u200cنمایند.\n\n### ۲. محدودیت مطلق مسئولیت\nتحت هیچ شرایطی و بر پایهٔ هیچ نظریهٔ حقوقی (اعم از مسئولیت قراردادی، مسئولیت مدنی یا شبه\u200cجرم — شامل قصور عادی، قصور فاحش و رفتار عمدی — مسئولیت محض، مسئولیت محصول یا غیره) پدیدآورنده، نگهدارندگان، مشارکت\u200cکنندگان یا دارندگان حق\u200cتألیف در قبال هیچ\u200cگونه خسارتی (شامل خسارات مستقیم، غیرمستقیم، اتفاقی، تبعی، خاص، تنبیهی، جزایی یا هر نوع خسارت دیگر از جمله از دست رفتن داده، سود، درآمد، وقفه در کسب\u200cوکار، خرابی سیستم، آسیب سخت\u200cافزاری، رخنه امنیتی، صدمه جانی یا هر زیان دیگر) ناشی از استفاده، عدم توانایی در استفاده، تغییر، توزیع یا اتکا به نرم\u200cافزار پاسخگو نخواهند بود؛ حتی اگر از امکان وقوع چنین خساراتی مطلع شده باشند و حتی اگر هرگونه جبران خسارت از هدف اساسی خود بازبماند.\n\n### ۳. پذیرش کامل ریسک و مسئولیت انحصاری کاربر\nهرگونه استفاده، کلون، تغییر، استقرار، توزیع یا اتکا به این نرم\u200cافزار تماماً با صلاحدید و ریسک انحصاری کاربر انجام می\u200cگیرد. کاربر به\u200cطور انحصاری و کامل مسئول است برای:\n- اطمینان از انطباق کامل با کلیه قوانین و مقررات محلی، ملی و بین\u200cالمللی، کنترل\u200cهای صادراتی و شرایط اشخاص ثالث؛\n- ارزیابی مناسب بودن، امنیت و قانونی بودن نرم\u200cافزار برای هر منظوری؛\n- تمام پیامدهای ناشی از استفاده یا سوءاستفاده از آن.\n\nهیچ بخشی از این مخزن در حکم مشاوره حقوقی، مالی، سایبری، پزشکی، معماری یا هر نوع مشاوره تخصصی دیگر محسوب نمی\u200cشود.\n\n### ۴. تعهد گسترده به جبران خسارت و مصون\u200cسازی\nهر شخص یا نهادی با دسترسی، دانلود، کلون، فورک، مشاهده، کامپایل، توزیع یا استفاده از هر بخشی از این مخزن، به\u200cطور قطعی و غیرقابل بازگشت متعهد می\u200cگردد که پدیدآورنده، مشارکت\u200cکنندگان و دارندگان حق\u200cتألیف را در برابر هرگونه ادعا، درخواست، دعوی، مسئولیت، خسارت، زیان، هزینه و مخارج (شامل حق\u200cالوکاله معقول و هزینه\u200cهای دادرسی) ناشی از دسترسی، استفاده، سوءاستفاده، تغییر، توزیع یا نقض این سلب مسئولیت یا هر قانون حاکم، کاملاً مصون نگاه داشته و کلیه خسارات را جبران نماید.\n\n### ۵. قابلیت تفکیک و حداکثر قابلیت اجرا\nاگر هر یک از مفاد این سلب مسئولیت بر اساس قوانین حاکم غیرقابل اجرا یا باطل تشخیص داده شود، آن مفاد باید به حداقل میزان لازم برای قابل اجرا شدن اصلاح شود، یا در صورت عدم امکان اصلاح، حذف گردد. سایر مفاد به قوت کامل خود باقی می\u200cمانند. این سلب مسئولیت باید به گونه\u200cای تفسیر شود که حداکثر حمایت مجاز توسط قانون را فراهم آورد.\n\n### ۶. عدم اسقاط حقوق غیرقابل اسقاط\nهیچ بخشی از این سلب مسئولیت به\u200cمنظور حذف یا محدود کردن مسئولیتی که بر اساس قوانین اجباری حاکم قابل حذف یا محدود کردن نیست (از جمله مسئولیت ناشی از مرگ یا صدمه جانی ناشی از قصور در حوزه\u200cهایی که چنین محدودیتی ممنوع است) نوشته نشده است. در چنین مواردی، مسئولیت تا حداکثر میزان مجاز توسط قانون محدود می\u200cشود.\n',
    },
    'SHA256-AUDIT': {
        "en": '# Directory Tree, Metadata & SHA-256 Auditor\n\nA high-precision, automated Windows Batch & PowerShell hybrid utility designed to recursively scan directory structures, map visual folder hierarchies, extract file metadata, and calculate cryptographic **SHA-256 hashes** for comprehensive data integrity auditing.\n\nIt outputs an organized, wide-format UTF-8 report without requiring third-party tools, external libraries, or administrator privileges.\n\n---\n\n## ✨ Features\n\n- **🔒 Cryptographic SHA-256 Hashing:** Generates a unique 64-character SHA-256 checksum for every file via native PowerShell (`Get-FileHash`) to verify data integrity and detect tampering or corruption.\n- **🛡️ Error Resilient (Access Denied Handling):** Gracefully catches locked or restricted files and tags them as `<ACCESS DENIED>` without halting the scan.\n- **🌳 Visual Directory Hierarchy:** Renders folder structures with clean Unicode box-drawing characters (`├──`, `└──`, `│`) for clear structural visualization.\n- **📊 Detailed File Metadata:** Captures human-readable file sizes (formatted dynamically to B, KB, MB, or GB), exact modification dates, and creation dates.\n- **📐 Dynamic Wide-Table Formatting:** Measures path lengths and automatically aligns columns and table borders to comfortably accommodate deep folder paths and 64-character hashes.\n- **📈 Statistical Summary:** Provides an audit summary displaying total folders scanned, total files processed, aggregate size (both human-readable and raw bytes), and execution time using high-precision timers.\n- **🌐 Full UTF-8 Encoding:** Accurately preserves international filenames, Persian/Arabic characters, special symbols, and emojis without encoding errors.\n- **🛡️ Self-Excluding Log:** Automatically ignores its own log file (`File List Log.txt`) during scanning to prevent skewed audit numbers.\n- **⚡ Zero Dependencies:** 100% native Windows script using Command Prompt and PowerShell.\n\n---\n\n## 📄 Output Preview\n\nThe generated `File List Log.txt` creates an organized tabular report similar to this:\n\n```text\n=================================================================================================================================================================\n                                                                DIRECTORY TREE & FILE AUDIT REPORT                                                               \n=================================================================================================================================================================\n  Target Path  :  C:\\MyProject\n  Generated On :  2026-09-15 16:00:00\n=================================================================================================================================================================\n\n  PATH / TREE STRUCTURE                   SIZE         DATE MODIFIED          DATE CREATED                            SHA-256 HASH                          \n  ---------------------------------   ----------   -------------------   -------------------   ----------------------------------------------------------------\n  .                                       <DIR>    2026-09-15 15:30:10   2026-09-15 15:30:10   -                                                               \n  ├── src/                                <DIR>    2026-09-15 15:45:22   2026-09-15 15:30:15   -                                                               \n  │   ├── index.js                     12.45 KB    2026-09-15 15:44:00   2026-09-15 15:31:00   A1B2C3D4E5F60718293A4B5C6D7E8F90123456789ABCDEF0123456789ABCDEF0\n  │   └── utils.js                      4.10 KB    2026-09-15 15:40:12   2026-09-15 15:31:20   E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855\n  └── README.md                         1.85 KB    2026-09-15 15:50:00   2026-09-15 15:30:10   8F434346648F6B96DF89DDAE13A4C7F7AB190A97A0DF161A92804CFD363D52A0\n  ---------------------------------   ----------   -------------------   -------------------   ----------------------------------------------------------------\n\n=================================================================================================================================================================\n                                                                       STATISTICAL SUMMARY                                                                       \n=================================================================================================================================================================\n  Total Folders   :  1\n  Total Files     :  3\n  Total File Size :  18.40 KB (18,842 Bytes)\n  Execution Time  :  0.42 Seconds\n=================================================================================================================================================================\n```\n\n---\n\n## 🚀 How to Use\n\n1. Place the script file (saved with a `.bat` extension, e.g., `Export-File-List-SHA256.bat`) inside the directory you want to audit.\n2. **Double-click** the script to execute it.\n3. The terminal will display real-time scan progress and statistics.\n4. A report file named **`File List Log.txt`** will be generated in the same directory.\n5. The console window will automatically close after 5 seconds (or upon pressing any key).\n\n---\n\n## 💻 System Requirements\n\n- **OS:** Windows 8.1, Windows 10, or Windows 11.\n- **PowerShell:** Version 4.0 or later (required for `Get-FileHash`; enabled by default on Windows 8.1, 10, and 11).\n- **Permissions:** Standard user privileges (Administrator access is **not** required unless scanning protected system folders).\n\n---\n\n## ⚖️ Absolute Legal Disclaimer, Waiver & Limitation of Liability\n\nThis project is licensed under the **Apache License, Version 2.0**. This disclaimer expressly supplements, expands, and reinforces **Section 7 (Disclaimer of Warranty)** and **Section 8 (Limitation of Liability)** of the Apache License 2.0, and shall control to the maximum extent permitted by applicable law.\n\n**FOR EDUCATIONAL, RESEARCH, AND INFORMATIONAL PURPOSES ONLY. NO COMMERCIAL WARRANTY OR LIABILITY IS ASSUMED.**\n\n### 1. Complete Disclaimer of All Warranties\nTo the maximum extent permitted by applicable law, the Software (including all code, documentation, data, and related materials) is provided strictly on an **"AS IS"** and **"AS AVAILABLE"** basis, without any warranties or conditions of any kind, whether express, implied, statutory, customary, or otherwise. This includes, without limitation, any warranties of merchantability, fitness for a particular purpose, non-infringement, title, security, accuracy, completeness, uninterrupted or error-free operation, or freedom from viruses or other harmful components. The author(s), copyright holder(s), maintainer(s), and contributor(s) expressly disclaim all such warranties.\n\n### 2. Absolute Limitation of Liability\nUnder no circumstances and under no legal theory (whether in contract, tort — including negligence, gross negligence, and willful misconduct — strict liability, product liability, or otherwise) shall the author(s), maintainer(s), contributor(s), or copyright holder(s) be liable for any damages whatsoever, including but not limited to direct, indirect, incidental, special, consequential, exemplary, punitive, or any other damages (including loss of data, profits, revenue, business interruption, system failure, hardware damage, security breaches, personal injury, or any other loss), arising out of or related to the use, inability to use, modification, distribution, or reliance upon the Software, even if advised of the possibility of such damages and even if any remedy fails of its essential purpose.\n\n### 3. Assumption of All Risk & User Responsibility\nAny use, cloning, modification, deployment, distribution, or reliance upon this Software is undertaken entirely at the user’s sole risk and discretion. The user is exclusively and solely responsible for:\n- Ensuring full compliance with all applicable local, national, and international laws, regulations, export controls, and third-party terms;\n- Evaluating the suitability, security, and legality of the Software for any purpose;\n- Any consequences arising from its use or misuse.\n\nNothing in this repository constitutes legal, financial, cybersecurity, medical, architectural, or any other form of professional advice.\n\n### 4. Broad Indemnification\nBy accessing, downloading, cloning, forking, viewing, compiling, distributing, or using any part of this repository, you irrevocably agree to indemnify, defend, and hold harmless the author(s), contributor(s), and copyright holder(s) from and against any and all claims, demands, actions, proceedings, liabilities, damages, losses, costs, and expenses (including reasonable attorneys’ fees and legal costs) arising out of or related to your access, use, misuse, modification, distribution, or violation of this disclaimer or any applicable law.\n\n### 5. Severability & Maximum Enforceability\nIf any provision of this disclaimer is held to be unenforceable or invalid under applicable law, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed. The remaining provisions shall continue in full force and effect. This disclaimer shall be interpreted to provide the maximum protection permitted by law.\n\n### 6. No Waiver of Non-Waivable Rights\nNothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.\n',
        "fa": '# ابزار بازرسی ساختار درختی، متادیتا و هش SHA-256 فایل\u200cها\n\nیک ابزار دقیق، سبک و کاملاً بومی بر پایه ترکیب خط فرمان ویندوز (Batch) و پاورشل (PowerShell) جهت اسکن بازگشتی پوشه\u200cها، رسم ساختار درختی (Directory Tree)، استخراج متادیتای فایل\u200cها و محاسبه هش رمزنگاری **SHA-256** برای هر فایل به منظور راستی\u200cآزمایی و بررسی سلامت داده\u200cها.\n\nاین ابزار گزارش عریض و تمیزی را با انکودینگ UTF-8 تولید می\u200cکند و بدون نیاز به نصب هیچ\u200cگونه نرم\u200cافزار جانبی، ماژول یا دسترسی Administrator در ویندوز اجرا می\u200cشود.\n\n---\n\n## ✨ قابلیت\u200cها و ویژگی\u200cها\n\n* 🔒 **محاسبه هش رمزنگاری SHA-256:** تولید کد هش اختصاصی ۶۴ کاراکتری برای هر فایل با دستور بومی پاورشل (`Get-FileHash`) جهت اطمینان از اصالت فایل\u200cها و تشخیص هرگونه دستکاری یا خرابی داده\u200cها.\n* 🛡️ **مدیریت خطای دسترسی فایل\u200cها:** در صورتی که فایلی قفل باشد یا دسترسی به آن محدود شده باشد، اسکریپت متوقف نشده و وضعیت آن را با برچسب `<ACCESS DENIED>` ثبت می\u200cکند.\n* 🌳 **رسم بصری سلسله\u200cمراتب پوشه\u200cها:** نمایش شاخه\u200cبندی دقیق پوشه\u200cها و فایل\u200cها با استفاده از کاراکترهای استاندارد جعبه\u200cای یونیکد (`├──`، `└──`، `│`).\n* 📊 **استخراج متادیتای کامل:** نمایش حجم فایل\u200cها (با تبدیل هوشمند و خوانا به B، KB، MB یا GB)، ثبت تاریخ آخرین ویرایش (Date Modified) و تاریخ ایجاد (Date Created).\n* 📐 **جدول\u200cبندی عریض و خودکار:** تنظیم داینامیک عرض جدول و ستون\u200cها بر اساس طولانی\u200cترین مسیر فایل\u200cها و طول ۶۴ کاراکتری هش SHA-256.\n* 📈 **خلاصه آماری جامع:** شمارش دقیق تعداد پوشه\u200cها، تعداد فایل\u200cها، مجموع حجم کل داده\u200cها (به بایت و واحد خوانا) و زمان دقیق پردازش با تایمر اختصاصی.\n* 🌐 **پشتیبانی کامل از UTF-8:** خواندن و ثبت صحیح نام فایل\u200cهای فارسی، حروف غیرانگلیسی، کاراکترهای خاص و ایموجی\u200cها بدون به\u200cهم\u200cریختگی انکودینگ.\n* 🛡️ **فیلتر خودکار فایل گزارش:** نادیده گرفتن خودکار فایل لاگ (`File List Log.txt`) حین اسکن تا در محاسبات آماری تداخلی ایجاد نشود.\n* ⚡ **۱۰۰٪ بومی و بدون وابستگی:** اجرا صرفاً با ابزارهای داخلی خط فرمان و پاورشل ویندوز.\n\n---\n\n## 📄 پیش\u200cنمایش خروجی\n\nفایل ایجادشده با نام `File List Log.txt` گزارشی منظم با ساختاری شبیه به نمونه زیر ارائه می\u200cدهد:\n\n```text\n=================================================================================================================================================================\n                                                                DIRECTORY TREE & FILE AUDIT REPORT                                                               \n=================================================================================================================================================================\n  Target Path  :  C:\\MyProject\n  Generated On :  2026-09-15 16:00:00\n=================================================================================================================================================================\n\n  PATH / TREE STRUCTURE                   SIZE         DATE MODIFIED          DATE CREATED                            SHA-256 HASH                          \n  ---------------------------------   ----------   -------------------   -------------------   ----------------------------------------------------------------\n  .                                       <DIR>    2026-09-15 15:30:10   2026-09-15 15:30:10   -                                                               \n  ├── src/                                <DIR>    2026-09-15 15:45:22   2026-09-15 15:30:15   -                                                               \n  │   ├── index.js                     12.45 KB    2026-09-15 15:44:00   2026-09-15 15:31:00   A1B2C3D4E5F60718293A4B5C6D7E8F90123456789ABCDEF0123456789ABCDEF0\n  │   └── utils.js                      4.10 KB    2026-09-15 15:40:12   2026-09-15 15:31:20   E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855\n  └── README.md                         1.85 KB    2026-09-15 15:50:00   2026-09-15 15:30:10   8F434346648F6B96DF89DDAE13A4C7F7AB190A97A0DF161A92804CFD363D52A0\n  ---------------------------------   ----------   -------------------   -------------------   ----------------------------------------------------------------\n\n=================================================================================================================================================================\n                                                                       STATISTICAL SUMMARY                                                                       \n=================================================================================================================================================================\n  Total Folders   :  1\n  Total Files     :  3\n  Total File Size :  18.40 KB (18,842 Bytes)\n  Execution Time  :  0.42 Seconds\n=================================================================================================================================================================\n```\n\n---\n\n## 🚀 راهنمای استفاده\n\n1. اسکریپت را با پسوند **`.bat`** ذخیره کنید (مثلاً `Export-File-List-SHA256.bat`) و آن را درون پوشه\u200cای که قصد بررسی آن را دارید بگذارید.\n2. روی فایل **دو بار کلیک** کنید.\n3. عملیات اسکن و محاسبه هش\u200cها شروع شده و آمار لحظه\u200cای درون خط فرمان نمایش داده می\u200cشود.\n4. فایل گزارش متنی با نام **`File List Log.txt`** در همان پوشه ساخته خواهد شد.\n5. پنجره خط فرمان پس از ۵ ثانیه به صورت خودکار بسته می\u200cشود (یا می\u200cتوانید کلیدی را برای خروج سریع\u200cتر فشار دهید).\n\n---\n\n## 💻 پیش\u200cنیازهای سیستم\n\n* **سیستم\u200cعامل:** ویندوز 8.1، ویندوز 10 یا ویندوز 11.\n* **پاورشل (PowerShell):** نسخه 4.0 یا بالاتر (برای دستور `Get-FileHash` که در ویندوزهای 8.1 به بعد پیش\u200cفرض است).\n* **سطح دسترسی:** کاربر معمولی (نیازی به دسترسی ادمین نیست، مگر برای اسکن فایل\u200cها و پوشه\u200cهای محافظت\u200cشده سیستمی).\n\n---\n\n## ⚖️ سلب مسئولیت مطلق قانونی، اسقاط حق و محدودیت کامل مسئولیت\n\nاین پروژه تحت مجوز **Apache License, Version 2.0** منتشر شده است. مفاد این بخش به\u200cطور صریح در راستای تقویت، گسترش و تأکید بر **بند ۷ (سلب هرگونه ضمانت)** و **بند ۸ (محدودیت کامل مسئولیت)** لایسنس Apache 2.0 تدوین شده و تا حداکثر میزان مجاز توسط قوانین حاکم، حاکم خواهد بود.\n\n**صرفاً جهت مقاصد آموزشی، پژوهشی و اطلاع\u200cرسانی. هیچ\u200cگونه ضمانت یا مسئولیت تجاری پذیرفته نمی\u200cشود.**\n\n### ۱. سلب کامل تمام ضمانت\u200cها\nبر اساس حداکثر حدود مجاز در قوانین حاکم، نرم\u200cافزار (شامل تمام کدها، مستندات، داده\u200cها و مواد مرتبط) دقیقاً بر مبنای اصل **«همان\u200cگونه که هست» (AS IS)** و **«به\u200cشرط وجود» (AS AVAILABLE)** و بدون هیچ\u200cگونه ضمانت یا شرطی (اعم از صریح، ضمنی، قانونی، عرفی یا غیره) ارائه می\u200cشود. این شامل و نه\u200cمحدود به ضمانت قابلیت فروش تجاری، تناسب برای مقصد خاص، عدم نقض حقوق ثالث، امنیت، دقت، کامل بودن، کارکرد بدون وقفه یا بدون خطا، و عاری بودن از ویروس یا اجزای مضر است. پدیدآورنده، دارندگان حق\u200cتألیف، نگهدارندگان و مشارکت\u200cکنندگان صریحاً تمام این ضمانت\u200cها را از خود سلب می\u200cنمایند.\n\n### ۲. محدودیت مطلق مسئولیت\nتحت هیچ شرایطی و بر پایهٔ هیچ نظریهٔ حقوقی (اعم از مسئولیت قراردادی، مسئولیت مدنی یا شبه\u200cجرم — شامل قصور عادی، قصور فاحش و رفتار عمدی — مسئولیت محض، مسئولیت محصول یا غیره) پدیدآورنده، نگهدارندگان، مشارکت\u200cکنندگان یا دارندگان حق\u200cتألیف در قبال هیچ\u200cگونه خسارتی (شامل خسارات مستقیم، غیرمستقیم، اتفاقی، تبعی، خاص، تنبیهی، جزایی یا هر نوع خسارت دیگر از جمله از دست رفتن داده، سود، درآمد، وقفه در کسب\u200cوکار، خرابی سیستم، آسیب سخت\u200cافزاری، رخنه امنیتی، صدمه جانی یا هر زیان دیگر) ناشی از استفاده، عدم توانایی در استفاده، تغییر، توزیع یا اتکا به نرم\u200cافزار پاسخگو نخواهند بود؛ حتی اگر از امکان وقوع چنین خساراتی مطلع شده باشند و حتی اگر هرگونه جبران خسارت از هدف اساسی خود بازبماند.\n\n### ۳. پذیرش کامل ریسک و مسئولیت انحصاری کاربر\nهرگونه استفاده، کلون، تغییر، استقرار، توزیع یا اتکا به این نرم\u200cافزار تماماً با صلاحدید و ریسک انحصاری کاربر انجام می\u200cگیرد. کاربر به\u200cطور انحصاری و کامل مسئول است برای:\n- اطمینان از انطباق کامل با کلیه قوانین و مقررات محلی، ملی و بین\u200cالمللی، کنترل\u200cهای صادراتی و شرایط اشخاص ثالث؛\n- ارزیابی مناسب بودن، امنیت و قانونی بودن نرم\u200cافزار برای هر منظوری؛\n- تمام پیامدهای ناشی از استفاده یا سوءاستفاده از آن.\n\nهیچ بخشی از این مخزن در حکم مشاوره حقوقی، مالی، سایبری، پزشکی، معماری یا هر نوع مشاوره تخصصی دیگر محسوب نمی\u200cشود.\n\n### ۴. تعهد گسترده به جبران خسارت و مصون\u200cسازی\nهر شخص یا نهادی با دسترسی، دانلود، کلون، فورک، مشاهده، کامپایل، توزیع یا استفاده از هر بخشی از این مخزن، به\u200cطور قطعی و غیرقابل بازگشت متعهد می\u200cگردد که پدیدآورنده، مشارکت\u200cکنندگان و دارندگان حق\u200cتألیف را در برابر هرگونه ادعا، درخواست، دعوی، مسئولیت، خسارت، زیان، هزینه و مخارج (شامل حق\u200cالوکاله معقول و هزینه\u200cهای دادرسی) ناشی از دسترسی، استفاده، سوءاستفاده، تغییر، توزیع یا نقض این سلب مسئولیت یا هر قانون حاکم، کاملاً مصون نگاه داشته و کلیه خسارات را جبران نماید.\n\n### ۵. قابلیت تفکیک و حداکثر قابلیت اجرا\nاگر هر یک از مفاد این سلب مسئولیت بر اساس قوانین حاکم غیرقابل اجرا یا باطل تشخیص داده شود، آن مفاد باید به حداقل میزان لازم برای قابل اجرا شدن اصلاح شود، یا در صورت عدم امکان اصلاح، حذف گردد. سایر مفاد به قوت کامل خود باقی می\u200cمانند. این سلب مسئولیت باید به گونه\u200cای تفسیر شود که حداکثر حمایت مجاز توسط قانون را فراهم آورد.\n\n### ۶. عدم اسقاط حقوق غیرقابل اسقاط\nهیچ بخشی از این سلب مسئولیت به\u200cمنظور حذف یا محدود کردن مسئولیتی که بر اساس قوانین اجباری حاکم قابل حذف یا محدود کردن نیست (از جمله مسئولیت ناشی از مرگ یا صدمه جانی ناشی از قصور در حوزه\u200cهایی که چنین محدودیتی ممنوع است) نوشته نشده است. در چنین مواردی، مسئولیت تا حداکثر میزان مجاز توسط قانون محدود می\u200cشود.\n',
    },
    'UNPACK': {
        "en": '# Folder Flattener & Subfolder Unpacker\n\nA fast, lightweight, and standalone Windows batch script designed to recursively extract and move all files from nested subdirectories directly into the parent (root) folder where the script is located.\n\nIt is particularly useful for cleaning up deeply nested folders from archive extractions, consolidating multi-folder downloads, or reorganizing media albums into a single directory.\n\n---\n\n## ✨ Features\n\n- **⚡ Fast & Native:** 100% pure Windows Batch (`.bat`) script with zero external dependencies, runtimes, or installations.\n- **🔄 Deep Recursive Scan:** Traverses all subdirectories (`for /r`) regardless of the nesting depth and brings all files up to the top level.\n- **🛡️ Self-Preserving:** Automatically identifies and skips the script file itself (`%~f0`), preventing it from being moved or disturbed.\n- **🎯 Root-Aware:** Ignores files that are already in the target root folder, moving only the files trapped inside subfolders.\n- **📋 Live Terminal Feedback:** Displays each filename in real-time as it is moved to the parent directory.\n- **⏳ Auto-Exit:** Automatically closes the terminal after 5 seconds upon completion (or immediately when any key is pressed).\n\n---\n\n## 🚀 How to Use\n\n1. Save the script with a `.bat` extension (e.g., `Unpack-Subfolders.bat`).\n2. Place the `.bat` file inside the **parent folder** that contains the subfolders you want to unpack.\n3. **Double-click** the script to execute it.\n4. All files from every subfolder will be moved into this parent folder.\n5. Once completed, the window will automatically close after 5 seconds.\n\n> **Tip:** Empty subfolders are left behind after files are moved, allowing you to review or delete them as needed.\n\n---\n\n## 💻 System Requirements\n\n- **Operating System:** Windows 7, Windows 8.1, Windows 10, or Windows 11.\n- **Permissions:** Standard user privileges (Administrator access is only required if files reside in protected system paths).\n\n---\n\n## ⚖️ Absolute Legal Disclaimer, Waiver & Limitation of Liability\n\nThis project is licensed under the **Apache License, Version 2.0**. This disclaimer expressly supplements, expands, and reinforces **Section 7 (Disclaimer of Warranty)** and **Section 8 (Limitation of Liability)** of the Apache License 2.0, and shall control to the maximum extent permitted by applicable law.\n\n**FOR EDUCATIONAL, RESEARCH, AND INFORMATIONAL PURPOSES ONLY. NO COMMERCIAL WARRANTY OR LIABILITY IS ASSUMED.**\n\n### 1. Complete Disclaimer of All Warranties\nTo the maximum extent permitted by applicable law, the Software (including all code, documentation, data, and related materials) is provided strictly on an **"AS IS"** and **"AS AVAILABLE"** basis, without any warranties or conditions of any kind, whether express, implied, statutory, customary, or otherwise. This includes, without limitation, any warranties of merchantability, fitness for a particular purpose, non-infringement, title, security, accuracy, completeness, uninterrupted or error-free operation, or freedom from viruses or other harmful components. The author(s), copyright holder(s), maintainer(s), and contributor(s) expressly disclaim all such warranties.\n\n### 2. Absolute Limitation of Liability\nUnder no circumstances and under no legal theory (whether in contract, tort — including negligence, gross negligence, and willful misconduct — strict liability, product liability, or otherwise) shall the author(s), maintainer(s), contributor(s), or copyright holder(s) be liable for any damages whatsoever, including but not limited to direct, indirect, incidental, special, consequential, exemplary, punitive, or any other damages (including loss of data, profits, revenue, business interruption, system failure, hardware damage, security breaches, personal injury, or any other loss), arising out of or related to the use, inability to use, modification, distribution, or reliance upon the Software, even if advised of the possibility of such damages and even if any remedy fails of its essential purpose.\n\n### 3. Assumption of All Risk & User Responsibility\nAny use, cloning, modification, deployment, distribution, or reliance upon this Software is undertaken entirely at the user’s sole risk and discretion. The user is exclusively and solely responsible for:\n- Ensuring full compliance with all applicable local, national, and international laws, regulations, export controls, and third-party terms;\n- Evaluating the suitability, security, and legality of the Software for any purpose;\n- Any consequences arising from its use or misuse.\n\nNothing in this repository constitutes legal, financial, cybersecurity, medical, architectural, or any other form of professional advice.\n\n### 4. Broad Indemnification\nBy accessing, downloading, cloning, forking, viewing, compiling, distributing, or using any part of this repository, you irrevocably agree to indemnify, defend, and hold harmless the author(s), contributor(s), and copyright holder(s) from and against any and all claims, demands, actions, proceedings, liabilities, damages, losses, costs, and expenses (including reasonable attorneys’ fees and legal costs) arising out of or related to your access, use, misuse, modification, distribution, or violation of this disclaimer or any applicable law.\n\n### 5. Severability & Maximum Enforceability\nIf any provision of this disclaimer is held to be unenforceable or invalid under applicable law, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed. The remaining provisions shall continue in full force and effect. This disclaimer shall be interpreted to provide the maximum protection permitted by law.\n\n### 6. No Waiver of Non-Waivable Rights\nNothing in this disclaimer is intended to exclude or limit any liability that cannot be excluded or limited under applicable mandatory law (including liability for death or personal injury caused by negligence in jurisdictions where such exclusion is prohibited). In such cases, liability is limited to the maximum extent permitted by law.\n',
        "fa": '# ابزار استخراج و مسطح\u200cسازی فایل\u200cها از زیرپوشه\u200cها (Folder Flattener)\n\nیک ابزار سبک، سریع و کاملاً بومی بر پایه بچ\u200cاسکریپت ویندوز (Batch Script) جهت انتقال خودکار و بازگشتی تمامی فایل\u200cها از زیرپوشه\u200cهای تودرتو به پوشه اصلی (محل قرارگیری اسکریپت).\n\nاین ابزار برای تخلیه پوشه\u200cهای تو در توی ایجادشده پس از استخراج فایل\u200cهای فشرده (ZIP یا RAR)، تجمیع دانلودهای پراکنده و سامان\u200cدهی آلبوم\u200cهای عکس و ویدیو در یک پوشه واحد فوق\u200cالعاده کاربردی است.\n\n---\n\n## ✨ قابلیت\u200cها و ویژگی\u200cها\n\n* ⚡ **۱۰۰٪ بومی و مستقل:** بدون نیاز به پایتون، پاورشل یا هرگونه نرم\u200cافزار جانبی؛ اجرا صرفاً با موتور داخلی خط فرمان ویندوز.\n* 🔄 **پیمایش عمیق و بازگشتی:** بررسی تمام لایه\u200cها و پوشه\u200cهای تودرتو بدون محدودیت در عمق ساختار پوشه\u200cها و انتقال همه فایل\u200cها به سطح اصلی.\n* 🛡️ **محافظت از فایل اسکریپت:** تشخیص هوشمند فایل خودِ اسکریپت (`%~f0`) جهت جلوگیری از جابه\u200cجایی یا تداخل در اجرای آن.\n* 🎯 **تشخیص فایل\u200cهای ریشه:** نادیده گرفتن فایل\u200cهایی که از قبل در پوشه اصلی قرار دارند و انتقال اختصاصی فایل\u200cهایی که درون زیرپوشه\u200cها گیر افتاده\u200cاند.\n* 📋 **گزارش لحظه\u200cای در کنسول:** نمایش نام هر فایل به محض جابه\u200cجا شدن در محیط ترمینال.\n* ⏳ **خروج خودکار:** بسته شدن خودکار پنجره پس از ۵ ثانیه از اتمام عملیات (یا با فشردن هر کلید کیبورد).\n\n---\n\n## 🚀 راهنمای استفاده\n\n1. اسکریپت را با پسوند **`.bat`** ذخیره کنید (مثلاً `Unpack-Subfolders.bat`).\n2. فایل را درون **پوشه اصلی** (پوشه\u200cای که زیرپوشه\u200cها داخل آن قرار دارند) کپی کنید.\n3. روی فایل اسکریپت **دو بار کلیک** کنید.\n4. تمام فایل\u200cهای موجود در زیرپوشه\u200cها به پوشه جاری منتقل می\u200cشوند.\n5. پس از مشاهده پیام اتمام عملیات، پنجره پس از ۵ ثانیه به صورت خودکار بسته می\u200cشود.\n\n> **نکته:** پس از انتقال فایل\u200cها، زیرپوشه\u200cهای خالی در جای خود باقی می\u200cمانند تا در صورت تمایل بتوانید آن\u200cها را بررسی کرده یا به سادگی حذف کنید.\n\n---\n\n## 💻 پیش\u200cنیازهای سیستم\n\n* **سیستم\u200cعامل:** ویندوز 7، 8.1، 10 یا 11.\n* **سطح دسترسی:** کاربر عادی (دسترسی Administrator تنها در صورتی نیاز است که پوشه\u200cها در مسیرهای محافظت\u200cشده سیستمی قرار داشته باشند).\n\n---\n\n## ⚖️ سلب مسئولیت مطلق قانونی، اسقاط حق و محدودیت کامل مسئولیت\n\nاین پروژه تحت مجوز **Apache License, Version 2.0** منتشر شده است. مفاد این بخش به\u200cطور صریح در راستای تقویت، گسترش و تأکید بر **بند ۷ (سلب هرگونه ضمانت)** و **بند ۸ (محدودیت کامل مسئولیت)** لایسنس Apache 2.0 تدوین شده و تا حداکثر میزان مجاز توسط قوانین حاکم، حاکم خواهد بود.\n\n**صرفاً جهت مقاصد آموزشی، پژوهشی و اطلاع\u200cرسانی. هیچ\u200cگونه ضمانت یا مسئولیت تجاری پذیرفته نمی\u200cشود.**\n\n### ۱. سلب کامل تمام ضمانت\u200cها\nبر اساس حداکثر حدود مجاز در قوانین حاکم، نرم\u200cافزار (شامل تمام کدها، مستندات، داده\u200cها و مواد مرتبط) دقیقاً بر مبنای اصل **«همان\u200cگونه که هست» (AS IS)** و **«به\u200cشرط وجود» (AS AVAILABLE)** و بدون هیچ\u200cگونه ضمانت یا شرطی (اعم از صریح، ضمنی، قانونی، عرفی یا غیره) ارائه می\u200cشود. این شامل و نه\u200cمحدود به ضمانت قابلیت فروش تجاری، تناسب برای مقصد خاص، عدم نقض حقوق ثالث، امنیت، دقت، کامل بودن، کارکرد بدون وقفه یا بدون خطا، و عاری بودن از ویروس یا اجزای مضر است. پدیدآورنده، دارندگان حق\u200cتألیف، نگهدارندگان و مشارکت\u200cکنندگان صریحاً تمام این ضمانت\u200cها را از خود سلب می\u200cنمایند.\n\n### ۲. محدودیت مطلق مسئولیت\nتحت هیچ شرایطی و بر پایهٔ هیچ نظریهٔ حقوقی (اعم از مسئولیت قراردادی، مسئولیت مدنی یا شبه\u200cجرم — شامل قصور عادی، قصور فاحش و رفتار عمدی — مسئولیت محض، مسئولیت محصول یا غیره) پدیدآورنده، نگهدارندگان، مشارکت\u200cکنندگان یا دارندگان حق\u200cتألیف در قبال هیچ\u200cگونه خسارتی (شامل خسارات مستقیم، غیرمستقیم، اتفاقی، تبعی، خاص، تنبیهی، جزایی یا هر نوع خسارت دیگر از جمله از دست رفتن داده، سود، درآمد، وقفه در کسب\u200cوکار، خرابی سیستم، آسیب سخت\u200cافزاری، رخنه امنیتی، صدمه جانی یا هر زیان دیگر) ناشی از استفاده، عدم توانایی در استفاده، تغییر، توزیع یا اتکا به نرم\u200cافزار پاسخگو نخواهند بود؛ حتی اگر از امکان وقوع چنین خساراتی مطلع شده باشند و حتی اگر هرگونه جبران خسارت از هدف اساسی خود بازبماند.\n\n### ۳. پذیرش کامل ریسک و مسئولیت انحصاری کاربر\nهرگونه استفاده، کلون، تغییر، استقرار، توزیع یا اتکا به این نرم\u200cافزار تماماً با صلاحدید و ریسک انحصاری کاربر انجام می\u200cگیرد. کاربر به\u200cطور انحصاری و کامل مسئول است برای:\n- اطمینان از انطباق کامل با کلیه قوانین و مقررات محلی، ملی و بین\u200cالمللی، کنترل\u200cهای صادراتی و شرایط اشخاص ثالث؛\n- ارزیابی مناسب بودن، امنیت و قانونی بودن نرم\u200cافزار برای هر منظوری؛\n- تمام پیامدهای ناشی از استفاده یا سوءاستفاده از آن.\n\nهیچ بخشی از این مخزن در حکم مشاوره حقوقی، مالی، سایبری، پزشکی، معماری یا هر نوع مشاوره تخصصی دیگر محسوب نمی\u200cشود.\n\n### ۴. تعهد گسترده به جبران خسارت و مصون\u200cسازی\nهر شخص یا نهادی با دسترسی، دانلود، کلون، فورک، مشاهده، کامپایل، توزیع یا استفاده از هر بخشی از این مخزن، به\u200cطور قطعی و غیرقابل بازگشت متعهد می\u200cگردد که پدیدآورنده، مشارکت\u200cکنندگان و دارندگان حق\u200cتألیف را در برابر هرگونه ادعا، درخواست، دعوی، مسئولیت، خسارت، زیان، هزینه و مخارج (شامل حق\u200cالوکاله معقول و هزینه\u200cهای دادرسی) ناشی از دسترسی، استفاده، سوءاستفاده، تغییر، توزیع یا نقض این سلب مسئولیت یا هر قانون حاکم، کاملاً مصون نگاه داشته و کلیه خسارات را جبران نماید.\n\n### ۵. قابلیت تفکیک و حداکثر قابلیت اجرا\nاگر هر یک از مفاد این سلب مسئولیت بر اساس قوانین حاکم غیرقابل اجرا یا باطل تشخیص داده شود، آن مفاد باید به حداقل میزان لازم برای قابل اجرا شدن اصلاح شود، یا در صورت عدم امکان اصلاح، حذف گردد. سایر مفاد به قوت کامل خود باقی می\u200cمانند. این سلب مسئولیت باید به گونه\u200cای تفسیر شود که حداکثر حمایت مجاز توسط قانون را فراهم آورد.\n\n### ۶. عدم اسقاط حقوق غیرقابل اسقاط\nهیچ بخشی از این سلب مسئولیت به\u200cمنظور حذف یا محدود کردن مسئولیتی که بر اساس قوانین اجباری حاکم قابل حذف یا محدود کردن نیست (از جمله مسئولیت ناشی از مرگ یا صدمه جانی ناشی از قصور در حوزه\u200cهایی که چنین محدودیتی ممنوع است) نوشته نشده است. در چنین مواردی، مسئولیت تا حداکثر میزان مجاز توسط قانون محدود می\u200cشود.\n',
    },
}

# ---------------------------------------------------------------- helpers
def resource_path(*parts):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


def load_private_fonts():
    """Load bundled Vazirmatn for this process only (no install). Windows."""
    if not IS_WIN:
        return
    FR_PRIVATE = 0x10
    for f in ("Vazirmatn-Regular.ttf", "Vazirmatn-Bold.ttf"):
        p = resource_path("fonts", f)
        if os.path.exists(p):
            try:
                ctypes.windll.gdi32.AddFontResourceExW(p, FR_PRIVATE, 0)
            except Exception:
                pass


def is_admin():
    if not IS_WIN:
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def ensure_admin():
    """Relaunch elevated via UAC if needed. Returns when admin."""
    if not IS_WIN or is_admin():
        return True
    if getattr(sys, "frozen", False):
        params = subprocess.list2cmdline(sys.argv[1:])
        fexe = sys.executable
    else:
        params = subprocess.list2cmdline(sys.argv)
        fexe = sys.executable
    try:
        rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", fexe, params, None, 1)
        if rc is not None and int(rc) <= 32:
            print("Elevation refused (code %s)." % rc)
            sys.exit(1)
    except Exception as e:
        print("Cannot elevate: %s" % e)
        sys.exit(1)
    sys.exit(0)


def stage_dir():
    base = os.environ.get("TEMP") or os.environ.get("TMP") or "."
    d = os.path.join(base, "PolarisKit-Pro")
    os.makedirs(d, exist_ok=True)
    return d


def patch_dp0(data: bytes, folder: str) -> bytes:
    try:
        enc = folder.encode("mbcs") if IS_WIN else folder.encode("utf-8")
    except Exception:
        enc = folder.encode("utf-8", "replace")
    if not enc.endswith(b"\\"):
        enc += b"\\"
    return data.replace(b"%~dp0", enc)


def decode_line(b: bytes) -> str:
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        pass
    try:
        enc = "mbcs" if IS_WIN else "utf-8"
        return b.decode(enc)
    except Exception:
        return b.decode("utf-8", "replace")


def fa_shape(s):
    if IS_WIN:
        # Windows tkinter renders through Uniscribe: native bidi + shaping.
        # Pre-shaping here would apply TWICE and scramble the text, so pass
        # logical-order text untouched on Windows.
        return s
    if HAVE_BIDI:
        try:
            return get_display(arabic_reshaper.reshape(s))
        except Exception:
            return s
    return s


def has_arabic(s):
    return any("\u0600" <= ch <= "\u06FF" for ch in s)


_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def fa_digits(s):
    return str(s).translate(_FA_DIGITS)


def fmt_size(n):
    n = float(n)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return ("%d %s" % (n, u)) if u == "B" else ("%.1f %s" % (n, u))
        n /= 1024.0
    return "%d B" % n

# ---------------------------------------------------------------- button (centering fix)
_ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F]")


class PButton(ctk.CTkButton):
    """CTkButton with pixel-accurate vertical text centering.

    Vazirmatn carries a large descent (Arabic script), so its line box
    sits high: pure-Latin text renders 2-3px above the geometric center
    (measured per size: 10->1.5, 11->2, 12->3, 13->2, 14->2.5). CTk
    lays the text out with a plain tkinter.Label inside a 5-row grid;
    we compensate after every draw with a small top grid padding
    (idempotent, no geometry feedback loop). Persian text already
    fills the line box, so it stays at 0. Image+text buttons get the
    same padding on both labels, so logo and text stay aligned.
    """

    def _pad_for(self, text):
        # measured on X11 (sizes 11-12, with/without image): +2px of top
        # grid padding puts pure-Latin glyphs exactly on the center line;
        # Persian text already fills the line box -> 0
        if not text or _ARABIC_RE.search(text):
            return 0
        return 2

    def _recenter(self):
        try:
            lbl = getattr(self, "_text_label", None)
            imgl = getattr(self, "_image_label", None)
            if lbl is None and imgl is None:
                return
            pad = self._pad_for(self._text or "")
            if lbl is not None:
                lbl.grid_configure(pady=(pad, 0))
            if imgl is not None:
                imgl.grid_configure(pady=(pad, 0))
        except Exception:
            pass

    def _draw(self, no_color_updates=False):
        super()._draw(no_color_updates)
        self._recenter()


# ---------------------------------------------------------------- markdown renderer
_MD_INLINE = re.compile(
    r"(\*\*.+?\*\*|`[^`\n]+`|\[[^\]\n]+\]\([^)\n]+\)|!\[[^\]\n]*\]\([^)\n]+\))")
_MD_LINK = re.compile(r"^\[([^\]]+)\]\(([^)]+)\)$")
_MD_IMG = re.compile(r"^!\[[^\]]*\]\([^)]+\)$")
_MD_SEP_CELL = re.compile(r"^:?-{2,}:?$")


def _md_strip_inline(s):
    return s.replace("**", "").replace("`", "")


def _md_insert_inline(inner, text, base, on_link):
    for frag in _MD_INLINE.split(text):
        if not frag:
            continue
        if frag.startswith("**") and frag.endswith("**") and len(frag) > 4:
            _md_insert_inline(inner, frag[2:-2], base + ("md_b",), on_link)
            continue
        if frag.startswith("`") and frag.endswith("`") and len(frag) > 2:
            inner.insert("end", frag[1:-1], base + ("md_c",))
            continue
        if _MD_IMG.match(frag):
            continue  # images/badges: nothing to render in-app
        m = _MD_LINK.match(frag)
        if m:
            start = inner.index("end-1c")
            inner.insert("end", m.group(1), base)
            end = inner.index("end-1c")
            tagn = "md_link_%s" % start
            inner.tag_configure(tagn, foreground="#22d3ee", underline=True)
            inner.tag_add(tagn, start, end)
            inner.tag_bind(tagn, "<Button-1>", lambda e, u=m.group(2): on_link(u))
            inner.tag_bind(tagn, "<Enter>", lambda e: inner.configure(cursor="hand2"))
            inner.tag_bind(tagn, "<Leave>", lambda e: inner.configure(cursor=""))
            continue
        inner.insert("end", frag, base)


def render_markdown(inner, doc, rtl, on_link):
    """Render GitHub-flavored markdown into a tkinter Text widget (tags)."""
    F, M = UI_FONT, MONO_FONT
    cfg = {
        "md_h1": (F, 15, "bold", CYAN, 0, 14, 14, 14, 10),
        "md_h2": (F, 13, "bold", "#4ade80", 0, 14, 14, 10, 6),
        "md_h3": (F, 11, "bold", "#7dd3fc", 0, 14, 14, 8, 4),
        "md_p":  (F, 11, "", TXT, 0, 14, 14, 3, 6),
        "md_ul": (F, 11, "", TXT, 0, 30, 30, 2, 3),
        "md_ol": (F, 11, "", TXT, 0, 32, 32, 2, 3),
        "md_cb": (M, 10, "", "#9cc4ff", "#0a1526", 16, 16, 6, 6),
        "md_th": (M, 10, "bold", "#67e8f9", "#132741", 16, 16, 4, 4),
        "md_td0": (M, 10, "", "#c9d6ea", "#0e1c31", 16, 16, 0, 0),
        "md_td1": (M, 10, "", "#c9d6ea", "#0b1526", 16, 16, 0, 0),
        "md_hr": (M, 10, "", "#22334f", 0, 14, 14, 8, 8),
        "md_q":  (F, 11, "", "#8b98ab", 0, 22, 22, 4, 6),
    }
    for t, (fam, sz, wt, fg, bg, lm1, lm2, s1, s3) in cfg.items():
        opts = dict(font=(fam, sz) + ((wt,) if wt else ()),
                    foreground=fg, lmargin1=lm1, lmargin2=lm2,
                    spacing1=s1, spacing3=s3)
        if bg:
            opts["background"] = bg
        inner.tag_configure(t, **opts)
    inner.tag_configure("md_b", font=(F, 11, "bold"), foreground="#eef6ff")
    inner.tag_configure("md_c", font=(M, 10), foreground="#fbbf24",
                        background="#1d2b47")
    if rtl:
        for t in ("md_h1", "md_h2", "md_h3", "md_p", "md_ul", "md_ol", "md_q",
                  "md_th", "md_td0", "md_td1"):
            inner.tag_configure(t, justify="right")

    # shape line-by-line (AFTER parsing) so structural markers (#, |, -)
    # are still detected in logical order; code blocks stay untouched
    sh = fa_shape if rtl else (lambda s: s)
    lines = doc.split("\n")
    i, n = 0, len(lines)
    last_hr = False
    para_buf = []

    def flush_para():
        nonlocal last_hr
        if not para_buf:
            return
        for j, p in enumerate(para_buf):
            _md_insert_inline(inner, sh(p), ("md_p",), on_link)
            inner.insert("end", "\n", ("md_p",))
        para_buf.clear()

    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        s = line.strip()

        # fenced code block
        if s.startswith("```"):
            flush_para()
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                inner.insert("end", lines[i].rstrip() + "\n", ("md_cb",))
                i += 1
            i += 1  # closing fence (or EOF)
            last_hr = False
            continue

        # table block
        if s.startswith("|") and s.count("|") >= 2:
            flush_para()
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            rows = [r for r in rows
                    if not all(_MD_SEP_CELL.match(c or "-") for c in r)]
            if rows:
                widths = []
                if not rtl:
                    for ci in range(max(len(r) for r in rows)):
                        wmax = max(len(_md_strip_inline(r[ci]))
                                   for r in rows if ci < len(r))
                        widths.append(min(wmax, 34))
                for ri, r in enumerate(rows):
                    tag = "md_th" if ri == 0 else ("md_td0" if ri % 2 == 1 else "md_td1")
                    if rtl:
                        celltxt = "    |    ".join(sh(_md_strip_inline(c)) for c in r)
                        inner.insert("end", celltxt + "\n", (tag,))
                    else:
                        cells = []
                        for ci, c in enumerate(r):
                            cw = widths[ci] if ci < len(widths) else max(len(c), 8)
                            cells.append(_md_strip_inline(c)[:cw].ljust(cw))
                        inner.insert("end", "  " + "   ".join(cells) + "\n", (tag,))
                last_hr = False
            continue

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            flush_para()
            lvl = min(len(m.group(1)), 3)
            _md_insert_inline(inner, sh(m.group(2)), ("md_h%d" % lvl,), on_link)
            inner.insert("end", "\n", ("md_h%d" % lvl,))
            last_hr = False
            i += 1
            continue

        # horizontal rule
        if re.match(r"^-{3,}$", s) or re.match(r"^\*{3,}$", s):
            flush_para()
            if not last_hr:
                inner.insert("end", "─" * 88 + "\n", ("md_hr",))
                last_hr = True
            i += 1
            continue
        last_hr = False

        # blockquote
        if s.startswith(">"):
            flush_para()
            body_q = sh(s.lstrip("> ").strip())
            if body_q:
                _md_insert_inline(inner,
                                  ("│  " if not rtl else "") + body_q +
                                  ("" if not rtl else "  │"),
                                  ("md_q",), on_link)
                inner.insert("end", "\n", ("md_q",))
            i += 1
            continue

        # unordered list
        m = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if m:
            flush_para()
            depth = 1 if len(m.group(1)) < 3 else 2
            item = sh(m.group(2).strip())
            if rtl:
                item = item + "  •"
            else:
                item = "•   " + item
            tag = "md_ul" if depth == 1 else "md_p"
            if depth == 2:
                inner.tag_configure("md_ul2", font=(F, 11), foreground=TXT,
                                    lmargin1=48, lmargin2=48, spacing3=2)
                tag = "md_ul2"
            _md_insert_inline(inner, item, (tag,), on_link)
            inner.insert("end", "\n", (tag,))
            i += 1
            continue

        # ordered list
        m = re.match(r"^(\s*)(\d+)[.)]\s+(.*)$", line)
        if m:
            flush_para()
            num = m.group(2)
            item = sh(m.group(3).strip())
            if rtl:
                item = item + "  " + fa_digits(num) + "."
            else:
                item = num + ".   " + item
            _md_insert_inline(inner, item, ("md_ol",), on_link)
            inner.insert("end", "\n", ("md_ol",))
            i += 1
            continue

        # blank
        if not s:
            i += 1
            continue

        # plain paragraph line (collect consecutive)
        para_buf.append(s)
        i += 1

    flush_para()


# ---------------------------------------------------------------- app
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PolarisKit-Pro")
        self.geometry("1220x820")
        self.minsize(1020, 680)
        self.configure(fg_color=BG)
        if IS_WIN:
            # same icon in titlebar + taskbar as the exe file carries
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    "PolarisVoid.CyberToolkit.Pro")
            except Exception:
                pass
        try:
            ico = resource_path("icon.ico")
            if os.path.exists(ico):
                self.iconbitmap(ico)
        except Exception:
            pass
        try:
            png = resource_path("icon.png")
            if os.path.exists(png):
                self._iconph = PhotoImage(file=png)
                self.iconphoto(True, self._iconph)
        except Exception:
            pass

        self.lang = "en"
        self.readme_lang = "en"      # in-app readme viewer language (toggle)
        self.mod = 0
        self.folder = ""
        self.busy = False
        self.logq = queue.Queue()
        self.admin = is_admin()
        self.current_proc = None
        self.confirm_answer = None
        self.stop_event = threading.Event()
        self.was_stopped = False     # full UI refresh after STOP
        self.vault_win = None

        # ---- header
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=16, pady=(10, 0))
        self.lbl_title = ctk.CTkLabel(head, text="POLARIS-VOID CYBER TOOLKIT",
                                      font=(UI_FONT, 20, "bold"), text_color=CYAN)
        self.lbl_title.pack(side="left")
        self.btn_lang = PButton(head, text="", width=70,
                                      font=(UI_FONT, 12, "bold"),
                                      fg_color="#22c55e", hover_color="#16a34a",
                                      text_color="#03130a",
                                      command=self.toggle_lang)
        self.btn_lang.pack(side="right", padx=(8, 0))
        try:
            from PIL import Image as _PILImage
            _gh = _PILImage.open(resource_path("gh.png")).convert("RGBA")
            self.gh_img = ctk.CTkImage(light_image=_gh, dark_image=_gh,
                                       size=(16, 16))
        except Exception:
            self.gh_img = None
        self.btn_gh = PButton(head, text="", width=150,
                                    font=(UI_FONT, 12, "bold"),
                                    fg_color="#f2f5f9", hover_color="#cdd6e4",
                                    text_color="#0b0e14", image=self.gh_img,
                                    compound="left",
                                    command=lambda: self.open_link(GITHUB))
        self.btn_gh.pack(side="right")
        sub = ctk.CTkFrame(self, fg_color="transparent")
        sub.pack(fill="x", padx=16, pady=(2, 0))
        self.lbl_sub = ctk.CTkLabel(sub, text="", font=(UI_FONT, 11), text_color=GRAY)
        self.lbl_sub.pack(side="left", fill="x", expand=True)
        div = ctk.CTkFrame(self, fg_color=BORDER, height=1)
        div.pack(fill="x", padx=16, pady=(8, 0))

        # ---- body
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=8)
        side = ctk.CTkFrame(body, fg_color=PANEL, width=264, corner_radius=6)
        side.pack(side="left", fill="y", padx=(0, 10))
        side.pack_propagate(False)
        self.lbl_mods = ctk.CTkLabel(side, text="", font=(UI_FONT, 12, "bold"),
                                     text_color=MAGENTA, anchor="w")
        self.lbl_mods.pack(fill="x", padx=10, pady=(8, 4))
        self.side_btns = []
        for i, m in enumerate(MODULES):
            b = PButton(side, text="%02d  %s" % (i + 1, m.title),
                              anchor="w", font=(UI_FONT, 12, "bold"),
                              fg_color="transparent", text_color=CYAN,
                              hover_color=CARD, height=32,
                              command=lambda i=i: self.select(i))
            b.pack(fill="x", padx=8, pady=2)
            self.side_btns.append(b)

        main = ctk.CTkFrame(body, fg_color="transparent")
        main.pack(side="left", fill="both", expand=True)
        trow = ctk.CTkFrame(main, fg_color="transparent")
        trow.pack(fill="x")
        self.lbl_mtitle = ctk.CTkLabel(trow, text="", font=(UI_FONT, 14, "bold"),
                                       text_color="#ebfaff", anchor="w")
        self.lbl_mtitle.pack(side="left", fill="x", expand=True)
        self.btn_open = PButton(trow, text="", width=160, height=30,
                                      font=(UI_FONT, 12, "bold"),
                                      fg_color="#eab308", hover_color="#ca8a04",
                                      text_color="#1a1405",
                                      command=self.open_current)
        self.btn_open.pack(side="right")
        self.lbl_meta = ctk.CTkLabel(main, text="", font=(MONO_FONT, 10),
                                     text_color=AMBER, anchor="w")
        self.lbl_meta.pack(fill="x", pady=(0, 6))
        drow = ctk.CTkFrame(main, fg_color="transparent")
        drow.pack(fill="x", pady=(0, 6))
        self.btn_readme = PButton(drow, text="", width=180, height=26,
                                        font=(UI_FONT, 11, "bold"),
                                        fg_color="transparent", border_width=1,
                                        border_color=GREEN, text_color=GREEN,
                                        command=self.toggle_readme)
        self.btn_readme.pack(side="left")
        self.txt_desc = ctk.CTkTextbox(main, font=(UI_FONT, 11), text_color=TXT,
                                       fg_color=PANEL, border_width=1,
                                       border_color=BORDER, wrap="word")
        self.txt_desc.pack(fill="both", expand=True)
        try:
            self.txt_desc._textbox.configure(padx=10, pady=8)
        except Exception:
            pass
        self.txt_desc.configure(state="disabled")

        frow = ctk.CTkFrame(main, fg_color="transparent")
        frow.pack(fill="x", pady=(8, 0))
        self.lbl_target = ctk.CTkLabel(frow, text="", font=(UI_FONT, 12), text_color=GRAY)
        self.lbl_target.pack(side="left", padx=(0, 8))
        self.ent_path = ctk.CTkEntry(frow, font=(MONO_FONT, 11), text_color=CYAN,
                                     fg_color=CARD, border_width=1,
                                     border_color=BORDER, state="disabled",
                                     justify="left")
        self.ent_path.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.btn_browse = PButton(frow, text="", width=110,
                                        font=(UI_FONT, 12, "bold"),
                                        fg_color="transparent", border_width=1,
                                        border_color=CYAN, text_color=CYAN,
                                        command=self.pick_folder)
        self.btn_browse.pack(side="left")
        self.frow = frow

        arow = ctk.CTkFrame(main, fg_color="transparent")
        arow.pack(fill="x", pady=8)
        self.arow = arow
        self.act_btns = []
        for i in range(3):
            b = PButton(arow, text="...", font=(UI_FONT, 12, "bold"),
                              fg_color=CARD, text_color="#b9f5ff",
                              border_width=1, border_color=CYAN, height=36,
                              command=lambda i=i: self.run_action(i))
            b.pack(side="left", fill="x", expand=True, padx=(0, 8) if i < 2 else (0, 0))
            self.act_btns.append(b)

        # ---- console
        clog = ctk.CTkFrame(self, fg_color="transparent")
        clog.pack(fill="x", padx=16)
        self.btn_stop = PButton(clog, text="", width=110, height=24,
                                      font=(UI_FONT, 11, "bold"),
                                      fg_color="#dc2626", hover_color="#b91c1c",
                                      text_color="white",
                                      command=self.stop_current, state="disabled")
        self.btn_clear = PButton(clog, text="", width=110, height=24,
                                       font=(UI_FONT, 11, "bold"),
                                       fg_color="#dc2626", hover_color="#b91c1c",
                                       text_color="white",
                                       command=self.clear_log)
        self.btn_export = PButton(clog, text="", width=110, height=24,
                                        font=(UI_FONT, 11, "bold"),
                                        fg_color="#22c55e", hover_color="#16a34a",
                                        text_color="#03130a",
                                        command=self.export_log)
        self.btn_export.pack(side="right")
        self.btn_clear.pack(side="right", padx=(0, 8))
        self.btn_stop.pack(side="right", padx=(0, 8))
        self.lbl_cl = ctk.CTkLabel(clog, text="", font=(UI_FONT, 12, "bold"),
                                   text_color=GREEN)
        self.lbl_cl.pack(side="left", fill="x", expand=True, padx=(0, 24))
        self.txt_log = ctk.CTkTextbox(self, height=168, font=(MONO_FONT, 11),
                                      text_color=GREEN, fg_color="#020408",
                                      border_width=1, border_color=BORDER,
                                      wrap="word")
        self.txt_log.pack(fill="x", padx=16, pady=(2, 0))
        try:
            self.txt_log._textbox.configure(padx=10, pady=6)
        except Exception:
            pass
        self.txt_log.configure(state="disabled")

        self.status_state = "ready"  # headless run state (no visible bar)

        self.apply_lang()
        self.select(0, silent=True)
        self.boot_log()
        self.after(100, self.pump_log)
        self.type_queue = []
        self.after(15, self.pump_type)

    # ------------------------------------------------------------ i18n
    def T(self, key):
        s = STR[key][self.lang]
        return fa_shape(s) if has_arabic(s) else s

    def toggle_lang(self):
        self.lang = "fa" if self.lang == "en" else "en"
        self.readme_lang = self.lang  # readme follows the UI language
        self.apply_lang()
        self.select(self.mod, silent=True)

    def apply_lang(self):
        fa = (self.lang == "fa")
        edge = "e" if fa else "w"
        self.lbl_sub.configure(text=self.T("subtitle"), anchor=edge)
        n = fa_digits(len(MODULES)) if fa else len(MODULES)
        raw_mods = "%s · %s" % (STR["modules"][self.lang], n)
        self.lbl_mods.configure(
            text=fa_shape(raw_mods) if has_arabic(raw_mods) else raw_mods,
            anchor=edge)
        self.btn_open.configure(text=self.T("open_project"))
        self.lbl_target.configure(text=self.T("target"))
        self.btn_browse.configure(text=self.T("browse"))
        self.lbl_cl.configure(text=self.T("console"), anchor="w")
        self.btn_export.configure(text=self.T("export"))
        self.btn_clear.configure(text=self.T("clear"))
        self.btn_stop.configure(text=self.T("stop"))
        self.btn_gh.configure(text=self.T("github"))
        self.btn_lang.configure(text=self.T("lang"))
        self.update_status_state()
        if self.vault_win is not None and self.vault_win.winfo_exists():
            self.refresh_vault_texts()
        if not self.folder:
            self.ent_path.configure(state="normal")
            self.ent_path.delete(0, "end")
            self.ent_path.insert(0, self.T("notarget"))
            self.ent_path.configure(state="disabled")

    # ------------------------------------------------------------ nav
    def update_status_state(self):
        m = MODULES[self.mod]
        if self.lang == "fa":
            s = "%s %s %s %s · %s" % (
                STR["st_module"]["fa"], fa_digits("%02d" % (self.mod + 1)),
                STR["st_of"]["fa"], fa_digits(len(MODULES)), m.mid)
            s = fa_shape(s)
        else:
            s = "module %02d of %02d · %s" % (self.mod + 1, len(MODULES), m.mid)
        if self.folder:
            s = "%s  |  %s: " % (s, self.T("st_target")) + os.path.basename(self.folder.rstrip("\\/"))
        self.status_state = s

    def select(self, i, silent=False):
        self.mod = i
        m = MODULES[i]
        for k, b in enumerate(self.side_btns):
            if k == i:
                b.configure(fg_color=CYAN, text_color="#04080e", hover=False)
            else:
                b.configure(fg_color="transparent", text_color=CYAN, hover=True)
        self.lbl_mtitle.configure(text="%02d · %s" % (i + 1, m.title))
        tech = m.tech if self.lang == "en" else TECH_FA.get(m.mid, m.tech)
        if self.lang == "fa":
            self.lbl_meta.configure(text=fa_shape("%s · %s" % (m.cat, tech)))
        else:
            self.lbl_meta.configure(text="%s · %s" % (m.cat, tech))
        self.show_readme()

        need = any(a.need_folder for a in m.acts)
        if need:
            self.frow.pack(fill="x", pady=(8, 0), before=self.arow)
        else:
            self.frow.pack_forget()
        for k in range(3):
            if k < len(m.acts):
                a = m.acts[k]
                if self.lang == "fa":
                    alabel = fa_shape(ACT_FA.get(a.label, a.label))
                else:
                    alabel = a.label
                self.act_btns[k].configure(
                    text=alabel,
                    border_color=MAGENTA if a.admin else CYAN,
                    state="normal")
                self.act_btns[k].pack(side="left", fill="x", expand=True,
                                      padx=(0, 8) if k < len(m.acts) - 1 else (0, 0))
            else:
                self.act_btns[k].pack_forget()
        self.update_status_state()
        if not silent:
            self.log("[NAV] module %02d of %02d · %s" % (i + 1, len(MODULES), m.mid))

    # ------------------------------------------------------------ readme viewer
    def show_readme(self):
        m = MODULES[self.mod]
        rtl = (self.readme_lang == "fa")
        body = READMES.get(m.mid, {}).get(self.readme_lang) or m.en
        doc = "# " + m.title + "\n\n" + body
        tb = self.txt_desc
        try:
            inner = tb._textbox
            tb.configure(state="normal")
            inner.delete("1.0", "end")
            render_markdown(inner, doc, rtl, self.open_link)
            inner.yview_moveto(0.0)
            tb.configure(state="disabled")
        except Exception:
            tb.configure(state="normal")
            tb.delete("1.0", "end")
            tb.insert("end", doc)
            tb.configure(state="disabled")
        self.btn_readme.configure(
            text=self.T("readme2en") if rtl else self.T("readme2fa"))

    def toggle_readme(self):
        self.readme_lang = "fa" if self.readme_lang == "en" else "en"
        self.show_readme()

    def open_current(self):
        self.open_link(MODULES[self.mod].url)

    def pick_folder(self):
        d = filedialog.askdirectory(title="Select TARGET folder (USB root for immunizer)")
        if not d:
            self.log("[SKIP] picker cancelled.")
            return
        self.folder = d
        self.ent_path.configure(state="normal")
        self.ent_path.delete(0, "end")
        self.ent_path.insert(0, d)
        self.ent_path.configure(state="disabled")
        self.update_status_state()
        self.log("[ OK ] target locked :: %s" % d)

    def open_link(self, url):
        try:
            webbrowser.open(url)
            self.log("[ OK ] browser launched :: %s" % url)
            self.status_state = "browser launched"
        except Exception as e:
            self.log("[ERR ] cannot open browser (%s) :: %s" % (e, url))

    def _apply_icon(self, w):
        try:
            ico = resource_path("icon.ico")
            if os.path.exists(ico):
                w.iconbitmap(ico)
        except Exception:
            pass
        try:
            if getattr(self, "_iconph", None) is not None:
                w.iconphoto(True, self._iconph)
        except Exception:
            pass

    def clear_log(self):
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.configure(state="disabled")
        self.log("[SYS] log purged.")

    def export_log(self):
        try:
            data = self.txt_log.get("1.0", "end-1c")
        except Exception as e:
            self.log("[ERR ] export failed (%s)" % e)
            return
        try:
            if getattr(sys, "frozen", False):
                base = os.path.dirname(os.path.abspath(sys.executable))
            else:
                base = os.getcwd()
            name = "PolarisKit-log-%s.txt" % time.strftime("%Y%m%d-%H%M%S")
            path = os.path.join(base, name)
            with open(path, "w", encoding="utf-8") as f:
                f.write("POLARIS-VOID CYBER TOOLKIT [PRO] :: log export %s\n\n"
                        % time.strftime("%Y-%m-%d %H:%M:%S"))
                f.write(data)
            self.log("[ OK ] log exported :: %s (%d bytes)"
                     % (path, len(data.encode("utf-8"))))
        except Exception as e:
            self.log("[ERR ] export failed (%s)" % e)

    def stop_current(self):
        if not self.busy:
            return
        self.stop_event.set()
        self.was_stopped = True
        p = self.current_proc
        if p is not None and p.poll() is None:
            try:
                if IS_WIN:
                    # kill the whole tree: children (robocopy, dism, ...)
                    # inherit the pipes and would freeze the stream reader
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(p.pid)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=0x08000000, timeout=10)
                else:
                    p.kill()
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass
            self.log("[WARN] stop requested - terminating process tree...")
        else:
            self.log("[WARN] stop requested - aborting before dispatch...")

    # ------------------------------------------------------------ vault (in-app)
    def open_vault(self, raw_path):
        path = os.path.expandvars(raw_path)
        if self.vault_win is not None and self.vault_win.winfo_exists():
            self.vault_win.lift()
            self.vault_path = path
            self.fill_vault()
            return
        self.vault_path = path
        w = ctk.CTkToplevel(self)
        w.title(self.T("vault_title"))
        self._apply_icon(w)
        try:
            cx = self.winfo_x() + max(0, (self.winfo_width() - 640) // 2)
            cy = self.winfo_y() + max(0, (self.winfo_height() - 480) // 2)
            w.geometry("640x480+%d+%d" % (cx, cy))
        except Exception:
            w.geometry("640x480")
        w.configure(fg_color=BG)
        try:
            w.transient(self)
        except Exception:
            pass
        self.vault_win = w
        self.lbl_vt = ctk.CTkLabel(w, text="", font=(UI_FONT, 14, "bold"), text_color=CYAN)
        self.lbl_vt.pack(fill="x", padx=12, pady=(10, 2))
        self.lbl_vp = ctk.CTkLabel(w, text="", font=(MONO_FONT, 11), text_color=AMBER,
                                   anchor="w", justify="left")
        self.lbl_vp.pack(fill="x", padx=12)
        self.txt_vault = ctk.CTkTextbox(w, font=(MONO_FONT, 11), text_color=TXT,
                                        fg_color=PANEL, border_width=1,
                                        border_color=BORDER, wrap="none")
        self.txt_vault.pack(fill="both", expand=True, padx=12, pady=8)
        self.txt_vault.configure(state="disabled")
        brow = ctk.CTkFrame(w, fg_color="transparent")
        brow.pack(fill="x", padx=12, pady=(0, 12))
        self.btn_vcopy = PButton(brow, text="", font=(UI_FONT, 11, "bold"),
                                       fg_color="transparent", border_width=1,
                                       border_color=CYAN, text_color=CYAN,
                                       command=self.copy_vault_path)
        self.btn_vcopy.pack(side="left", padx=(0, 8))
        self.btn_vref = PButton(brow, text="", font=(UI_FONT, 11, "bold"),
                                      fg_color="transparent", border_width=1,
                                      border_color=CYAN, text_color=CYAN,
                                      command=self.fill_vault)
        self.btn_vref.pack(side="left", padx=(0, 8))
        self.btn_vclose = PButton(brow, text="", font=(UI_FONT, 11, "bold"),
                                        fg_color="transparent", border_width=1,
                                        border_color=MAGENTA, text_color=MAGENTA,
                                        command=w.destroy)
        self.btn_vclose.pack(side="right")
        self.refresh_vault_texts()
        self.fill_vault()
        self.log("[ OK ] vault inspector opened (in-app).")

    def refresh_vault_texts(self):
        fa = (self.lang == "fa")
        try:
            self.lbl_vt.configure(text=self.T("vault_title"), anchor="e" if fa else "w")
            self.btn_vcopy.configure(text=self.T("vault_copy"))
            self.btn_vref.configure(text=self.T("vault_refresh"))
            self.btn_vclose.configure(text=self.T("vault_close"))
        except Exception:
            pass

    def copy_vault_path(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.vault_path)
            self.update()
            self.log("[ OK ] vault path copied :: %s" % self.vault_path)
        except Exception as e:
            self.log("[WARN] clipboard failed (%s)" % e)

    def fill_vault(self):
        p = self.vault_path
        try:
            self.lbl_vp.configure(text=p)
        except Exception:
            pass
        lines = []
        if not os.path.isdir(p):
            lines.append("(vault not found yet - run BACKUP first)")
            self.log("[WARN] vault missing :: %s" % p)
        else:
            try:
                entries = sorted(os.scandir(p), key=lambda e: e.name.lower())
            except Exception as e:
                entries = []
                lines.append("(cannot read vault: %s)" % e)
            total = 0
            files = [e for e in entries if e.is_file()]
            dirs = [e for e in entries if e.is_dir()]
            for e in entries:
                try:
                    sz = e.stat().st_size if e.is_file() else 0
                except OSError:
                    sz = 0
                total += sz
            lines.append("%d files, %d folders :: %s total" % (len(files), len(dirs), fmt_size(total)))
            lines.append("-" * 56)
            shown = 0
            for e in dirs:
                lines.append("[DIR ] %s" % e.name)
                shown += 1
            for e in files[:200]:
                try:
                    sz = e.stat().st_size
                except OSError:
                    sz = 0
                lines.append("%-7s %s" % (fmt_size(sz), e.name))
                shown += 1
            if len(files) > 200:
                lines.append("... and %d more" % (len(files) - 200))
            if not entries:
                lines.append("(empty)")
            self.log("[ OK ] vault scanned :: %s (%d entries)" % (p, len(entries)))
        try:
            self.txt_vault.configure(state="normal")
            self.txt_vault.delete("1.0", "end")
            self.txt_vault.insert("end", "\n".join(lines))
            self.txt_vault.configure(state="disabled")
        except Exception:
            pass

    # ------------------------------------------------------------ log
    def log(self, msg):
        ts = time.strftime("[%H:%M:%S] ")
        try:
            self.txt_log.configure(state="normal")
            if len(self.txt_log.get("1.0", "end")) > 80000:
                self.txt_log.delete("1.0", "5000c")
            self.txt_log.insert("end", ts + msg + "\n")
            self.txt_log.see("end")
            self.txt_log.configure(state="disabled")
        except Exception:
            pass

    def pump_log(self):
        try:
            while True:
                kind, msg = self.logq.get_nowait()
                if kind == "type":
                    self.type_queue.append(msg)
                elif kind == "state":
                    self.status_state = msg
                elif kind == "done":
                    self.busy = False
                    self.current_proc = None
                    if self.was_stopped:
                        self.was_stopped = False
                        self.select(self.mod, silent=True)
                        self.refresh_buttons()
                        self.log("[SYS] interface refreshed.")
                    else:
                        self.refresh_buttons()
                else:
                    self.log(msg)
        except queue.Empty:
            pass
        self.after(100, self.pump_log)

    def pump_type(self):
        if self.type_queue:
            msg = self.type_queue.pop(0)
            ts = time.strftime("[%H:%M:%S] ")
            try:
                self.txt_log.configure(state="normal")
                self.txt_log.insert("end", ts)
                for i in range(0, len(msg), 3):
                    self.txt_log.insert("end", msg[i:i + 3])
                    self.txt_log.see("end")
                    self.txt_log.update_idletasks()
                self.txt_log.insert("end", "\n")
                self.txt_log.see("end")
                self.txt_log.configure(state="disabled")
            except Exception:
                pass
        self.after(15, self.pump_type)

    def boot_log(self):
        total = 0
        seen = set()
        for m in MODULES:
            for a in m.acts:
                if a.resid and a.resid not in seen:
                    seen.add(a.resid)
                    _, raw = get_payload(a.resid)
                    total += len(raw)
        _, ico = get_payload("USB_ICO")
        total += len(ico)
        self.log("=" * 64)
        self.log("POLARIS-VOID CYBER TOOLKIT  [PRO EDITION v1.5]")
        self.log("%d modules loaded :: payload vault %d bytes, byte-exact" % (len(MODULES), total))
        self.log("neural link: ESTABLISHED :: thinking mode: ON :: bidi: %s"
                 % ("ON" if HAVE_BIDI else "OFF"))
        self.log("session: %s :: popups: ZERO (all output streams here)"
                 % ("ELEVATED ADMIN" if self.admin else "STANDARD (dev)"))
        self.log("font: Vazirmatn :: layout: RTL/FA + LTR/EN per paragraph")
        self.log("staging bay :: %s" % stage_dir())
        self.log("=" * 64)
        self.log("[TIP] pick a module, optionally lock a target folder, hit an action.")
        self.log("[TIP] each module ships its full GitHub README (EN/FA) + OPEN PROJECT button.")
        self.log("[TIP] STOP kills a running tool. EXPORT saves this log next to the app.")



    def refresh_buttons(self):
        st = "disabled" if self.busy else "normal"
        for k in range(len(MODULES[self.mod].acts)):
            try:
                self.act_btns[k].configure(state=st)
            except Exception:
                pass
        try:
            self.btn_browse.configure(state=st)
            self.btn_stop.configure(state="normal" if self.busy else "disabled")
        except Exception:
            pass

    # ------------------------------------------------------------ confirm
    def ask_confirm(self, key):
        """In-app modal confirm (no system popups). True = user pressed YES."""
        result = {"ok": False}
        w = ctk.CTkToplevel(self)
        w.title(self.T("confirm_title"))
        self._apply_icon(w)
        w.configure(fg_color=BG)
        w.resizable(False, False)
        try:
            w.transient(self)
            cx = self.winfo_x() + max(0, (self.winfo_width() - 520) // 2)
            cy = self.winfo_y() + max(0, (self.winfo_height() - 230) // 2)
            w.geometry("520x230+%d+%d" % (cx, cy))
        except Exception:
            w.geometry("520x230")
        fa = (self.lang == "fa")
        txt = CONFIRM_TEXTS.get(key, {}).get(self.lang, key)
        if fa:
            txt = fa_shape(txt)
        edge = "e" if fa else "w"
        ctk.CTkLabel(w, text=self.T("confirm_title"), font=(UI_FONT, 14, "bold"),
                     text_color=AMBER, anchor=edge).pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(w, text=txt, font=(UI_FONT, 12), text_color=TXT,
                     anchor=edge, wraplength=480).pack(fill="both", expand=True, padx=16, pady=4)
        brow = ctk.CTkFrame(w, fg_color="transparent")
        brow.pack(fill="x", padx=16, pady=(4, 14))

        def _yes():
            result["ok"] = True
            w.destroy()

        def _no():
            w.destroy()

        PButton(brow, text=self.T("yes"), font=(UI_FONT, 12, "bold"),
                      fg_color="transparent", border_width=1, border_color=MAGENTA,
                      text_color=MAGENTA, command=_yes).pack(
                          side="left", expand=True, fill="x", padx=(0, 8))
        PButton(brow, text=self.T("no"), font=(UI_FONT, 12, "bold"),
                      fg_color="transparent", border_width=1, border_color=CYAN,
                      text_color=CYAN, command=_no).pack(side="left", expand=True, fill="x")
        w.protocol("WM_DELETE_WINDOW", _no)
        try:
            w.grab_set()
        except Exception:
            pass
        self.wait_window(w)
        try:
            w.grab_release()
        except Exception:
            pass
        return result["ok"]

    # ------------------------------------------------------------ run
    def run_action(self, ai):
        if self.busy:
            return
        m = MODULES[self.mod]
        if ai >= len(m.acts):
            return
        a = m.acts[ai]
        if a.kind == "link":
            self.open_link(a.path)
            return
        if a.kind == "vault":
            self.open_vault(a.path)
            return
        if not IS_WIN:
            self.log("[ERR ] execution needs Windows (dev preview on %s)." % os.name)
            return
        if a.need_folder and not self.folder:
            self.log("[WARN] target folder required - opening picker...")
            self.pick_folder()
            if not self.folder:
                self.log("[ABORT] no target selected.")
                return
        if a.confirm:
            self.log("[THINK] action needs operator consent - asking in-app...")
            if not self.ask_confirm(a.confirm):
                self.log("[ABORT] cancelled by operator.")
                return
            self.confirm_answer = "Y\r\n"
            self.log("[ OK ] consent granted :: piping YES to the tool prompt.")
        else:
            self.confirm_answer = None
        self.busy = True
        self.stop_event.clear()
        self.refresh_buttons()
        self.logq.put(("state", "thinking..."))
        t = threading.Thread(target=self.worker,
                             args=(m, a, self.folder, self.confirm_answer),
                             daemon=True)
        t.start()

    # lines that are artefacts of headless runs, not real problems
    STREAM_SKIP = ("Input redirection is not supported",
                   "Press any key to continue")

    def run_hidden_stream(self, cmd, cwd, input_text=None):
        """Run fully hidden, stream decoded lines into the log queue.
        input_text (e.g. "Y\\r\\n") is piped to stdin for interactive prompts.
        Returns exit code (or -1 on spawn failure, -2 if stopped)."""
        Q = self.logq
        kwargs = {}
        if IS_WIN:
            try:
                si = subprocess.STARTUPINFO()
                si.dwFlags |= 0x00000001  # STARTF_USESHOWWINDOW
                si.wShowWindow = 0        # SW_HIDE
                kwargs["startupinfo"] = si
            except Exception:
                pass
            kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
        try:
            p = subprocess.Popen(
                cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE if input_text else subprocess.DEVNULL,
                shell=False, **kwargs)
        except Exception as e:
            Q.put(("log", "[ERR ] spawn failed :: %s" % e))
            return -1
        self.current_proc = p
        start = time.time()
        Q.put(("log", "[EXEC] PID %s :: streaming output (hidden, in-app)..." % p.pid))
        stop_beat = threading.Event()

        def _beat():
            while not stop_beat.wait(20):
                if p.poll() is not None:
                    break
                Q.put(("log", "[....] still running (%ds elapsed) - output streams live..."
                       % (time.time() - start)))

        threading.Thread(target=_beat, daemon=True).start()
        if input_text:
            try:
                p.stdin.write(input_text.encode("ascii", "ignore"))
                p.stdin.close()
            except Exception:
                pass
        try:
            while True:
                raw = p.stdout.readline()
                if raw:
                    line = decode_line(raw).rstrip("\r\n")
                    if line.strip() and not any(s in line for s in self.STREAM_SKIP):
                        Q.put(("log", "  | " + line))
                if p.poll() is not None:
                    try:
                        rest = p.stdout.read()
                    except Exception:
                        rest = b""
                    if rest:
                        for chunk in rest.splitlines():
                            line = decode_line(chunk).strip()
                            if line and not any(s in line for s in self.STREAM_SKIP):
                                Q.put(("log", "  | " + line))
                    break
        except Exception as e:
            Q.put(("log", "[WARN] stream fault :: %s" % e))
        finally:
            stop_beat.set()
        code = p.wait()
        self.current_proc = None
        if self.stop_event.is_set():
            return -2
        return code

    def worker(self, m, a, folder, answer=None):
        Q = self.logq
        try:
            Q.put(("type", "[THINK] neural link :: module %s authenticated" % m.mid))
            time.sleep(0.25)
            if a.need_folder:
                Q.put(("type", "[THINK] target resolved :: %s" % folder))
            else:
                Q.put(("type", "[THINK] scope :: LOCAL SYSTEM (no folder needed)"))
            time.sleep(0.25)
            Q.put(("type", "[THINK] privilege scan :: ELEVATED session, no more prompts"))
            time.sleep(0.25)
            if self.stop_event.is_set():
                # STOP pressed during the thinking phase: never spawn
                Q.put(("log", "[WARN] stopped by operator before dispatch."))
                Q.put(("state", "stopped by operator"))
                return

            sd = stage_dir()
            if a.kind in ("script", "reg"):
                stage_name, raw = get_payload(a.resid)
                if a.kind == "script" and a.need_folder:
                    raw = patch_dp0(raw, folder)
                fname = stage_name if a.kind == "script" else "polaris_tweak.reg"
                spath = os.path.join(sd, fname)
                with open(spath, "wb") as f:
                    f.write(raw)
                Q.put(("type", "[THINK] payload :: %s (%d bytes, byte-exact original)"
                       % (fname, len(raw))))
                time.sleep(0.2)
                if a.copy_ico:
                    _, ico = get_payload("USB_ICO")
                    dest = os.path.join(folder, ".autorun.ico")
                    if not os.path.exists(dest):
                        try:
                            with open(dest, "wb") as f:
                                f.write(ico)
                            Q.put(("log", "[ OK ] brand icon deployed :: .autorun.ico"))
                        except Exception as e:
                            Q.put(("log", "[WARN] icon deploy failed (%s) - continuing." % e))
                    else:
                        Q.put(("log", "[SKIP] .autorun.ico already present - kept as-is."))
                if answer:
                    Q.put(("type", "[THINK] consent :: operator confirmed, answering prompt"))
                    time.sleep(0.2)
                Q.put(("log", "[EXEC] dispatching :: %s / %s" % (m.mid, a.label)))
                Q.put(("state", "running :: %s" % a.label))
                comspec = os.environ.get("COMSPEC", "cmd.exe")
                if a.kind == "script":
                    tail = (" " + a.argv) if a.argv else ""
                    # NOTE: single string, NOT a list. Python's list2cmdline
                    # would escape the inner quotes (\"...\") and cmd.exe would
                    # fail with "not recognized as an internal command".
                    # /d = skip AutoRun, /s = deterministic quote stripping.
                    cmdline = '"%s" /d /s /c ""%s"%s"' % (comspec, spath, tail)
                    code = self.run_hidden_stream(
                        cmdline, folder if a.need_folder else sd,
                        input_text=answer)
                else:
                    code = self.run_hidden_stream(
                        ["reg.exe", "import", spath], sd)
            else:  # cmd (restart explorer)
                Q.put(("type", "[THINK] payload :: direct shell command (hidden)"))
                time.sleep(0.2)
                Q.put(("log", "[EXEC] dispatching :: %s / %s" % (m.mid, a.label)))
                Q.put(("state", "running :: %s" % a.label))
                comspec = os.environ.get("COMSPEC", "cmd.exe")
                cmdline = '"%s" /d /s /c "%s"' % (comspec, a.args)
                code = self.run_hidden_stream(cmdline, sd)

            if code == -2:
                Q.put(("log", "[WARN] terminated by operator."))
                Q.put(("state", "stopped by operator"))
            elif code == -1:
                Q.put(("state", "spawn failed"))
            elif code == 0:
                Q.put(("log", "[ OK ] process exited clean :: code 0"))
                Q.put(("state", "done :: exit 0"))
            else:
                Q.put(("log", "[WARN] process ended :: exit code %s" % code))
                Q.put(("state", "done :: exit %s" % code))
            if m.mid == "SPOTLIGHT" and a.kind == "reg" and code == 0:
                Q.put(("log", "[TIP ] if the icon lingers: press RESTART EXPLORER."))
        except Exception as e:
            Q.put(("log", "[ERR ] worker fault :: %s" % e))
            Q.put(("state", "worker fault"))
        finally:
            Q.put(("done", ""))


if __name__ == "__main__":
    ensure_admin()       # UAC once, before any window exists
    load_private_fonts() # Vazirmatn for this process (no install)
    App().mainloop()
