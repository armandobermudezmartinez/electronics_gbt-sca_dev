import logging
from math import floor, log
from copy import deepcopy
import yaml
from pathlib import Path


def blen(b):
    # number of bits in binary value
    try:
        return floor(log(b, 2))+1
    except ValueError:
        return 0


def hexb(b, l):
    return "{0:#0{1}x}".format(b, l)


def merge(a, b, path=None):
    "merges b into a"
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


def getFirstSetBitPosition(val):
    return int(log((val & -val), 2))


def update_dict(original: dict, update: dict, offset: bool = False,
                in_place: bool = False):
    """
    Update one multi level dictionary with another. If a key does not
    exist in the original, it is created. The updated dictionary is returned

    :param original: The unaltered dictionary
    :type original: dict
    :param update: The dictionary that will either overwrite or extend the
        original
    :type update: dict
    :param offset: If True, the values in the update dictionary will be
        interpreted as offsets to the values in the original dict. The
        resulting value will be original + update (this will be string
        concatenation if both the original and update values are strings)
    :type offset: bool
    :return: The extended/updated dict where the values that do not
        appear in the update dict are from the original dict, the keys that
        do appear in the update dict overwrite/extend the values in
        the original
    :rtype: dict
    :raises TypeError: If offset is set to true and the types don't match the
        addition of the values will cause a TypeError to be raised
    :raises ConfigPatchError: If lists are updated the length of the lists
        needs to match otherwise a error is raised
    """

    if in_place is True:
        result = original
    else:
        result = deepcopy(original)
    for update_key in update.keys():
        if update_key not in result.keys():
            if in_place is True:
                result[update_key] = update[update_key]
            else:
                result[update_key] = deepcopy(update[update_key])
            continue
        if not isinstance(result[update_key], type(update[update_key])):

            if in_place is True:
                result[update_key] = update[update_key]
            else:
                result[update_key] = deepcopy(update[update_key])
            continue
        if isinstance(result[update_key], dict):
            result[update_key] = update_dict(result[update_key],
                                             update[update_key],
                                             offset=offset,
                                             in_place=in_place)
        elif isinstance(result[update_key], list) or\
                isinstance(result[update_key], tuple):
            if len(result[update_key]) != len(update[update_key]):
                raise TypeError(
                    'If a list is a value of the dict the list'
                    ' lengths in the original and update need to'
                    ' match')
            patch = []
            for i, (orig_elem, update_elem) in enumerate(
                    zip(result[update_key], update[update_key])):
                if isinstance(orig_elem, dict):
                    patch.append(update_dict(result[update_key][i],
                                             update_elem,
                                             offset=offset,
                                             in_place=in_place))
                else:
                    if in_place is True:
                        patch.append(update_elem)
                    else:
                        patch.append(deepcopy(update_elem))
            if isinstance(result[update_key], tuple):
                patch = tuple(patch)
            result[update_key] = patch
        else:
            if offset is True:
                result[update_key] += update[update_key]
            else:
                if in_place is True:
                    result[update_key] = update[update_key]
                else:
                    result[update_key] = deepcopy(update[update_key])
    return result


def diff_dict(d1: dict, d2: dict) -> dict:
    """
    create the diff of two dictionaries.

    Create a dictionary containing all the keys that differ between
    d1 and d2 or that exist in d2 but not in d1. The value of the
    differing key will be the value found in d2.

    Example:
        With the inputs being
        d1 = {'a': 1, 'b': {'c': 2, 'f': 4}, 'e': 3}
        d2 = {'a': 2, 'b': {'c': 3, 'f': 4}, 'e': 3, 'g': 4}

        the resulting diff will be
        diff = {'a': 2, 'b': {'c':3}, 'g': 4}

        showing that the keys 'a' and 'b:c' are different and that the
        value in the differing d2 is 2 for a and 3 for 'b:c' respectively.
        As there is an entry in d2 that is not in d1 it will appear in the
        diff, however if there is an entry in d1 that is not in d2 it will
        not appear.

    This function is intended to find the patch that where applied on d1 to
    create d2. This may provide some motivation for the way that the function
    handles the different dictionaries
    """
    diff = {}
    for key2, value2 in d2.items():
        if key2 not in d1.keys():
            diff[key2] = value2
        elif isinstance(d1[key2], dict) and isinstance(value2, dict):
            potential_diff = diff_dict(d1[key2], value2)
            if potential_diff is not None:
                diff[key2] = potential_diff
        elif value2 != d1[key2]:
            diff[key2] = value2
    if diff == {}:
        return None
    return diff


def nested_dict_from_keylist(keys: list, value):
    """
    Given a list of keys and a value generate a nested dict
    with one level of nesting for every entry in the list
    if any of the list entries is itself a list create a dict for every
    element of the list. Make s
    """
    if len(keys) == 0:
        return {}
    keys.reverse()
    current_root = value
    for key in keys:
        level = {}
        if isinstance(key, list) or isinstance(key, tuple):
            for subkey in key:
                level[subkey] = deepcopy(current_root)
        else:
            level[key] = current_root
        current_root = level
    return current_root


# To load this config the following function is provided
def load_yaml(filepath: str) -> dict:
    """
    Load chip configuration from yaml file

    :param filepath: Path to the configuration file to be loaded
    :return: Dictionary containing configuration
    """
    path = Path(filepath)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as config_file:
            configuration = yaml.safe_load(config_file.read())
    else:
        print(f'File {path.absolute()} not found')
    return configuration
