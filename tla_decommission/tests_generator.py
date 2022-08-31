# -*- coding: utf-8 -*-
import ast
from os import mkdir
from os import walk
from os.path import exists
from os.path import isdir
from os.path import join
from typing import Dict
from typing.io import IO


def generate_pair(filename: str):
    pair = {'source': filename, 'test': ''}
    if not filename.endswith('.py'):
        return pair
    if filename == '__init__.py':
        pair['test'] = filename
    else:
        pair['test'] = f'test_{filename}'

    return pair


def check_if_file_exits_and_create(path: str, filename: str):
    fullpath = join(path, filename)

    if not isdir(path):
        print(f'creating dir: {path}')
        mkdir(path)

    if not exists(fullpath):
        print(f'creating file: {fullpath}')
        f = open(fullpath, 'w')
        f.close()

    return fullpath


def get_methods(source_file: str):
    class_list = {}

    if not source_file.endswith('.py'):
        return class_list

    class_name = None
    method_name = None
    file_object = open(source_file, 'r')
    text = file_object.read()
    p = ast.parse(text)
    node = ast.NodeVisitor()
    for node in ast.walk(p):
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
            else:
                method_name = node.name
            if class_name != None and method_name != None:
                if class_name not in class_list.keys():
                    class_list[class_name] = []
                class_list[class_name].append(method_name)
    return class_list


def write_test_class(filestream: IO, classname: str):
    filestream.write("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase


class """ + classname + """(TestCase):
""")


def write_test_method(filestream: IO, methodname: str):
    if methodname == 'test___init__':
        filestream.write("""
    def """ + methodname + """(self):
        self.skipTest('Constructor method')
    """)
    else:
        filestream.write("""
    def """ + methodname + """(self):
        self.assertTrue(False, 'NOT TESTED YET')
    """)


def create_test_methods(classlist: Dict, test_file: str):
    print(f' creating methods in {test_file}')
    f = open(test_file, 'a')

    classlist_test = get_methods(test_file)
    print(classlist_test)
    for classname in classlist.keys():
        for method_name in classlist[classname]:
            test_classname = f'{classname}Test'
            test_method_name = f'test_{method_name}'
            if test_classname not in classlist_test.keys():
                write_test_class(f, test_classname)
                classlist_test[test_classname] = []
            if test_method_name not in classlist_test[test_classname]:
                write_test_method(f, test_method_name)
                classlist_test[test_classname].append(test_method_name)

    f.close()


path_src = './src'
path_tst = './tests'

files = {}
for (dirpath, dirnames, filenames) in walk(path_src):
    if 'cache' in dirpath or dirpath == path_src:
        continue
    # f.extend(filenames)
    dirpath = dirpath.replace(path_src + '/', '')
    # print(f'dirpath: {dirpath}  dirnames: {dirnames}  filenames: {filenames}')
    print('-----------------------')
    print(f'dirpath: {dirpath}')
    for filename in filenames:
        print(f'   {filename}')
        if not dirpath in files.keys():
            files[dirpath] = []
        pair = generate_pair(filename)
        files[dirpath].append(pair)

        if pair['test'] != '':
            test_file = check_if_file_exits_and_create(f'{path_tst}/{dirpath}',
                                                       pair['test'])
            source_file = f'{path_src}/{dirpath}/{pair["source"]}'
            classlist = get_methods(source_file)
            print(classlist)
            create_test_methods(classlist, test_file)


# print(files)
