#define IN6ADDRSZ   16
#define INADDRSZ    4
#define INT16SZ     2

static int inet_pton4(const char *src, unsigned char *dst);
static int inet_pton6(const char *src, unsigned char *dst);

static int inet_pton(int af, const char *src, void *dst)
{
    switch (af)
    {
        case AF_INET:
            return (inet_pton4(src, (unsigned char *)dst));

        case AF_INET6:
            return (inet_pton6(src, (unsigned char *)dst));

        default:
            break;
    }
    return -1;
}

static int inet_pton4(const char *src, unsigned char *dst)
{
    static const char digits[] = "0123456789";
    int saw_digit, octets, ch;
    unsigned char tmp[INADDRSZ], *tp;

    saw_digit = 0;
    octets = 0;
    tp = tmp;
    *tp = 0;
    while ((ch = *src++) != '\0')
    {
        const char *pch;

        if ((pch = strchr(digits, ch)) != NULL)
        {
            unsigned int val = *tp * 10 + (unsigned int)(pch - digits);

            if (val > 255)
                return (0);
            *tp = (unsigned char)val;
            if (! saw_digit)
            {
                if (++octets > 4)
                    return (0);
                saw_digit = 1;
            }
        }
        else if (ch == '.' && saw_digit)
        {
            if (octets == 4)
                return (0);
            *++tp = 0;
            saw_digit = 0;
        }
        else
            return (0);
    }
    if (octets < 4)
        return (0);

    memcpy(dst, tmp, INADDRSZ);
    return (1);
}

static int inet_pton6(const char *src, unsigned char *dst)
{
    static const char xdigits_l[] = "0123456789abcdef",
            xdigits_u[] = "0123456789ABCDEF";
    unsigned char tmp[IN6ADDRSZ], *tp, *endp, *colonp;
    const char *xdigits, *curtok;
    int ch, saw_xdigit;
    unsigned int val;

    memset((tp = tmp), 0, IN6ADDRSZ);
    endp = tp + IN6ADDRSZ;
    colonp = NULL;
    /* Leading :: requires some special handling. */
    if (*src == ':')
        if (*++src != ':')
            return (0);
    curtok = src;
    saw_xdigit = 0;
    val = 0;
    while ((ch = *src++) != '\0')
    {
        const char *pch;

        if ((pch = strchr((xdigits = xdigits_l), ch)) == NULL)
            pch = strchr((xdigits = xdigits_u), ch);
        if (pch != NULL)
        {
            val <<= 4;
            val |= (pch - xdigits);
            if (val > 0xffff)
                return (0);
            saw_xdigit = 1;
            continue;
        }
        if (ch == ':')
        {
            curtok = src;
            if (!saw_xdigit)
            {
                if (colonp)
                    return (0);
                colonp = tp;
                continue;
            }
            if (tp + INT16SZ > endp)
                return (0);
            *tp++ = (unsigned char)(val >> 8) & 0xff;
            *tp++ = (unsigned char) val & 0xff;
            saw_xdigit = 0;
            val = 0;
            continue;
        }
        if (ch == '.' && ((tp + INADDRSZ) <= endp) &&
                inet_pton4(curtok, tp) > 0)
        {
            tp += INADDRSZ;
            saw_xdigit = 0;
            break;    /* '\0' was seen by inet_pton4(). */
        }
        return (0);
    }
    if (saw_xdigit)
    {
        if (tp + INT16SZ > endp)
            return (0);
        *tp++ = (unsigned char)(val >> 8) & 0xff;
        *tp++ = (unsigned char) val & 0xff;
    }
    if (colonp != NULL)
    {
        /*
         * Since some memmove()'s erroneously fail to handle
         * overlapping regions, we'll do the shift by hand.
         */
        const int n = tp - colonp;
        int i;

        for (i = 1; i <= n; i++)
        {
            endp[- i] = colonp[n - i];
            colonp[n - i] = 0;
        }
        tp = endp;
    }
    if (tp != endp)
        return (0);

    memcpy(dst, tmp, IN6ADDRSZ);
    return (1);
}
