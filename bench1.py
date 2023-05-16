import fake_ast
import ast

ast.AST = fake_ast.AST
dump = ast.dump

import timeit
from glob import glob


files = {}
for path in glob("../cpython/Lib/**/*.py"):
    try:
        txt = open(path, 'r').read()
    except UnicodeDecodeError:
        continue
    # try:
    #     if py_ast.dump(py_ast.parse(txt)) != py_ast.dump(rust_ast.parse(txt)):
    #         continue
    # except SyntaxError:
    #     continue
    files[path] = txt

t = [0.0] * 5

import ast as py_ast
import baembal as rust_ast

def f(i):
    return f'{t[i]/t[0]:.2f}({t[i]:.2f}s)'

for path, txt in files.items():
    # p = py_ast.parse(txt)
    # r = rust_ast.parse(txt)

    # compile(p, 'x', 'exec')
    # compile(r, 'x', 'exec')

    # print('starting', path)

    # break
    try:
        p = timeit.timeit(lambda: (py_ast.parse(txt, type_comments=True)), number=5)
        r1 = timeit.timeit(lambda: (rust_ast.parse(txt, locate=False)), number=5)
        r2 = timeit.timeit(lambda: (rust_ast.parse(txt, locate=True)), number=5)
        r3 = timeit.timeit(lambda: (rust_ast.parse_wrap(txt, locate=False)), number=5)
        r4 = timeit.timeit(lambda: (rust_ast.parse_wrap(txt, locate=True)), number=5)
    except Exception as e:
        print('error:', path, e)
        continue

    for i, d in enumerate([p, r1, r2, r3, r4]):
        t[i] += d
    print('acc:', f(0), f(1), f(2), f(3), f(4), path)

