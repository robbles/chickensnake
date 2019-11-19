def clone(obj: dict, **kwargs):
    obj = obj.copy()
    obj.update(kwargs)
    return obj
