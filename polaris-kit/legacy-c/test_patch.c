/* Linux-native self-test: patch engine + embedded payload integrity.
 * Compile: gcc -DPOLARIS_TEST_HARNESS -o /tmp/t test_patch.c && /tmp/t
 * Includes the REAL polaris_kit.c core (patch_dp0 + resources.h). */
#include "polaris_kit.c"

static int fails = 0;
#define CHECK(c, msg) do { \
    if (c) { printf("PASS: %s\n", msg); } \
    else { printf("FAIL: %s\n", msg); fails++; } } while (0)

static const char* FNAMES[] = {
    "Windows-No-Internet-Fix__Restart_Network_Service.bat",
    "Windows-No-Internet-Fix__Disable_Internet_Probing.reg",
    "Windows-No-Internet-Fix__Enable_Internet_Probing.reg",
    "Win-User-Backup__Backup.bat",
    "Win-User-Backup__Restore.bat",
    "Win-Spotlight-Icon-Toggle__Hide_Learn_about_this_picture.reg",
    "Win-Spotlight-Icon-Toggle__Show_Learn_about_this_picture.reg",
    "Win-Drv-Backup__Backup-Drivers.bat",
    "Win-Drv-Backup__Restore-Drivers.bat",
    "Win-Display-Drv-Backup__Backup.bat",
    "Win-Display-Drv-Backup__Restore.bat",
    "USB-Immunizer-Customizer__Prevent_Automatic_Folder_Creation_on_USB_Drive.bat",
    "USB-Immunizer-Customizer__.autorun.ico",
    "Reset-DNS-Proxy__Reset-DNS-Proxy.bat",
    "Image-Video-Renamer__Image_to_JPG_Renamer.bat",
    "Image-Video-Renamer__Video_to_MP4_Renamer.bat",
    "Directory-Tree-Exporter__Directory-Tree-Exporter.bat",
    "Directory-SHA256-Tree-Exporter__Directory-SHA256-Tree-Exporter.bat",
    "Unpack-Subfolders__Unpack-Subfolders.bat",
};

int main(void) {
    int i;
    char msg[256];
    /* 1. integrity: embedded bytes == raw files on disk */
    CHECK(R_COUNT == 19, "resource count == 19");
    for (i = 0; i < R_COUNT; i++) {
        char path[512];
        FILE* f; long sz; unsigned char* buf; size_t rd;
        snprintf(path, sizeof(path), "../assets/raw/%s", FNAMES[i]);
        f = fopen(path, "rb");
        snprintf(msg, sizeof(msg), "open raw %s", FNAMES[i]);
        CHECK(f != NULL, msg);
        if (!f) continue;
        fseek(f, 0, SEEK_END); sz = ftell(f); fseek(f, 0, SEEK_SET);
        buf = malloc(sz > 0 ? (size_t)sz : 1);
        rd = fread(buf, 1, (size_t)sz, f); fclose(f);
        snprintf(msg, sizeof(msg), "len match %s (%ld vs %u)",
                 FNAMES[i], sz, RES_TABLE[i].len);
        CHECK(rd == (size_t)sz && sz == (long)RES_TABLE[i].len, msg);
        snprintf(msg, sizeof(msg), "bytes identical %s", FNAMES[i]);
        CHECK(memcmp(buf, RES_TABLE[i].data, (size_t)sz) == 0, msg);
        free(buf);
    }
    /* 2. patch engine: folder scripts */
    {
        int ids[] = { R_USB_TOOL, R_IMGREN, R_VIDREN, R_TREE, R_SHA256, R_UNPACK };
        const char* tgt = "D:\\Demo\\Sub\\";
        for (i = 0; i < 6; i++) {
            size_t outlen = 0;
            unsigned char* out = patch_dp0(RES_TABLE[ids[i]].data,
                                           RES_TABLE[ids[i]].len, tgt, &outlen);
            snprintf(msg, sizeof(msg), "patch ok resid %d (in=%u out=%u)",
                     ids[i], RES_TABLE[ids[i]].len, (unsigned)outlen);
            CHECK(out != NULL && outlen > RES_TABLE[ids[i]].len, msg);
            if (out) {
                int k, foundNeedle = 0, foundTarget = 0;
                for (k = 0; k + 5 <= (int)outlen; k++)
                    if (memcmp(out + k, "%~dp0", 5) == 0) foundNeedle = 1;
                for (k = 0; k + (int)strlen(tgt) <= (int)outlen; k++)
                    if (memcmp(out + k, tgt, strlen(tgt)) == 0) foundTarget = 1;
                snprintf(msg, sizeof(msg), "no %%~dp0 left resid %d", ids[i]);
                CHECK(!foundNeedle, msg);
                snprintf(msg, sizeof(msg), "target injected resid %d", ids[i]);
                CHECK(foundTarget, msg);
                free(out);
            }
        }
    }
    /* 3. patch engine: no-op on scripts without needle
     * (R_DRVBACKUP uses %SystemDrive%, has no %~dp0) */
    {
        size_t outlen = 0;
        unsigned char* out = patch_dp0(RES_TABLE[R_DRVBACKUP].data,
                                       RES_TABLE[R_DRVBACKUP].len,
                                       "C:\\Longer\\Target\\Path\\", &outlen);
        CHECK(out != NULL && outlen == RES_TABLE[R_DRVBACKUP].len,
              "no-needle script unchanged in length");
        if (out) {
            CHECK(memcmp(out, RES_TABLE[R_DRVBACKUP].data, outlen) == 0,
                  "no-needle script byte-identical");
            free(out);
        }
    }
    /* 4. DNS script DOES contain one pushd %~dp0 (cosmetic cwd) */
    {
        size_t outlen = 0;
        const char* tgt = "C:\\Longer\\Target\\Path\\";
        unsigned char* out = patch_dp0(RES_TABLE[R_DNSRESET].data,
                                       RES_TABLE[R_DNSRESET].len, tgt, &outlen);
        CHECK(out != NULL && outlen > RES_TABLE[R_DNSRESET].len,
              "needle script grows with longer target");
        if (out) {
            int k, foundNeedle = 0;
            for (k = 0; k + 5 <= (int)outlen; k++)
                if (memcmp(out + k, "%~dp0", 5) == 0) foundNeedle = 1;
            CHECK(!foundNeedle, "no %~dp0 left in DNS script");
            free(out);
        }
    }
    printf(fails ? "\nRESULT: %d FAILURES\n" : "\nRESULT: ALL GREEN\n", fails);
    return fails ? 1 : 0;
}
