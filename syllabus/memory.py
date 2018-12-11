
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

    units = [
        (10**21, 'ZB'), (10**18, 'EB'),
        (10**15, 'PB'), (10**12, 'TB'),
        (10**9, 'GB'), (10**6, 'MB'),
        (10**3, 'KB'), (10**0, 'B')]

    for r in units:
        if s > r[0]:
            return (s / r[0], r[1])
    return (0, 'NULL')
