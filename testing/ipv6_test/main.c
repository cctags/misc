#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32

#include <winsock2.h>
#include <ws2tcpip.h>
#include "inet_pton.c"

static HANDLE s_hThread = 0;
static int s_nThreadQuitFlag = 0;

#else

#include <ctype.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <signal.h>

#endif /* _WIN32 */

#define DEFAULT_PORT 8000               /* 默认端口号 */
#define BUFFER_LENGTH 4096              /* 缓冲区大小 */
#define ROOM_LIMIT 1024                 /* 客户端连接个数 */
#define NAME_LIMIT 32                   /* 客户端别名长度 */
#define NAME_B_LIMIT (NAME_LIMIT + 2)

#define SERVER_TERMINATE 0              /* Server quit */

static int s_nSocketFileDescriptor = -1;
static int s_nSocketFileDescriptor4 = -1;
static int s_nNewSocketFileDescriptor = -1;
static int s_nMaxFd = 3;

static void SafeQuit(int return_code)
{
    int fd;
    for (fd = 3; fd <= s_nMaxFd; fd++)
    {
        close(fd);
    }
    s_nMaxFd = 3;
    exit(return_code);
}

static void MakeBuffer(
    /* [in, out] */ char *pBuffer)
{
    int n = 0;

    if (NULL == pBuffer)
    {
        return;
    }

    if (1 != sscanf(pBuffer, "<<<%d", &n))
    {
        return;
    }

    if ((n <= 8) || (n >= BUFFER_LENGTH))
    {
        return;
    }

    memset(pBuffer, '.', n);

    pBuffer[0] = 'A';
    pBuffer[1] = 'B';
    pBuffer[2] = 'C';
    pBuffer[3] = 'D';

    pBuffer[n - 5] = 'W';
    pBuffer[n - 4] = 'X';
    pBuffer[n - 3] = 'Y';
    pBuffer[n - 2] = 'Z';

    pBuffer[n - 1] = 0;
}

#ifndef _WIN32

static void ExceptionHandler(int signal)
{
    int fileDescriptor;

    switch (signal)
    {
        case SIGTERM:
            printf("\nReceived kill signal. Shutting down.\n");
            break;
        case SIGSEGV:
            printf("\nDamn, we segfaulted! Shutting down.\n");
            break;
        case SIGINT:
            printf("\nReceived keyboard interrupt. Shutting down.\n");
            break;
        default:
            break;
    }

    for (fileDescriptor = 3; fileDescriptor <= s_nMaxFd; fileDescriptor++)
    {
        close(fileDescriptor);
    }

    exit(0);
}

#else

static BOOL WINAPI HandlerRoutine(DWORD dwCtrlType)
{
    if (dwCtrlType == CTRL_BREAK_EVENT || dwCtrlType == CTRL_C_EVENT)
    {
        SafeQuit(1);
        return TRUE;
    }
    return FALSE;
}

static DWORD WINAPI HandleUserInputThread(LPVOID lpParameter)
{
    HANDLE hStdin;
    DWORD dwWait;
    char buffer[BUFFER_LENGTH];

    hStdin = GetStdHandle(STD_INPUT_HANDLE);
    if (INVALID_HANDLE_VALUE == hStdin)
    {
        printf("GetStdHandle failed, ec = %d\n", GetLastError());
        SafeQuit(1);
    }

    while (1)
    {
        if (s_nThreadQuitFlag)
        {
            break;
        }

        dwWait = WaitForSingleObject(hStdin, 100);
        if (WAIT_OBJECT_0 == dwWait)
        {
            gets(buffer);

            if (strlen(buffer) == 0)
            {
                continue;
            }

            MakeBuffer(buffer);

            if (send(s_nSocketFileDescriptor, buffer, strlen(buffer), 0) <= 0)
            {
                break;
            }
        }
    }

    return 0;
}

#endif /* _WIN32 */

static void DisconnectShutdown(int code)
{
    /* The remote host is no longer connected. */
    int fileDescriptor;

    for (fileDescriptor = 3; fileDescriptor <= s_nMaxFd; fileDescriptor++)
    {
        close(fileDescriptor);
    }

    switch (code)
    {
        case SERVER_TERMINATE:
            printf("\nThe server has terminated the session.\n");
            break;

        default:
            printf("\nRemote host disconnected. Shutting down.\n");
            break;
    }

    exit(0);
}

static void RunAsClient(char *hostname, int port, char nickname[])
{
    struct sockaddr_in6 socketAddress6;
    struct sockaddr_in socketAddress4;
    char buffer[BUFFER_LENGTH];
    int numActiveFDs, fileDescriptor;
    fd_set readSet, testSet;
    int is_ipv6 = 1;

    if ((NULL == hostname) || (0 == hostname[0]))
    {
        printf("*Error*: invalid hostname.\n");
        SafeQuit(1);
    }

    if (NULL != strchr(hostname, '.'))
    {
        is_ipv6 = 0;
    }

    if (is_ipv6)
    {
        /* Build address data structure. */
        memset((char *)&socketAddress6, 0, sizeof(socketAddress6));
        socketAddress6.sin6_family = AF_INET6;
        if (inet_pton(AF_INET6, hostname, &socketAddress6.sin6_addr) < 0)
        {
            perror(hostname);
            SafeQuit(1);
        }
        socketAddress6.sin6_port = htons(port);

        /* Active open. */
        if ((s_nSocketFileDescriptor = socket(AF_INET6, SOCK_STREAM, 0)) < 0)
        {
            perror("chat: socket6");
            SafeQuit(1);
        }

        if (connect(s_nSocketFileDescriptor, (struct sockaddr *)&socketAddress6,
                sizeof(socketAddress6)) < 0)
        {
            perror("chat: connect6");
            close(s_nSocketFileDescriptor);
            SafeQuit(1);
        }
    }
    else
    {
        /* Build address data structure. */
        memset((char *)&socketAddress4, 0, sizeof(socketAddress4));
        socketAddress4.sin_family = AF_INET;
        socketAddress4.sin_addr.s_addr = inet_addr(hostname);
        socketAddress4.sin_port = htons(port);

        /* Active open. */
        if ((s_nSocketFileDescriptor = socket(AF_INET, SOCK_STREAM, 0)) < 0)
        {
            perror("chat: socket4");
            SafeQuit(1);
        }

        if (connect(s_nSocketFileDescriptor, (struct sockaddr *)&socketAddress4,
                sizeof(socketAddress4)) < 0)
        {
            perror("chat: connect4");
            close(s_nSocketFileDescriptor);
            SafeQuit(1);
        }
    }

    /* Keep track of the largest file descriptor. */
    s_nMaxFd = s_nSocketFileDescriptor;

    FD_ZERO(&readSet);
    FD_SET(s_nSocketFileDescriptor, &readSet);
#ifndef _WIN32
    FD_SET(0, &readSet);
#endif /* _WIN32 */

    printf("***Connection established.***\n");

    /* Send the nickname. */
    memset(buffer, 0, sizeof(buffer));
    strcat(nickname, ": ");
    send(s_nSocketFileDescriptor, nickname, strlen(nickname), 0);
    recv(s_nSocketFileDescriptor, buffer, sizeof(buffer), 0);

#ifdef _WIN32
    s_hThread = CreateThread(NULL, 0, HandleUserInputThread, NULL, 0, NULL);
    if (NULL == s_hThread)
    {
        printf("CreateThread failed, ec = %d\n", GetLastError());
        SafeQuit(1);
    }
#endif

    while (1)
    {
        testSet = readSet;
        numActiveFDs = select((s_nMaxFd + 1), &testSet, (fd_set *)0,
                (fd_set *)0, (struct timeval *)0);
        if (numActiveFDs == -1)
        {
            perror("chat: select");
            SafeQuit(1);
        }

        for (fileDescriptor = 0; fileDescriptor <= s_nMaxFd; fileDescriptor++)
        {
            if (!FD_ISSET(fileDescriptor, &testSet))
            {
                continue;
            }

            if (fileDescriptor == s_nSocketFileDescriptor)
            {
                memset(buffer, 0, sizeof(buffer));
                if (recv(s_nSocketFileDescriptor, buffer, sizeof(buffer), 0) <= 0)
                {
                    DisconnectShutdown(SERVER_TERMINATE);
                }
                printf("%s\n", buffer);
            }
            else if (fileDescriptor == 0)
            {
                gets(buffer);
                MakeBuffer(buffer);
                send(s_nSocketFileDescriptor, buffer, strlen(buffer), 0);
            }
        }
    }
}

static void RunAsServer(int port, char nickname[], int connectionLimit)
{
    struct sockaddr_in6 socketAddress6;
    struct sockaddr_in socketAddress4;
    int length, numActiveFDs, fileDescriptor, fd_write, index, strlength;
    fd_set readSet, testSet;
    char NickNames[ROOM_LIMIT][NAME_B_LIMIT];
    char sendBuffer[BUFFER_LENGTH + NAME_B_LIMIT], buffer[BUFFER_LENGTH];
#ifdef _WIN32
    struct in_addr6 in6addr_any = { 0 };
#endif

    for (index = 0; index < ROOM_LIMIT; index++)
    {
        NickNames[index][0] = '\0';
    }

    /* Put the server's nickname in the list. */
    strcat(nickname, ": ");
    strcpy(NickNames[0], nickname);

    /* Set up the address struct. */
    memset((char *)&socketAddress6, 0, sizeof(socketAddress6));
    socketAddress6.sin6_family = AF_INET6;
    socketAddress6.sin6_addr = in6addr_any;
    socketAddress6.sin6_port = htons(port);

    memset((char *)&socketAddress4, 0, sizeof(socketAddress4));
    socketAddress4.sin_family = AF_INET;
    socketAddress4.sin_addr.s_addr = INADDR_ANY;
    socketAddress4.sin_port = htons(port - 1);

    /* Create a socket. */
    if ((s_nSocketFileDescriptor = socket(AF_INET6, SOCK_STREAM, 0)) < 0)
    {
        perror("chat: socket6");
        SafeQuit(1);
    }

    if ((s_nSocketFileDescriptor4 = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        perror("chat: socket4");
        SafeQuit(1);
    }

    /* Keep track of the largest file descriptor. */
    s_nMaxFd = s_nSocketFileDescriptor;
    if (s_nMaxFd < s_nSocketFileDescriptor4)
    {
        s_nMaxFd = s_nSocketFileDescriptor4;
    }

    /* Name the socket. */
    if ((bind(s_nSocketFileDescriptor, (struct sockaddr *)&socketAddress6, sizeof(socketAddress6))) < 0)
    {
        perror("chat: bind6");
        SafeQuit(1);
    }

    if ((bind(s_nSocketFileDescriptor4, (struct sockaddr *)&socketAddress4, sizeof(socketAddress4))) < 0)
    {
        perror("chat: bind4");
        SafeQuit(1);
    }

    /* Set up the connection queue. */
    listen(s_nSocketFileDescriptor, 5);
    listen(s_nSocketFileDescriptor4, 5);

    /* Initialize the file descriptor sets. */
    FD_ZERO(&readSet);
    FD_ZERO(&testSet);
    FD_SET(s_nSocketFileDescriptor, &readSet);
    FD_SET(s_nSocketFileDescriptor4, &readSet);

    /* The loop! */
    while (1)
    {
        testSet = readSet;  /* Use a copy of the set. */

        numActiveFDs = select((s_nMaxFd + 1), &testSet, (fd_set *)0,
                (fd_set *)0, (struct timeval *)0);

        if (numActiveFDs == -1)
        {
            perror("chat: select");
            SafeQuit(1);
        }

        for (fileDescriptor = 0; fileDescriptor <= s_nMaxFd; fileDescriptor++)
        {
            if (!FD_ISSET(fileDescriptor, &testSet))
            {
                continue;
            }

            if ((fileDescriptor == s_nSocketFileDescriptor) ||
                    (fileDescriptor == s_nSocketFileDescriptor4))
            {
                if (fileDescriptor == s_nSocketFileDescriptor)
                {
                    /* 接受一个IPv6的连接 */
                    if ((s_nNewSocketFileDescriptor = accept(
                                s_nSocketFileDescriptor,
                                (struct sockaddr *) & socketAddress6, &length)) < 0)
                    {
                        perror("chat: accept6");
                        SafeQuit(1);
                    }
                }
                else
                {
                    /* 接受一个IPv4的连接 */
                    if ((s_nNewSocketFileDescriptor = accept(
                                s_nSocketFileDescriptor4,
                                (struct sockaddr *) & socketAddress4, &length)) < 0)
                    {
                        perror("chat: accept4");
                        SafeQuit(1);
                    }
                }

                memset(buffer, 0, sizeof(buffer));
                recv(s_nNewSocketFileDescriptor, buffer, sizeof(buffer), 0);

                FD_SET(s_nNewSocketFileDescriptor, &readSet);

                /* Keep track of the largest file descriptor. */
                if (s_nNewSocketFileDescriptor > s_nMaxFd)
                    s_nMaxFd = s_nNewSocketFileDescriptor;
                printf("***New connection on socket.\n");
                strlength = (int) strlen(buffer);  /* Add the nickname to the table. */
                buffer[strlength] = '\0';
                strcpy(NickNames[s_nNewSocketFileDescriptor - 3], buffer);
                connectionLimit--;             /* Keep track of number of connections */

                send(s_nNewSocketFileDescriptor, "Ok.", sizeof("Ok."), 0);
            }
            else
            {
                memset(buffer, 0, sizeof(buffer));

                if (recv(fileDescriptor, buffer, sizeof(buffer), 0) <= 0)
                {
                    /* 某客户端退出 */
                    FD_CLR(fileDescriptor, &readSet);
                    if (fileDescriptor == s_nMaxFd) s_nMaxFd--;
                    connectionLimit++;
                    close(fileDescriptor);
                    printf("***Closed connection on socket.\n");
                    sendBuffer[0] = '\0';
                    strcpy(sendBuffer, "*** ");
                    strcat(sendBuffer, NickNames[fileDescriptor - 3]);
                    strcat(sendBuffer, "Goodbye!");
                    printf("%s\n", sendBuffer);
                    strlength = strlen(sendBuffer);
                    for (fd_write = 3; fd_write <= s_nMaxFd; fd_write++)
                    {
                        if (FD_ISSET(fd_write, &readSet) &&
                                (fd_write != s_nSocketFileDescriptor) &&
                                (fd_write != s_nSocketFileDescriptor4))
                        {
                            send(fd_write, sendBuffer, strlength, 0);
                        }
                    }
                    strcpy(NickNames[fileDescriptor - 3], "");
                }
                else
                {
                    /* 转发消息 */
                    sendBuffer[0] = '\0';
                    strcpy(sendBuffer, NickNames[fileDescriptor - 3]);
                    strcat(sendBuffer, buffer);
                    printf("%s\n", sendBuffer);
                    strlength = strlen(sendBuffer);
                    for (fd_write = 3; fd_write <= s_nMaxFd; fd_write++)
                    {
                        if (FD_ISSET(fd_write, &readSet) &&
                                (fd_write != s_nSocketFileDescriptor) &&
                                (fd_write != s_nSocketFileDescriptor4))
                        {
                            send(fd_write, sendBuffer, strlength, 0);
                        }
                    }
                }
            }
        }
    }
}

int main(int argc, char *argv[])
{
    int port, connectionLimit = -1;
    char nickname[NAME_B_LIMIT];
    int is_server = 0;
#ifdef _WIN32
    WSADATA wsaData;
    int nError;
#endif

    if (argc < 2)
    {
        fprintf(stderr, "usage: %s (<hostname> | --server) [port] [local identifier]\n", argv[0]);
        SafeQuit(1);
    }

#ifdef _WIN32
    nError = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (0 != nError)
    {
        printf("WSAStartup failed! ec = 0x%08x\n", WSAGetLastError());
        SafeQuit(1);
    }

    if (2 != LOBYTE(wsaData.wVersion) || 2 != HIBYTE(wsaData.wVersion))
    {
        printf("Not desired version!\n");
        SafeQuit(1);
    }

    if (!SetConsoleCtrlHandler(HandlerRoutine, TRUE))
    {
        printf("SetConsoleCtrlHandler failed, ec = %d\n", GetLastError());
        SafeQuit(1);
    }
#else
    signal(SIGINT, ExceptionHandler);
    signal(SIGTERM, ExceptionHandler);
    signal(SIGSEGV, ExceptionHandler);
#endif /* _WIN32 */

#ifdef _WIN32
    if (!stricmp(argv[1], "--server"))
#else
    if (!strcasecmp(argv[1], "--server"))
#endif
    {
        is_server = 1;
    }

    port = DEFAULT_PORT;

    if (argc >= 3)
    {
        port = atoi(argv[2]);
    }

    if (is_server)
    {
        strncpy(nickname, "Server", sizeof(nickname) - 1);
        RunAsServer(port, nickname, connectionLimit);
    }
    else
    {
        if (argc >= 4)
        {
            strncpy(nickname, argv[3], sizeof(nickname) - 1);
        }
        else
        {
            strcpy(nickname, "Client");
        }
        RunAsClient(argv[1], port, nickname);
    }

    return 0;
}
