

SIZE_UNITS = [
    (10**21, 'ZB'), (10**18, 'EB'),
    (10**15, 'PB'), (10**12, 'TB'),
    (10**9, 'GB'), (10**6, 'MB'),
    (10**3, 'KB'), (10**0, 'B')]


TIME_UNITS = [
    (10**-12, 'ps'), (10**-9, 'ns'),
    (10**-6, 'us'), (10**-3, 'ms'),
    (10**0, 's')
]


def size_fmt(s):
    """Scale and get units for a size s, in Bytes

    Parameters
    ----------
    s : int
        size, in bytes

    Returns
    -------
    (int, str)
        [0] : scaled size; 0-1000 for sizes < 10**24 (1YB)
        [1] : units; B, KB, MB, etc. If size == 0, returns 'NULL'
    """

    for r in SIZE_UNITS:
        if s > r[0]:
            return (s / r[0], r[1])
    return (0, 'NULL')


def time_fmt(t):
    """Scale and get units for a time t, in seconds

    Parameters
    ----------
    t : float
        time, in seconds

    Returns
    -------
    (float, str)
        [0] : scaled time
        [1] : units; s, ms, us, ns, etc.
    """

    for r in TIME_UNITS:
        if t < r[0] * 10**2:
            return (t / r[0], r[1])
    return (t, 's')
