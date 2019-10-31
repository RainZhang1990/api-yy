def update_dict2(dict2, key1, key2, val):
    if key1 in dict2:
        dict2[key1][key2] = val
    else:
        dict2[key1] = {key2: val}


def get_dict_value2(dict2, key1, key2, default):
    if key1 in dict2:
        return dict2[key1].get(key2, default)
    else:
        return default

def del_all_dict_value2(dict2, key1, key2):
    if key1 in dict2:
        del dict2[key1]
    for v in dict2.values():
        if key2 in v:
            del v[key2]
    return dict2