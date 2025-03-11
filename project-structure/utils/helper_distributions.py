def show_freqs(df, keys):
    # distribution of keys in the order of counts
    dx = df.groupBy(keys).count().toPandas()
    dx = dx.sort_values('count', ascending=True)
    dx['frac'] = dx['count']/dx['count'].sum()
    dx['cum_frac'] = dx['frac'].cumsum()
    return dx


def show_freqs_ordered(df, keys):
    # distribution of keys in the order of keys
    dx = df.groupBy(keys).count().toPandas()
    dx = dx.sort_values(keys, ascending=True)
    dx['frac'] = dx['count']/dx['count'].sum()
    dx['cum_frac'] = dx['frac'].cumsum()
    return dx
