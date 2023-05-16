import re
import baembal

import ast

ast.AST = baembal.AST

import pytest

import ast as py_ast
import baembal as rust_ast


from glob import glob

files = {}
for path in glob("../../cpython/Lib/**/*.py"):
    try:
        txt = open(path, "r").read()
    except UnicodeDecodeError:
        continue

    if not path.endswith('cp869.py'):
        continue
    # try:
    #     if py_ast.dump(py_ast.parse(txt)) != py_ast.dump(rust_ast.parse(txt)):
    #         continue
    # except SyntaxError:
    #     continue
    files[path] = txt


@pytest.mark.parametrize("path", files.keys())
def test_roundtrip(path):
    txt = files[path]
    module_p = py_ast.parse(txt)
    dump_p = py_ast.dump(module_p, indent=True)
    module_r = rust_ast.parse(txt)
    dump_r = py_ast.dump(module_r, indent=True)
    p = re.compile("object at 0x[0-9a-f]+")
    dump_p2 = re.sub(p, "object at 0x????????", dump_p)
    dump_r2 = re.sub(p, "object at 0x????????", dump_r)
    try:
        assert dump_p2 == dump_r2, dump_r2
    except AssertionError:
        with open("dump_code.py", "w") as f:
            f.write(path)
            f.write('\n')
            f.write(txt)
        with open("dump_p.txt", "w") as f:
            f.write(dump_p2)
        with open("dump_r.txt", "w") as f:
            f.write(dump_r2)
        raise


    with open("dump_code.py", "w") as f:
        f.write(path)
        f.write('\n')
        f.write(txt)
    with open("dump_p.txt", "w") as f:
        f.write(dump_p2)
    with open("dump_r.txt", "w") as f:
        f.write(dump_r2)