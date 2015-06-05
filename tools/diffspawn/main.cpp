#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

static void PrintHelp(char *program)
{
    printf("--> %%ProgramFiles%%\\Rational\\ClearCase\\lib\\mgrs\\map -->\n"
            "    text_file_delta     compare  <path>\\%s\n"
            "    text_file_delta     xcompare <path>\\%s\n",
            program, program);
}

static char *GetUserBatchFile()
{
    static char s_szBatchFile[MAX_PATH] = { 0 };
    if (0 == s_szBatchFile[0])
    {
        if (0 == GetModuleFileName(0, s_szBatchFile, MAX_PATH))
        {
            return NULL;
        }

        char *p = strrchr(s_szBatchFile, '.');
        if (NULL == p)
        {
            return NULL;
        }

        p++;
        strcpy(p, "bat");
    }
    return s_szBatchFile;
}

int main(int argc, char *argv[])
{
    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    char buf[MAX_PATH * 3] = { 0 };
    char *p;

    if (argc < 7)
    {
        PrintHelp(argv[0]);
        return 0;
    }

    p = GetUserBatchFile();
    if (NULL == p)
    {
        return 0;
    }

    /* Create the process */
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    strcpy(buf, p);
    for (int i = 1; i < argc; i++)
    {
        strcat(buf, " ");
        strcat(buf, argv[i]);
    }

    if (!CreateProcess(NULL, buf, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi))
    {
        return 0;
    }

    /* Close process and thread handles */
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return 0;
}
