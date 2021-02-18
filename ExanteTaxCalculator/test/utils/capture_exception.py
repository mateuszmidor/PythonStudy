def capture_exception(f, *args):
    """ unittest helper. call f and return exception or None """
    
    try:
        f(*args)
    except Exception as e:
        return e

    return None