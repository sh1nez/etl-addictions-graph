from sqlglot import parse


def safe_parse(sql):
    try:
        return parse(sql, dialect="postgres"), "postgres"
    except:  # catch error
        pass

    try:
        return parse(sql, dialect="oracle"), "oracle"
    except:
        pass

    return None, "Unknown"
