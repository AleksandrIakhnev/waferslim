import os
import sys
import re

def to_pythonic(method_name):
    '''Converts CamelCase to pythonic_case'''
    return (method_name[0].lower() +
            ''.join(map(underscored_lowercase, method_name[1:])))


def to_lower_camel_case(method_name):
    '''Converts pythonic_case to camelCase'''
    camel_case = re.sub(
        '_(.)',
        lambda m: m.group(1).upper(),
        method_name
    )
    return camel_case[:1].lower() + camel_case[1:]


def to_upper_camel_case(method_name):
    '''Converts pythonic_case to CamelCase'''
    camel_case = re.sub(
        '_(.)',
        lambda m: m.group(1).upper(),
        method_name
    )
    return camel_case[:1].upper() + camel_case[1:]


def underscored_lowercase(char):
    if char.isupper():
        return '_' + char.lower()
    else:
        return char


def get_aliases(methods):
    aliases = dict((n, n) for n in methods)
    aliases.update(convention_aliases(aliases))
    return aliases


def convention_aliases(aliases):
    camel_caseds = dict([
                            (to_lower_camel_case(name), aliases[name])
                            for name in aliases
                            ])
    camel_caseds.update([
                            (to_upper_camel_case(name), aliases[name])
                            for name in aliases
                            ])
    return camel_caseds

def load_classes(package_path):
    on_path = find_in_sys_path(package_path)
    if on_path is not None:
        if os.path.isfile(on_path):
            for name, data in get_classes(load_source(on_path)):
                yield (name, data)
        else:
            for module in load_package(on_path):
                for name, data in get_classes(module):
                    yield (name, data)
    else:
        for name, data in get_classes(__import__(package_path)):
            yield (name, data)

def find_in_sys_path(path):
    for base in sys.path:
        rel_path = os.path.join(base, path)
        if os.path.exists(rel_path):
            return rel_path
    return None

def load_source(source_path):
    import imp
    name = os.path.splitext(os.path.basename(source_path))[0]
    return imp.load_source(name, source_path)

def load_package(package_path):
    import pkgutil
    for loader, name, is_pkg in pkgutil.iter_modules([package_path]):
        if is_pkg:
            subpackage_path = os.path.join(package_path, name)
            for module in load_package(subpackage_path):
                yield module
        else:
            yield loader.find_module(name).load_module(name)

def get_classes(module):
    import inspect
    for class_name, Class in inspect.getmembers(module, inspect.isclass):
        methods = [n
                   for n, _ in inspect.getmembers(Class, inspect.isroutine)
                   if '__' not in n]
        yield (class_name, {'class': Class, 'methods': methods})