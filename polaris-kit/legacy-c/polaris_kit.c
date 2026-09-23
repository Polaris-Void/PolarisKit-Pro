/* ============================================================================
 * POLARIS-VOID // CYBER TOOLKIT v1.0
 * All-in-one Windows hub for the 11 Polaris-Void utility projects.
 * Original .bat / .reg / .ico payloads are embedded byte-exact (resources.h).
 * UI: cyberpunk console + "thinking mode" neural log.
 * Target: Windows 7+ x64, zero dependencies, single portable EXE.
 * Build: x86_64-w64-mingw32-gcc ... (see build.sh)
 * ========================================================================== */
#ifndef UNICODE
#define UNICODE
#define _UNICODE
#endif
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0601
/* Platform-neutral core first (unit-testable on Linux) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "resources.h"

#define IDI_APP 101

/* Control IDs */
#define IDC_LIST    1001
#define IDC_DESC    1002
#define IDC_CONSOLE 1003
#define IDC_PATH    1004
#define IDC_BTN0    1011
#define IDC_BTN1    1012
#define IDC_BTN2    1013
#define IDC_BROWSE  1014
#define IDC_GITHUB  1015
#define IDC_CLEAR   1016
#define IDC_TITLE   1021
#define IDC_META    1022
#define IDC_SUB     1023
#define IDC_ADMIN   1024
#define IDC_FLBL    1025
#define IDC_CLBL    1026
#define IDC_STATUS  1027
#define IDC_HEAD    1028

/* Timers */
#define IDT_THINK 1
#define IDT_MON   2
#define IDT_CLOCK 3

/* Palette */
#define C_BG     RGB(8,10,18)
#define C_PANEL  RGB(13,17,28)
#define C_DARK   RGB(16,22,36)
#define C_CYAN   RGB(0,230,255)
#define C_DIMCY  RGB(0,140,160)
#define C_MAG    RGB(255,0,128)
#define C_GRN    RGB(0,255,170)
#define C_TXT    RGB(205,222,238)
#define C_GRAY   RGB(120,132,150)
#define C_AMBER  RGB(255,176,0)
#define C_BLACK  RGB(2,4,8)
#define C_INK    RGB(4,8,14)

/* ============================== patch engine ==============================
 * Byte-exact replacement of "%~dp0" with an ANSI target path (must end with
 * backslash). Platform independent so it can be unit tested on Linux.
 * Returns malloc'd buffer (*outlen set) or NULL. Caller frees with free(). */
static unsigned char* patch_dp0(const unsigned char* in, size_t inlen,
                                const char* target, size_t* outlen)
{
    static const char needle[] = "%~dp0";
    const size_t nlen = 5;
    size_t tlen = strlen(target);
    size_t count = 0, i = 0, need = 0;
    unsigned char *out, *p;

    if (!in || !target || !outlen) return NULL;
    for (i = 0; i + nlen <= inlen; ) {
        if (memcmp(in + i, needle, nlen) == 0) { count++; i += nlen; }
        else i++;
    }
    need = inlen + count * (tlen > nlen ? (tlen - nlen) : 0) + 1;
    out = (unsigned char*)malloc(need ? need : 1);
    if (!out) return NULL;
    p = out;
    for (i = 0; i < inlen; ) {
        if (i + nlen <= inlen && memcmp(in + i, needle, nlen) == 0) {
            memcpy(p, target, tlen); p += tlen; i += nlen;
        } else {
            *p++ = in[i++];
        }
    }
    *outlen = (size_t)(p - out);
    return out;
}
#ifndef POLARIS_TEST_HARNESS /* ================= Windows app below ======== */
#include <windows.h>
#include <shlobj.h>
#include <shellapi.h>

/* ============================== data model ============================== */
typedef enum { ACT_SCRIPT, ACT_REG, ACT_CMD, ACT_OPENPATH, ACT_URL } ActKind;

typedef struct {
    const wchar_t* label;
    ActKind kind;
    int resid;
    int admin;
    int needFolder;
    int copyIco;
    const wchar_t* cmdFile;   /* ACT_CMD */
    const wchar_t* cmdArgs;   /* ACT_CMD */
    const wchar_t* path;      /* ACT_OPENPATH / ACT_URL (env-expandable) */
} Action;

typedef struct {
    const wchar_t* id;
    const wchar_t* title;
    const wchar_t* cat;
    const wchar_t* tech;
    const wchar_t* descEN;
    const char*    descFA;    /* UTF-8, converted at runtime */
    const wchar_t* url;
    Action acts[3];
    int nActs;
} Module;

static const Module MODS[] = {
{
    L"NCSI-FIX", L"NCSI // No-Internet Fix", L"NET",
    L"tech: registry tweak + NlaSvc restart",
    L"Fix false \"No Internet\" alerts (globe icon / yellow bang while the web works), "
    L"kill surprise captive-portal popups, and control Microsoft active probing telemetry.",
    "رفع خطای کاذب No Internet (آیکون کره یا علامت زرد با وجود اینترنت سالم)، توقف پاپ‌آپ‌های captive-portal و کنترل درخواست‌های دوره‌ای مایکروسافت، بدون نیاز به ریبوت.",
    L"https://github.com/Polaris-Void/Windows-No-Internet-Fix",
    {
        { L"DISABLE PROBING",  ACT_REG, R_NCSI_DISABLE, 1, 0, 0, NULL, NULL, NULL },
        { L"ENABLE PROBING",   ACT_REG, R_NCSI_ENABLE,  1, 0, 0, NULL, NULL, NULL },
        { L"RESTART NLA SVC",  ACT_SCRIPT, R_NCSI_RESTART, 1, 0, 0, NULL, NULL, NULL },
    }, 3
},
{
    L"USER-BACKUP", L"User Folders Backup", L"BACKUP",
    L"tech: robocopy + registry path resolution",
    L"Backup Desktop, Downloads, Documents, Pictures, Music, Videos to C:\\User Backup. "
    L"Resolves real paths from the registry (OneDrive aware). Restore merges back without overwriting anything.",
    "بکاپ خودکار پوشه‌های کاربر (دسکتاپ، دانلود، اسناد، عکس، موسیقی، ویدیو) در C:\\User Backup با Robocopy؛ مسیرها از رجیستری خوانده می‌شود (سازگار با OneDrive) و بازیابی هیچ فایلی را بازنویسی نمی‌کند.",
    L"https://github.com/Polaris-Void/Win-User-Backup",
    {
        { L"BACKUP NOW",       ACT_SCRIPT, R_USERBACKUP, 1, 0, 0, NULL, NULL, NULL },
        { L"RESTORE (MERGE)",  ACT_SCRIPT, R_USERRESTORE, 1, 0, 0, NULL, NULL, NULL },
        { L"OPEN VAULT",       ACT_OPENPATH, -1, 0, 0, 0, NULL, NULL, L"C:\\User Backup" },
    }, 3
},
{
    L"SPOTLIGHT", L"Spotlight Icon Toggle", L"DESKTOP",
    L"tech: HKCU registry tweak",
    L"Remove the annoying \"Learn about this picture\" desktop icon while keeping Spotlight "
    L"wallpapers alive. One click to hide, one click to bring it back.",
    "حذف آیکون مزاحم «Learn about this picture» از دسکتاپ بدون غیرفعال‌کردن والپیپر Spotlight؛ مخفی یا نمایش با یک کلیک.",
    L"https://github.com/Polaris-Void/Win-Spotlight-Icon-Toggle",
    {
        { L"HIDE ICON",        ACT_REG, R_SPOT_HIDE, 0, 0, 0, NULL, NULL, NULL },
        { L"SHOW ICON",        ACT_REG, R_SPOT_SHOW, 0, 0, 0, NULL, NULL, NULL },
        { L"RESTART EXPLORER", ACT_CMD, -1, 0, 0, 0, L"cmd.exe",
          L"/c taskkill /F /IM explorer.exe & timeout /t 1 >nul & start explorer.exe", NULL },
    }, 3
},
{
    L"DRV-BACKUP", L"OEM Driver Backup", L"DRIVERS",
    L"tech: DISM + PnPUtil, zero dependencies",
    L"Export every third-party OEM driver to a vault, and reinstall them in bulk later. "
    L"The lifesaver you run before reinstalling Windows.",
    "بکاپ کامل درایورهای OEM با DISM و نصب گروهی آن‌ها هنگام بازیابی؛ نجات‌دهنده قبل از تعویض ویندوز، بدون هیچ وابستگی.",
    L"https://github.com/Polaris-Void/Win-Drv-Backup",
    {
        { L"BACKUP ALL OEM",   ACT_SCRIPT, R_DRVBACKUP, 1, 0, 0, NULL, NULL, NULL },
        { L"RESTORE DRIVERS",  ACT_SCRIPT, R_DRVRESTORE, 1, 0, 0, NULL, NULL, NULL },
        { L"OPEN VAULT",       ACT_OPENPATH, -1, 0, 0, 0, NULL, NULL, L"%SystemDrive%\\Backup_Driver" },
    }, 3
},
{
    L"DISP-BACKUP", L"Display Driver Backup", L"DRIVERS",
    L"tech: Get-WindowsDriver + PnPUtil export",
    L"Surgical backup/restore of GPU display-class drivers only. Filters the Display class GUID "
    L"and exports matching oem*.inf packages.",
    "بکاپ و بازیابی تخصصی درایور گرافیک (فقط کلاس Display) با فیلتر GUID و خروجی PnPUtil؛ سریع و تمیز.",
    L"https://github.com/Polaris-Void/Win-Display-Drv-Backup",
    {
        { L"BACKUP DISPLAY",   ACT_SCRIPT, R_DISPBACKUP, 1, 0, 0, NULL, NULL, NULL },
        { L"RESTORE DISPLAY",  ACT_SCRIPT, R_DISPRESTORE, 1, 0, 0, NULL, NULL, NULL },
        { L"OPEN VAULT",       ACT_OPENPATH, -1, 0, 0, 0, NULL, NULL, L"%SystemDrive%\\Backup_Display_Driver" },
    }, 3
},
{
    L"USB-SHIELD", L"USB Immunizer", L"USB",
    L"tech: decoy files + hidden/system attributes",
    L"Immunize a USB stick against auto-created junk (Android, System Volume Information) using "
    L"hidden decoy files, and brand it with a custom icon + label. Pick the drive root first.",
    "ایمن‌سازی فلش USB در برابر پوشه‌های زائد خودکار با فایل‌طعمه Hidden/System و برندسازی آیکون و لیبل درایو؛ ابتدا ریشه درایو را انتخاب کن.",
    L"https://github.com/Polaris-Void/USB-Immunizer-Customizer",
    {
        { L"IMMUNIZE TARGET",  ACT_SCRIPT, R_USB_TOOL, 1, 1, 1, NULL, NULL, NULL },
        { L"OPEN ON GITHUB",   ACT_URL, -1, 0, 0, 0, NULL, NULL, L"https://github.com/Polaris-Void/USB-Immunizer-Customizer" },
        { NULL, ACT_URL, -1, 0, 0, 0, NULL, NULL, NULL },
    }, 2
},
{
    L"DNS-RESET", L"DNS + Proxy Reset", L"NET",
    L"tech: NetAdapter reset + proxy off + flushdns",
    L"Reset DNS to automatic (DHCP) on all adapters, disable system proxy (HKCU+HKLM), and flush "
    L"the resolver cache. First aid for \"connected but nothing loads\".",
    "ریست DNS به حالت خودکار (DHCP)، غیرفعال‌سازی پروکسی سیستم و Flush کش DNS؛ کمک‌های اولیه برای «وصلم ولی هیچی باز نمی‌شود».",
    L"https://github.com/Polaris-Void/Reset-DNS-Proxy",
    {
        { L"RESET DNS+PROXY",  ACT_SCRIPT, R_DNSRESET, 1, 0, 0, NULL, NULL, NULL },
        { L"OPEN ON GITHUB",   ACT_URL, -1, 0, 0, 0, NULL, NULL, L"https://github.com/Polaris-Void/Reset-DNS-Proxy" },
        { NULL, ACT_URL, -1, 0, 0, 0, NULL, NULL, NULL },
    }, 2
},
{
    L"MEDIA-RENAME", L"Image / Video Renamer", L"FILES",
    L"tech: recursive batch rename, collision-safe",
    L"Bulk-rename 50+ image formats to .jpg and 40+ video formats to .mp4, recursively. "
    L"Name clashes get auto (1), (2) suffixes - nothing is ever overwritten or deleted.",
    "تغییرنام گروهی بازگشتی: ده‌ها فرمت عکس به jpg. و ویدیو به mp4.؛ تداخل نام با پسوند خودکار حل می‌شود و هیچ فایلی بازنویسی یا حذف نمی‌شود.",
    L"https://github.com/Polaris-Void/Image-Video-Renamer",
    {
        { L"IMAGES -> .JPG",   ACT_SCRIPT, R_IMGREN, 0, 1, 0, NULL, NULL, NULL },
        { L"VIDEOS -> .MP4",   ACT_SCRIPT, R_VIDREN, 0, 1, 0, NULL, NULL, NULL },
        { NULL, ACT_URL, -1, 0, 0, 0, NULL, NULL, NULL },
    }, 2
},
{
    L"TREE-EXPORT", L"Directory Tree Exporter", L"AUDIT",
    L"tech: batch + PowerShell, UTF-8 report",
    L"Map a folder into a visual tree report with sizes and creation/modification dates. "
    L"Wide UTF-8 table, self-excluding log, stats summary included.",
    "تولید گزارش درختی دایرکتوری با حجم و تاریخ ساخت/تغییر در فایل UTF-8؛ مناسب مستندسازی پروژه و آرشیو.",
    L"https://github.com/Polaris-Void/Directory-Tree-Exporter",
    {
        { L"EXPORT TREE",      ACT_SCRIPT, R_TREE, 0, 1, 0, NULL, NULL, NULL },
        { L"OPEN ON GITHUB",   ACT_URL, -1, 0, 0, 0, NULL, NULL, L"https://github.com/Polaris-Void/Directory-Tree-Exporter" },
        { NULL, ACT_URL, -1, 0, 0, 0, NULL, NULL, NULL },
    }, 2
},
{
    L"SHA256-AUDIT", L"SHA-256 Tree Auditor", L"AUDIT",
    L"tech: Get-FileHash per file, tamper evidence",
    L"Everything Tree Exporter does, plus a SHA-256 checksum for every file. Prove integrity, "
    L"detect corruption or tampering. Locked files are tagged, never fatal.",
    "ممیزی دقیق: درخت دایرکتوری + متادیتا + هش SHA-256 تک‌تک فایل‌ها برای اثبات یکپارچگی و تشخیص دستکاری یا خرابی.",
    L"https://github.com/Polaris-Void/Directory-SHA256-Tree-Exporter",
    {
        { L"RUN SHA-256 AUDIT", ACT_SCRIPT, R_SHA256, 0, 1, 0, NULL, NULL, NULL },
        { L"OPEN ON GITHUB",   ACT_URL, -1, 0, 0, 0, NULL, NULL, L"https://github.com/Polaris-Void/Directory-SHA256-Tree-Exporter" },
        { NULL, ACT_URL, -1, 0, 0, 0, NULL, NULL, NULL },
    }, 2
},
{
    L"UNPACK", L"Subfolder Unpacker", L"FILES",
    L"tech: deep recursive move-to-parent",
    L"Flatten chaos: move every file from all nested subfolders straight into the parent folder. "
    L"Perfect cleanup after extracting archives or multi-folder downloads.",
    "صاف‌کردن پوشه‌ها: انتقال همه فایل‌ها از ساب‌فولدرهای تودرتو به پوشه اصلی؛ عالی برای تمیزکاری بعد از اکسترکت آرشیوها.",
    L"https://github.com/Polaris-Void/Unpack-Subfolders",
    {
        { L"UNPACK TO PARENT", ACT_SCRIPT, R_UNPACK, 0, 1, 0, NULL, NULL, NULL },
        { L"OPEN ON GITHUB",   ACT_URL, -1, 0, 0, 0, NULL, NULL, L"https://github.com/Polaris-Void/Unpack-Subfolders" },
        { NULL, ACT_URL, -1, 0, 0, 0, NULL, NULL, NULL },
    }, 2
}
};
#define N_MODS (int)(sizeof(MODS)/sizeof(MODS[0]))

/* ============================== globals ============================== */
static HINSTANCE g_hInst;
static HWND g_hMain, g_hList, g_hDesc, g_hConsole, g_hPath;
static HWND g_hBtn[3], g_hBrowse, g_hGithub, g_hClear;
static HWND g_hTitle, g_hMeta, g_hSub, g_hAdmin, g_hFLbl, g_hCLbl, g_hStatus, g_hHead;
static HFONT g_fTitle, g_fHead, g_fUI, g_fBtn, g_fList, g_fListSm, g_fMono, g_fDesc;
static HBRUSH g_brBg, g_brPanel, g_brDark, g_brBlack, g_brCyan, g_brMag, g_brDimCy;
static int g_mod = 0;
static wchar_t g_folder[MAX_PATH] = L"";
static wchar_t g_tempdir[MAX_PATH] = L"";
static wchar_t g_state[160] = L"ready";
static int g_isAdmin = 0;
/* thinking sequence */
static int g_pMod = 0, g_pAct = 0, g_thinkStep = 0, g_thinkTotal = 0;
static wchar_t g_think[6][560];
static HANDLE g_hProc = NULL;

/* ============================== helpers ============================== */
static void set_status_state(const wchar_t* s) {
    wcsncpy(g_state, s, 159); g_state[159] = 0;
}

static void nlog(const wchar_t* fmt, ...) {
    wchar_t buf[2300], line[2400];
    SYSTEMTIME st;
    va_list ap;
    int n, len;
    if (!g_hConsole) return;
    va_start(ap, fmt);
    n = vswprintf(buf, 2290, fmt, ap);
    va_end(ap);
    if (n < 0) return;
    GetLocalTime(&st);
    _snwprintf(line, 2390, L"[%02d:%02d:%02d] %ls\r\n",
               st.wHour, st.wMinute, st.wSecond, buf);
    line[2390] = 0;
    len = GetWindowTextLengthW(g_hConsole);
    if (len > 60000) { /* trim head to avoid unbounded growth */
        SendMessageW(g_hConsole, EM_SETSEL, 0, 12000);
        SendMessageW(g_hConsole, EM_REPLACESEL, FALSE, (LPARAM)L"");
    }
    SendMessageW(g_hConsole, EM_SETSEL, (WPARAM)-1, (LPARAM)-1);
    SendMessageW(g_hConsole, EM_REPLACESEL, FALSE, (LPARAM)line);
    SendMessageW(g_hConsole, EM_SCROLLCARET, 0, 0);
}

static int is_admin(void) {
    BOOL b = FALSE;
    PSID sid = NULL;
    SID_IDENTIFIER_AUTHORITY nt = SECURITY_NT_AUTHORITY;
    if (AllocateAndInitializeSid(&nt, 2, SECURITY_BUILTIN_DOMAIN_RID,
            DOMAIN_ALIAS_RID_ADMINS, 0, 0, 0, 0, 0, 0, &sid)) {
        CheckTokenMembership(NULL, sid, &b);
        FreeSid(sid);
    }
    return b ? 1 : 0;
}

static int write_bytes(const wchar_t* path, const unsigned char* data, size_t len) {
    HANDLE h = CreateFileW(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                           FILE_ATTRIBUTE_NORMAL, NULL);
    DWORD wrote = 0;
    if (h == INVALID_HANDLE_VALUE) return 0;
    if (len && !WriteFile(h, data, (DWORD)len, &wrote, NULL)) {
        CloseHandle(h); return 0;
    }
    CloseHandle(h);
    return (size_t)wrote == len;
}

static int module_needs_folder(int m) {
    int i;
    for (i = 0; i < MODS[m].nActs; i++)
        if (MODS[m].acts[i].needFolder) return 1;
    return 0;
}

static void enable_actions(int en) {
    int i;
    for (i = 0; i < 3; i++) EnableWindow(g_hBtn[i], en);
    EnableWindow(g_hBrowse, en);
}

/* Build ANSI target path with trailing backslash for %~dp0 injection. */
static int build_ansi_target(char* out, int outsz) {
    int n, len;
    n = WideCharToMultiByte(CP_ACP, 0, g_folder, -1, out, outsz - 2, NULL, NULL);
    if (n <= 0) return 0;
    len = (int)strlen(out);
    if (len <= 0) return 0;
    if (out[len - 1] != '\\' && len + 1 < outsz) {
        out[len] = '\\'; out[len + 1] = 0;
    }
    return 1;
}

/* ============================== dispatch ============================== */
static void dispatch_pending(void);

static void start_action(int mod, int act) {
    const Module* M = &MODS[mod];
    const Action* A = &M->acts[act];
    wchar_t stage[64];
    int k = 0;

    if (A->needFolder && !g_folder[0]) {
        nlog(L"[WARN] target folder required - opening picker...");
        SendMessageW(g_hMain, WM_COMMAND, MAKEWPARAM(IDC_BROWSE, BN_CLICKED), (LPARAM)g_hBrowse);
        if (!g_folder[0]) { nlog(L"[ABORT] no target selected."); return; }
    }

    g_pMod = mod; g_pAct = act; g_thinkStep = 0;
    _snwprintf(g_think[k++], 550, L"[THINK] neural link :: module %ls authenticated", M->id);
    if (A->needFolder)
        _snwprintf(g_think[k++], 550, L"[THINK] target resolved :: %ls", g_folder);
    else
        _snwprintf(g_think[k++], 550, L"[THINK] scope :: LOCAL SYSTEM (no folder needed)");
    if (A->admin)
        _snwprintf(g_think[k++], 550, L"[THINK] privilege scan :: ELEVATION REQUIRED - approve the UAC prompt");
    else
        _snwprintf(g_think[k++], 550, L"[THINK] privilege scan :: standard token sufficient");
    if (A->kind == ACT_SCRIPT || A->kind == ACT_REG) {
        MultiByteToWideChar(CP_UTF8, 0, RES_TABLE[A->resid].stage, -1, stage, 63);
        _snwprintf(g_think[k++], 550,
            L"[THINK] payload :: %ls (%u bytes, byte-exact original)",
            stage, RES_TABLE[A->resid].len);
    } else if (A->kind == ACT_CMD) {
        _snwprintf(g_think[k++], 550, L"[THINK] payload :: direct shell command");
    } else if (A->kind == ACT_OPENPATH) {
        _snwprintf(g_think[k++], 550, L"[THINK] payload :: open vault folder");
    } else {
        _snwprintf(g_think[k++], 550, L"[THINK] payload :: open upstream repository");
    }
    g_thinkTotal = k;
    enable_actions(FALSE);
    set_status_state(L"thinking...");
    SetTimer(g_hMain, IDT_THINK, 210, NULL);
}

static void run_elevated_or_not(const wchar_t* file, const wchar_t* args,
                                const wchar_t* dir, int admin) {
    SHELLEXECUTEINFOW sei;
    memset(&sei, 0, sizeof(sei));
    sei.cbSize = sizeof(sei);
    sei.fMask = SEE_MASK_NOCLOSEPROCESS | SEE_MASK_NOASYNC | SEE_MASK_FLAG_NO_UI;
    sei.hwnd = g_hMain;
    sei.lpVerb = admin ? L"runas" : L"open";
    sei.lpFile = file;
    sei.lpParameters = args;
    sei.lpDirectory = dir;
    sei.nShow = SW_SHOWNORMAL;
    if (ShellExecuteExW(&sei)) {
        nlog(L"[EXEC] process spawned (%ls) :: %ls",
             admin ? L"elevated" : L"standard", file);
        if (sei.hProcess) {
            if (g_hProc) CloseHandle(g_hProc);
            g_hProc = sei.hProcess;
            nlog(L"[EXEC] PID %u :: monitoring exit code...",
                 (unsigned)GetProcessId(sei.hProcess));
            SetTimer(g_hMain, IDT_MON, 500, NULL);
        } else {
            nlog(L"[ OK ] detached - no handle returned, check the tool window.");
            set_status_state(L"dispatched (detached)");
        }
    } else {
        DWORD e = GetLastError();
        if (e == ERROR_CANCELLED)
            nlog(L"[ABORT] UAC denied by operator (1223). Nothing was executed.");
        else
            nlog(L"[ERR ] launch failed :: Win32 error %u", (unsigned)e);
        set_status_state(L"launch failed");
    }
}

static void dispatch_pending(void) {
    const Module* M = &MODS[g_pMod];
    const Action* A = &M->acts[g_pAct];
    wchar_t sysdir[MAX_PATH], exe[MAX_PATH], arg[1100], stagePath[MAX_PATH * 2];

    nlog(L"[EXEC] dispatching :: %ls / %ls", M->id, A->label);
    switch (A->kind) {
    case ACT_SCRIPT: {
        const ResEntry* R = &RES_TABLE[A->resid];
        const unsigned char* data = R->data;
        size_t len = R->len;
        unsigned char* patched = NULL;
        size_t plen = 0;
        wchar_t stageW[64];
        MultiByteToWideChar(CP_UTF8, 0, R->stage, -1, stageW, 63);
        _snwprintf(stagePath, 2000, L"%ls%ls", g_tempdir, stageW);
        if (A->needFolder) {
            char ansiTarget[MAX_PATH + 4];
            if (!build_ansi_target(ansiTarget, sizeof(ansiTarget))) {
                nlog(L"[ERR ] cannot encode target path - aborting.");
                set_status_state(L"path encode error");
                return;
            }
            patched = patch_dp0(R->data, R->len, ansiTarget, &plen);
            if (!patched) {
                nlog(L"[ERR ] staging buffer failure - aborting.");
                set_status_state(L"staging error");
                return;
            }
            data = patched; len = plen;
        }
        if (!write_bytes(stagePath, data, len)) {
            nlog(L"[ERR ] cannot write staging file - aborting.");
            if (patched) free(patched);
            set_status_state(L"staging error");
            return;
        }
        nlog(L"[ OK ] staged :: %ls (%u bytes)", stageW, (unsigned)len);
        if (patched) free(patched);
        if (A->copyIco) { /* USB: drop brand icon next to target if missing */
            wchar_t icoPath[MAX_PATH * 2];
            _snwprintf(icoPath, 2000, L"%ls%ls.autorun.ico",
                       g_folder,
                       (g_folder[wcslen(g_folder) - 1] == L'\\') ? L"" : L"\\");
            if (GetFileAttributesW(icoPath) == INVALID_FILE_ATTRIBUTES) {
                if (write_bytes(icoPath, RES_TABLE[R_USB_ICO].data,
                                RES_TABLE[R_USB_ICO].len))
                    nlog(L"[ OK ] brand icon deployed :: .autorun.ico");
                else
                    nlog(L"[WARN] icon deploy failed - continuing anyway.");
            } else {
                nlog(L"[SKIP] .autorun.ico already present - kept as-is.");
            }
        }
        GetSystemDirectoryW(sysdir, MAX_PATH);
        _snwprintf(exe, MAX_PATH - 1, L"%ls\\cmd.exe", sysdir);
        _snwprintf(arg, 1090, L"/c \"\"%ls\"\"", stagePath);
        run_elevated_or_not(exe, arg, A->needFolder ? g_folder : g_tempdir, A->admin);
        break;
    }
    case ACT_REG: {
        const ResEntry* R = &RES_TABLE[A->resid];
        _snwprintf(stagePath, 2000, L"%lspolaris_tweak.reg", g_tempdir);
        if (!write_bytes(stagePath, R->data, R->len)) {
            nlog(L"[ERR ] cannot write staging file - aborting.");
            set_status_state(L"staging error");
            return;
        }
        nlog(L"[ OK ] staged :: polaris_tweak.reg (%u bytes)", R->len);
        GetSystemDirectoryW(sysdir, MAX_PATH);
        _snwprintf(exe, MAX_PATH - 1, L"%ls\\regedit.exe", sysdir);
        _snwprintf(arg, 1090, L"/s \"%ls\"", stagePath);
        run_elevated_or_not(exe, arg, g_tempdir, A->admin);
        if (g_pMod == 2)
            nlog(L"[TIP ] if the icon lingers: press RESTART EXPLORER.");
        break;
    }
    case ACT_CMD: {
        GetSystemDirectoryW(sysdir, MAX_PATH);
        _snwprintf(exe, MAX_PATH - 1, L"%ls\\%ls", sysdir, A->cmdFile);
        run_elevated_or_not(exe, A->cmdArgs, g_tempdir, A->admin);
        break;
    }
    case ACT_OPENPATH: {
        wchar_t expanded[MAX_PATH * 2];
        HINSTANCE r;
        ExpandEnvironmentStringsW(A->path, expanded, 2000);
        r = ShellExecuteW(g_hMain, L"open", expanded, NULL, NULL, SW_SHOWNORMAL);
        if ((INT_PTR)r > 32) {
            nlog(L"[ OK ] vault opened :: %ls", expanded);
            set_status_state(L"vault opened");
        } else {
            nlog(L"[WARN] folder not found yet (run backup first) :: %ls", expanded);
            set_status_state(L"vault missing");
        }
        break;
    }
    case ACT_URL: {
        HINSTANCE r = ShellExecuteW(g_hMain, L"open", A->path, NULL, NULL, SW_SHOWNORMAL);
        if ((INT_PTR)r > 32) {
            nlog(L"[ OK ] browser launched :: upstream repo");
            set_status_state(L"browser launched");
        } else {
            nlog(L"[ERR ] cannot open browser.");
            set_status_state(L"browser failed");
        }
        break;
    }
    }
    enable_actions(TRUE);
}

/* ============================== UI: details ============================== */
static void refresh_details(void) {
    const Module* M = &MODS[g_mod];
    wchar_t meta[300], desc[4600], faW[2400], head[128];
    int i, showFolder = module_needs_folder(g_mod);

    _snwprintf(head, 120, L"[%02d/%02d] %ls", g_mod + 1, N_MODS, M->title);
    SetWindowTextW(g_hTitle, head);
    _snwprintf(meta, 290, L"sector:%ls :: %ls :: %d action%ls :: src: github.com/Polaris-Void",
               M->cat, M->tech, M->nActs, M->nActs > 1 ? L"s" : L"");
    SetWindowTextW(g_hMeta, meta);

    MultiByteToWideChar(CP_UTF8, 0, M->descFA, -1, faW, 2390);
    _snwprintf(desc, 4590, L"%ls\r\n\r\n%ls\r\n\r\n%ls",
               M->descEN, faW, M->url);
    SetWindowTextW(g_hDesc, desc);

    for (i = 0; i < 3; i++) {
        if (i < M->nActs && M->acts[i].label) {
            SetWindowTextW(g_hBtn[i], M->acts[i].label);
            SetWindowLongPtrW(g_hBtn[i], GWLP_USERDATA,
                              M->acts[i].admin ? 1 : 0);
            ShowWindow(g_hBtn[i], SW_SHOW);
        } else {
            ShowWindow(g_hBtn[i], SW_HIDE);
        }
    }
    ShowWindow(g_hFLbl, showFolder ? SW_SHOW : SW_HIDE);
    ShowWindow(g_hPath, showFolder ? SW_SHOW : SW_HIDE);
    ShowWindow(g_hBrowse, showFolder ? SW_SHOW : SW_HIDE);

    {
        wchar_t st[160];
        _snwprintf(st, 150, L"module %02d/%02d :: %ls", g_mod + 1, N_MODS, M->id);
        set_status_state(st);
    }
    /* relayout right column */
    {
        RECT rc; GetClientRect(g_hMain, &rc);
        SendMessageW(g_hMain, WM_SIZE, 0,
                     MAKELPARAM(rc.right - rc.left, rc.bottom - rc.top));
    }
}

static void pick_folder(void) {
    BROWSEINFOW bi;
    LPITEMIDLIST pidl;
    wchar_t buf[MAX_PATH];
    memset(&bi, 0, sizeof(bi));
    bi.hwndOwner = g_hMain;
    bi.lpszTitle = L"Select TARGET folder (USB root for immunizer)";
    bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE | BIF_USENEWUI;
    pidl = SHBrowseForFolderW(&bi);
    if (!pidl) { nlog(L"[SKIP] picker cancelled."); return; }
    buf[0] = 0;
    if (SHGetPathFromIDListW(pidl, buf) && buf[0]) {
        wcsncpy(g_folder, buf, MAX_PATH - 1);
        SetWindowTextW(g_hPath, g_folder);
        nlog(L"[ OK ] target locked :: %ls", g_folder);
    } else {
        nlog(L"[WARN] could not resolve that selection.");
    }
    CoTaskMemFree(pidl);
}

/* ============================== layout ============================== */
static void do_layout(int W, int H) {
    const int M = 12, headH = 86, statusH = 28, consoleH = 178;
    const int sideW = 292;
    int rx = M + sideW + 12;              /* right column x */
    int rw = W - rx - M;                  /* right column w */
    int consoleTop = H - statusH - consoleH;
    int clblY = consoleTop - 24;
    int yBtn = clblY - 46;
    int yFolder = yBtn - 38;
    int listTop = headH + 30;
    int listBottom = yBtn + 38;
    int showFolder = module_needs_folder(g_mod);
    int descTop = headH + 50;
    int descBottom = showFolder ? (yFolder - 8) : (yBtn - 8);
    int descH = descBottom - descTop;
    int bw, i, visBtns = 0;
    if (descH < 60) descH = 60;

    if (W < 200 || H < 200) return;
    for (i = 0; i < 3; i++)
        if (IsWindowVisible(g_hBtn[i])) visBtns++;

    MoveWindow(g_hHead, M, 10, 760, 30, TRUE);
    MoveWindow(g_hSub, M + 2, 42, 760, 20, TRUE);
    MoveWindow(g_hGithub, W - M - 150, 10, 150, 30, TRUE);
    MoveWindow(g_hAdmin, W - M - 330, 44, 330, 20, TRUE);

    /* sidebar */
    {
        HWND hLbl = GetDlgItem(g_hMain, 2001);
        if (hLbl) MoveWindow(hLbl, M, headH + 6, sideW, 20, TRUE);
    }
    MoveWindow(g_hList, M, listTop, sideW, listBottom - listTop, TRUE);

    /* right column */
    MoveWindow(g_hTitle, rx, headH + 2, rw, 28, TRUE);
    MoveWindow(g_hMeta, rx, headH + 30, rw, 18, TRUE);
    MoveWindow(g_hDesc, rx, descTop, rw, descH, TRUE);
    if (showFolder) {
        MoveWindow(g_hFLbl, rx, yFolder + 2, 140, 26, TRUE);
        MoveWindow(g_hPath, rx + 144, yFolder + 2, rw - 144 - 120, 26, TRUE);
        MoveWindow(g_hBrowse, rx + rw - 112, yFolder, 112, 30, TRUE);
    }
    bw = visBtns ? (rw - (visBtns - 1) * 10) / visBtns : rw;
    {
        int x = rx, k = 0;
        for (i = 0; i < 3; i++) {
            if (!IsWindowVisible(g_hBtn[i])) continue;
            MoveWindow(g_hBtn[i], x, yBtn, bw, 38, TRUE);
            x += bw + 10; k++;
        }
    }
    /* console spans full width */
    MoveWindow(g_hCLbl, M, H - statusH - consoleH - 24, W - M - 130, 20, TRUE);
    MoveWindow(g_hClear, W - M - 110, H - statusH - consoleH - 26, 110, 24, TRUE);
    MoveWindow(g_hConsole, M, H - statusH - consoleH, W - 2 * M, consoleH, TRUE);
    MoveWindow(g_hStatus, 0, H - statusH, W, statusH, TRUE);
}

/* ============================== owner draw ============================== */
static void draw_list_item(DRAWITEMSTRUCT* d) {
    HDC hdc = d->hDC;
    RECT rc = d->rcItem;
    int idx, oldBk;
    COLORREF cIdx, cSub;
    RECT bar, r1, r2;
    wchar_t line1[160], line2[160];

    if (d->itemID == (UINT)-1) {
        FillRect(hdc, &rc, g_brPanel);
        return;
    }
    idx = (int)d->itemData;
    if (idx < 0 || idx >= N_MODS) { FillRect(hdc, &rc, g_brPanel); return; }
    {
        BOOL sel = (d->itemState & ODS_SELECTED) ? TRUE : FALSE;
        FillRect(hdc, &rc, sel ? g_brCyan : g_brPanel);
        bar = rc; bar.right = bar.left + 4;
        FillRect(hdc, &bar, sel ? g_brMag : g_brDimCy);
        cIdx  = sel ? C_INK : C_CYAN;
        cSub  = sel ? RGB(20,30,40) : C_GRAY;
        _snwprintf(line1, 150, L"%02d  %ls", idx + 1, MODS[idx].title);
        _snwprintf(line2, 150, L"       %ls :: %d actions",
                   MODS[idx].cat, MODS[idx].nActs);
        oldBk = SetBkMode(hdc, TRANSPARENT);
        SelectObject(hdc, g_fList);
        r1 = rc; r1.left += 12; r1.top += 1; r1.bottom = r1.top + 19;
        SetTextColor(hdc, cIdx);
        DrawTextW(hdc, line1, -1, &r1, DT_LEFT | DT_SINGLELINE | DT_END_ELLIPSIS);
        SelectObject(hdc, g_fListSm);
        r2 = rc; r2.left += 12; r2.top += 19; r2.bottom = r2.top + 16;
        SetTextColor(hdc, cSub);
        DrawTextW(hdc, line2, -1, &r2, DT_LEFT | DT_SINGLELINE | DT_END_ELLIPSIS);
        /* title part in brighter tone: redraw name portion */
        SetBkMode(hdc, oldBk);
        if (d->itemState & ODS_FOCUS) DrawFocusRect(hdc, &rc);
    }
}

static void draw_button(DRAWITEMSTRUCT* d) {
    HDC hdc = d->hDC;
    RECT rc = d->rcItem;
    wchar_t txt[128];
    BOOL dis = (d->itemState & ODS_DISABLED) ? TRUE : FALSE;
    BOOL press = (d->itemState & ODS_SELECTED) ? TRUE : FALSE;
    int isAdmin = (int)GetWindowLongPtrW(d->hwndItem, GWLP_USERDATA);
    COLORREF bg = dis ? RGB(18,22,32) : press ? C_CYAN : C_DARK;
    COLORREF brd = dis ? RGB(64,72,88) : press ? RGB(220,255,255) : C_CYAN;
    COLORREF fg = dis ? C_GRAY : press ? C_INK : RGB(185,245,255);
    HBRUSH hbg = CreateSolidBrush(bg);
    HBRUSH hbr = CreateSolidBrush(brd);
    RECT inner = rc;
    int oldBk;

    GetWindowTextW(d->hwndItem, txt, 127);
    FillRect(hdc, &rc, hbg);
    FrameRect(hdc, &rc, hbr);
    if (isAdmin && !dis) {
        RECT ab = rc;
        ab.left += 3; ab.right = ab.left + 4; ab.top += 3; ab.bottom -= 3;
        FillRect(hdc, &ab, g_brMag);
    }
    if (press) { rc.left += 1; rc.top += 1; }
    oldBk = SetBkMode(hdc, TRANSPARENT);
    SelectObject(hdc, g_fBtn);
    SetTextColor(hdc, fg);
    inner.left += 6; inner.right -= 6;
    DrawTextW(hdc, txt, -1, &inner,
              DT_CENTER | DT_VCENTER | DT_SINGLELINE | DT_END_ELLIPSIS);
    SetBkMode(hdc, oldBk);
    if ((d->itemState & ODS_FOCUS) && !dis) {
        RECT fr = d->rcItem;
        InflateRect(&fr, -4, -4);
        DrawFocusRect(hdc, &fr);
    }
    DeleteObject(hbg);
    DeleteObject(hbr);
}

/* ============================== window proc ============================== */
static LRESULT CALLBACK WndProc(HWND h, UINT m, WPARAM w, LPARAM l) {
    switch (m) {
    case WM_CREATE: {
        HWND hLbl;
        int i;
        (void)l;
        g_hMain = h;

        g_brBg = CreateSolidBrush(C_BG);
        g_brPanel = CreateSolidBrush(C_PANEL);
        g_brDark = CreateSolidBrush(C_DARK);
        g_brBlack = CreateSolidBrush(C_BLACK);
        g_brCyan = CreateSolidBrush(C_CYAN);
        g_brMag = CreateSolidBrush(C_MAG);
        g_brDimCy = CreateSolidBrush(C_DIMCY);

        g_fTitle = CreateFontW(26, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, FF_MODERN, L"Consolas");
        g_fHead = CreateFontW(17, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, FF_MODERN, L"Consolas");
        g_fUI = CreateFontW(17, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, DEFAULT_PITCH, L"Segoe UI");
        g_fBtn = CreateFontW(17, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, DEFAULT_PITCH, L"Segoe UI");
        g_fList = CreateFontW(17, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, FF_MODERN, L"Consolas");
        g_fListSm = CreateFontW(14, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, FF_MODERN, L"Consolas");
        g_fMono = CreateFontW(16, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, FF_MODERN, L"Consolas");
        g_fDesc = CreateFontW(18, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, DEFAULT_PITCH, L"Segoe UI");

        g_hHead = CreateWindowExW(0, L"STATIC", L"POLARIS-VOID // CYBER TOOLKIT",
            WS_CHILD | WS_VISIBLE | SS_LEFT,
            0, 0, 10, 10, h, (HMENU)IDC_HEAD, g_hInst, NULL);
        SendMessageW(g_hHead, WM_SETFONT, (WPARAM)g_fTitle, 0);

        g_hSub = CreateWindowExW(0, L"STATIC",
            L"11 windows utilities // one neon hub // thinking mode: ON",
            WS_CHILD | WS_VISIBLE | SS_LEFT,
            0, 0, 10, 10, h, (HMENU)IDC_SUB, g_hInst, NULL);
        SendMessageW(g_hSub, WM_SETFONT, (WPARAM)g_fUI, 0);

        g_hGithub = CreateWindowExW(0, L"BUTTON", L"GITHUB //",
            WS_CHILD | WS_VISIBLE | BS_OWNERDRAW | WS_TABSTOP,
            0, 0, 10, 10, h, (HMENU)IDC_GITHUB, g_hInst, NULL);

        g_hAdmin = CreateWindowExW(0, L"STATIC", L"",
            WS_CHILD | WS_VISIBLE | SS_RIGHT,
            0, 0, 10, 10, h, (HMENU)IDC_ADMIN, g_hInst, NULL);
        SendMessageW(g_hAdmin, WM_SETFONT, (WPARAM)g_fUI, 0);

        hLbl = CreateWindowExW(0, L"STATIC", L"// MODULES",
            WS_CHILD | WS_VISIBLE | SS_LEFT,
            0, 0, 10, 10, h, (HMENU)2001, g_hInst, NULL);
        SendMessageW(hLbl, WM_SETFONT, (WPARAM)g_fHead, 0);

        g_hList = CreateWindowExW(WS_EX_CLIENTEDGE, L"LISTBOX", L"",
            WS_CHILD | WS_VISIBLE | WS_VSCROLL | LBS_NOTIFY |
            LBS_OWNERDRAWFIXED | LBS_HASSTRINGS | LBS_NOINTEGRALHEIGHT,
            0, 0, 10, 10, h, (HMENU)IDC_LIST, g_hInst, NULL);

        g_hTitle = CreateWindowExW(0, L"STATIC", L"",
            WS_CHILD | WS_VISIBLE | SS_LEFT,
            0, 0, 10, 10, h, (HMENU)IDC_TITLE, g_hInst, NULL);
        SendMessageW(g_hTitle, WM_SETFONT, (WPARAM)g_fHead, 0);

        g_hMeta = CreateWindowExW(0, L"STATIC", L"",
            WS_CHILD | WS_VISIBLE | SS_LEFT,
            0, 0, 10, 10, h, (HMENU)IDC_META, g_hInst, NULL);
        SendMessageW(g_hMeta, WM_SETFONT, (WPARAM)g_fUI, 0);

        g_hDesc = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", L"",
            WS_CHILD | WS_VISIBLE | WS_VSCROLL | ES_MULTILINE |
            ES_READONLY | ES_AUTOVSCROLL,
            0, 0, 10, 10, h, (HMENU)IDC_DESC, g_hInst, NULL);
        SendMessageW(g_hDesc, WM_SETFONT, (WPARAM)g_fDesc, 0);

        g_hFLbl = CreateWindowExW(0, L"STATIC", L"TARGET FOLDER:",
            WS_CHILD | WS_VISIBLE | SS_LEFT,
            0, 0, 10, 10, h, (HMENU)IDC_FLBL, g_hInst, NULL);
        SendMessageW(g_hFLbl, WM_SETFONT, (WPARAM)g_fUI, 0);

        g_hPath = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", L"(no target selected)",
            WS_CHILD | WS_VISIBLE | ES_READONLY | ES_AUTOHSCROLL,
            0, 0, 10, 10, h, (HMENU)IDC_PATH, g_hInst, NULL);
        SendMessageW(g_hPath, WM_SETFONT, (WPARAM)g_fUI, 0);

        g_hBrowse = CreateWindowExW(0, L"BUTTON", L"BROWSE...",
            WS_CHILD | WS_VISIBLE | BS_OWNERDRAW | WS_TABSTOP,
            0, 0, 10, 10, h, (HMENU)IDC_BROWSE, g_hInst, NULL);

        for (i = 0; i < 3; i++) {
            g_hBtn[i] = CreateWindowExW(0, L"BUTTON", L"...",
                WS_CHILD | WS_VISIBLE | BS_OWNERDRAW | WS_TABSTOP,
                0, 0, 10, 10, h, (HMENU)(INT_PTR)(IDC_BTN0 + i), g_hInst, NULL);
        }

        g_hCLbl = CreateWindowExW(0, L"STATIC",
            L"// NEURAL LOG - THINKING MODE",
            WS_CHILD | WS_VISIBLE | SS_LEFT,
            0, 0, 10, 10, h, (HMENU)IDC_CLBL, g_hInst, NULL);
        SendMessageW(g_hCLbl, WM_SETFONT, (WPARAM)g_fHead, 0);

        g_hClear = CreateWindowExW(0, L"BUTTON", L"CLEAR",
            WS_CHILD | WS_VISIBLE | BS_OWNERDRAW | WS_TABSTOP,
            0, 0, 10, 10, h, (HMENU)IDC_CLEAR, g_hInst, NULL);

        g_hConsole = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", L"",
            WS_CHILD | WS_VISIBLE | WS_VSCROLL | ES_MULTILINE |
            ES_READONLY | ES_AUTOVSCROLL,
            0, 0, 10, 10, h, (HMENU)IDC_CONSOLE, g_hInst, NULL);
        SendMessageW(g_hConsole, WM_SETFONT, (WPARAM)g_fMono, 0);
        SendMessageW(g_hConsole, EM_SETLIMITTEXT, 0, 0);

        g_hStatus = CreateWindowExW(0, L"STATIC", L"booting...",
            WS_CHILD | WS_VISIBLE | SS_LEFT,
            0, 0, 10, 10, h, (HMENU)IDC_STATUS, g_hInst, NULL);
        SendMessageW(g_hStatus, WM_SETFONT, (WPARAM)g_fUI, 0);

        /* populate list */
        for (i = 0; i < N_MODS; i++) {
            int pos = (int)SendMessageW(g_hList, LB_ADDSTRING, 0,
                                        (LPARAM)MODS[i].title);
            SendMessageW(g_hList, LB_SETITEMDATA, pos, (LPARAM)i);
        }
        SendMessageW(g_hList, LB_SETCURSEL, 0, 0);

        /* staging dir */
        GetTempPathW(MAX_PATH - 20, g_tempdir);
        {
            size_t L = wcslen(g_tempdir);
            if (L && g_tempdir[L - 1] != L'\\' && L + 1 < MAX_PATH) {
                g_tempdir[L] = L'\\'; g_tempdir[L + 1] = 0;
            }
            wcsncat(g_tempdir, L"PolarisKit\\", MAX_PATH - wcslen(g_tempdir) - 1);
        }
        CreateDirectoryW(g_tempdir, NULL);

        g_isAdmin = is_admin();
        {
            wchar_t ab[160];
            _snwprintf(ab, 150, L"token: %ls // elevate per-action via UAC",
                       g_isAdmin ? L"ADMIN" : L"STANDARD");
            SetWindowTextW(g_hAdmin, ab);
        }

        refresh_details();

        /* boot banner */
        {
            unsigned total = 0;
            int k;
            for (k = 0; k < R_COUNT; k++) total += RES_TABLE[k].len;
            nlog(L"================================================================");
            nlog(L"POLARIS-VOID // CYBER TOOLKIT v1.0");
            nlog(L"%d modules loaded :: %d payloads embedded (%u bytes, byte-exact)",
                 N_MODS, R_COUNT, total);
            nlog(L"neural link: ESTABLISHED :: thinking mode: ON");
            nlog(L"staging bay :: %ls", g_tempdir);
            nlog(L"================================================================");
            nlog(L"[TIP] pick a module, optionally lock a target folder, hit an action.");
            nlog(L"[TIP] magenta edge = needs ADMIN (UAC will ask). double-click = run #1.");
        }
        SetTimer(h, IDT_CLOCK, 1000, NULL);
        return 0;
    }
    case WM_SIZE:
        do_layout(LOWORD(l), HIWORD(l));
        return 0;
    case WM_GETMINMAXINFO: {
        MINMAXINFO* mm = (MINMAXINFO*)l;
        mm->ptMinTrackSize.x = 1020;
        mm->ptMinTrackSize.y = 680;
        return 0;
    }
    case WM_MEASUREITEM: {
        MEASUREITEMSTRUCT* mi = (MEASUREITEMSTRUCT*)l;
        if (w == IDC_LIST) mi->itemHeight = 40;
        return TRUE;
    }
    case WM_DRAWITEM: {
        DRAWITEMSTRUCT* d = (DRAWITEMSTRUCT*)l;
        if (w == IDC_LIST) draw_list_item(d);
        else draw_button(d);
        return TRUE;
    }
    case WM_CTLCOLORSTATIC:
    case WM_CTLCOLOREDIT:
    case WM_CTLCOLORLISTBOX: {
        HDC hdc = (HDC)w;
        HWND ctl = (HWND)l;
        int id = GetDlgCtrlID(ctl);
        COLORREF fg = C_TXT, bg = C_BG;
        HBRUSH br = g_brBg;
        switch (id) {
        case IDC_CONSOLE: fg = C_GRN; bg = C_BLACK; br = g_brBlack; break;
        case IDC_DESC:    fg = C_TXT; bg = C_PANEL; br = g_brPanel; break;
        case IDC_PATH:    fg = C_CYAN; bg = C_DARK; br = g_brDark; break;
        case IDC_HEAD:    fg = C_CYAN; bg = C_BG; br = g_brBg; break;
        case IDC_TITLE:   fg = RGB(235,250,255); bg = C_BG; br = g_brBg; break;
        case IDC_META:    fg = C_AMBER; bg = C_BG; br = g_brBg; break;
        case IDC_SUB:
        case IDC_FLBL:    fg = C_GRAY; bg = C_BG; br = g_brBg; break;
        case IDC_CLBL:    fg = C_GRN; bg = C_BG; br = g_brBg; break;
        case IDC_ADMIN:   fg = g_isAdmin ? C_GRN : C_AMBER; bg = C_BG; br = g_brBg; break;
        case IDC_STATUS:  fg = C_MAG; bg = C_PANEL; br = g_brPanel; break;
        case 2001:        fg = C_MAG; bg = C_BG; br = g_brBg; break;
        default:          fg = C_TXT; bg = C_BG; br = g_brBg; break;
        }
        SetTextColor(hdc, fg);
        SetBkColor(hdc, bg);
        return (LRESULT)br;
    }
    case WM_COMMAND: {
        int id = LOWORD(w), ev = HIWORD(w);
        if (id == IDC_LIST && ev == LBN_SELCHANGE) {
            int s = (int)SendMessageW(g_hList, LB_GETCURSEL, 0, 0);
            if (s >= 0 && s < N_MODS) {
                g_mod = (int)SendMessageW(g_hList, LB_GETITEMDATA, s, 0);
                if (g_mod < 0 || g_mod >= N_MODS) g_mod = 0;
                refresh_details();
                nlog(L"[NAV] module %02d/%02d :: %ls", g_mod + 1, N_MODS,
                     MODS[g_mod].id);
            }
            return 0;
        }
        if (id == IDC_LIST && ev == LBN_DBLCLK) {
            if (MODS[g_mod].nActs > 0) start_action(g_mod, 0);
            return 0;
        }
        if ((id == IDC_BTN0 || id == IDC_BTN1 || id == IDC_BTN2) &&
            (ev == BN_CLICKED || ev == BN_DOUBLECLICKED)) {
            int a = id - IDC_BTN0;
            if (a < MODS[g_mod].nActs) start_action(g_mod, a);
            return 0;
        }
        if (id == IDC_BROWSE && ev == BN_CLICKED) { pick_folder(); return 0; }
        if (id == IDC_GITHUB && ev == BN_CLICKED) {
            ShellExecuteW(h, L"open", L"https://github.com/Polaris-Void",
                          NULL, NULL, SW_SHOWNORMAL);
            nlog(L"[ OK ] browser launched :: github.com/Polaris-Void");
            return 0;
        }
        if (id == IDC_CLEAR && ev == BN_CLICKED) {
            SetWindowTextW(g_hConsole, L"");
            nlog(L"[SYS] neural log purged.");
            return 0;
        }
        return 0;
    }
    case WM_TIMER:
        if (w == IDT_THINK) {
            if (g_thinkStep < g_thinkTotal) {
                nlog(L"%ls", g_think[g_thinkStep++]);
            } else {
                KillTimer(h, IDT_THINK);
                dispatch_pending();
            }
            return 0;
        }
        if (w == IDT_MON) {
            if (g_hProc) {
                DWORD code = 0;
                if (GetExitCodeProcess(g_hProc, &code) && code != STILL_ACTIVE) {
                    KillTimer(h, IDT_MON);
                    CloseHandle(g_hProc);
                    g_hProc = NULL;
                    if (code == 0) {
                        nlog(L"[ OK ] process exited clean :: code 0");
                        set_status_state(L"done :: exit 0");
                    } else {
                        nlog(L"[WARN] process ended :: exit code %u (see tool window)",
                             (unsigned)code);
                        set_status_state(L"done :: non-zero exit");
                    }
                }
            } else {
                KillTimer(h, IDT_MON);
            }
            return 0;
        }
        if (w == IDT_CLOCK) {
            SYSTEMTIME st;
            wchar_t s[320];
            GetLocalTime(&st);
            _snwprintf(s, 310, L"  ONLINE %02d:%02d:%02d  |  %ls",
                       st.wHour, st.wMinute, st.wSecond, g_state);
            SetWindowTextW(g_hStatus, s);
            return 0;
        }
        return 0;
    case WM_CLOSE:
        DestroyWindow(h);
        return 0;
    case WM_DESTROY:
        if (g_hProc) { CloseHandle(g_hProc); g_hProc = NULL; }
        KillTimer(h, IDT_THINK); KillTimer(h, IDT_MON); KillTimer(h, IDT_CLOCK);
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcW(h, m, w, l);
}

int WINAPI wWinMain(HINSTANCE hi, HINSTANCE hp, LPWSTR cl, int cs) {
    WNDCLASSEXW wc;
    HWND h;
    MSG msg;
    (void)hp; (void)cl; (void)cs;
    g_hInst = hi;
    SetProcessDPIAware();
    OleInitialize(NULL);

    memset(&wc, 0, sizeof(wc));
    wc.cbSize = sizeof(wc);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hi;
    wc.hCursor = LoadCursorW(NULL, IDC_ARROW);
    wc.hbrBackground = CreateSolidBrush(C_BG);
    wc.lpszClassName = L"PolarisCyberKit";
    wc.hIcon = LoadIconW(hi, MAKEINTRESOURCEW(IDI_APP));
    wc.hIconSm = LoadIconW(hi, MAKEINTRESOURCEW(IDI_APP));
    if (!RegisterClassExW(&wc)) {
        MessageBoxW(NULL, L"RegisterClass failed.", L"PolarisKit", MB_ICONERROR);
        return 1;
    }
    h = CreateWindowExW(0, L"PolarisCyberKit",
        L"POLARIS-VOID // CYBER TOOLKIT",
        WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN,
        CW_USEDEFAULT, CW_USEDEFAULT, 1180, 780,
        NULL, NULL, hi, NULL);
    if (!h) {
        MessageBoxW(NULL, L"CreateWindow failed.", L"PolarisKit", MB_ICONERROR);
        return 1;
    }
    ShowWindow(h, SW_SHOW);
    UpdateWindow(h);
    while (GetMessageW(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
    OleUninitialize();
    return (int)msg.wParam;
}
#endif /* POLARIS_TEST_HARNESS */
