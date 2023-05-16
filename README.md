## Baembal (뱀발, 畵蛇添足, Legs on a snake)

Why does a snake require legs? To let it runs. Let's begin by walking.

Baembal is a highly experimental Python AST parser using RustPython. It can be installed through pip and (hopefully) will eventually be available on PyPI.

Right now, it can (nearly) replace `ast.parse` function of Python standard library. The way same to installing `orjson` and replacing standard library `json`.

## Benchmarks

Platform: aarch64-apple-darwin
CPython version: 3.11.2 (pyenv)

Used benchmark: bench1.py with CPython source code. (`Lib/**/*.py`)

Raw data: (not statistically adjusted, but the ratio is stable)

- p0 - CPython ast.parse: 8.93s
- b1 - baembal.parse(locate=False): 8.45s
- b2 - baembal.parse: 11.04s
- b3 - baembal parsing-only w/o location: 5.55s
- b4 - baembal parsing-only w/ location: 6.77s

Derived data:
- Parsing + Locating + AST object construction + AST object location: 11.04s = b2
- Parsing: 5.55s (b3)
- AST object construction: 2.90s (b1 - b3)
- Locating: 1.22s (b4 - b3)
- Locating + AST object location: 2.59s (b2 - b1)
- AST object location: 1.37s (b2 - b1) - (b4 - b3)  (Low accuracy)

## What it means?

Although the complete step `baembal.parse` is slower than `ast.parse`, this strongly implies that the Python parser can be made to run more quickly.

Rough analysis with performance notes for each part.

- Parsing takes 50% of time.
  - It is comparably fast enough to other parts. But it still is not well-optimized. It copies every string without good reasons([Parser#21](https://github.com/RustPython/Parser/issues/21)). It is also using poor scanning algorithm without SIMD support.
- AST object construction takes 26% of time.
  - This is a lot slower than internal API. So this is unfair game in nature. Though `ast.parse` also spend such amount of time for object constructions, I don't know the ratio.
  - And I am very new to PyO3. I probably missed something.
- AST object location takes 13% of time.
  - This is a part of object construction. Not mandatory by use cases.
  - Also not optimized. It is currently calling setattr 4 times for every object.
- Locating takes 11% of time.
  - This is not optimized at all.
  - Locating must be `O(n)`, but currently `O(nlogm)`. ([Parser#46](https://github.com/RustPython/Parser/pull/46))
  - It also uselessly copies AST during locating.

By looking the predictable performance enhancement in future, using Baembal as a python package can gives small performance gain for applications using ast.parse. It will be not dramatically fast like 10x. It can be up to 30% by application.

Some applications make heavy use of AST. For instance, mypy seems to use `ast.parse` as fastparse. These applications can integrate RustPython parser more deeply to speed up. Removing AST object construction will saves more time. (See [Ruff](https://github.com/charliermarsh/ruff) project for this use case.)

Traditionally, parser took up a lesser proportion of the overall program runtime. These days, that is not true anymore. Compilers, including the parser, are run many multiple times before execution by development environment. And since it saves programmers' time than machine time, It is even more important.

CPython may be better to invest more on parsers. I am not saying CPython needs to integrate RustPython parser to its core - though it will be a great event. CPython has much more room to optimize its parser. Unlike the ratio of benchmark enhancement, it will immediately gives benefits to every python programmers.

## Is this library useful?

Mostly not yet, and even not in the Future. Most of the time, 1.x times performance gain is insufficient to cover the engineering cost. Using baembal will gives less performance gain but it also increases binary size and memory usage - because we cannot remove builtin CPython parser.

But if you are going to write a new python tools using AST, please consider not to start from Python and CPython. There will be more chances.

### Why do I make it?

Well, I didn't expect AST object construction parts could be that slow at the first time.
But working on it revealed that it was really helpful.

- A useful benchmark of RustPython parser to CPython parser.
- A good and easy tool to test compatibility of parser and AST out of the test suites.

And... please search for "draw legs on a snake". For a very long time, I wanted to create this named Python library but never had the opportunity.

## Acknowledgement

In addition to thanking of all of the RustPython developers and contributors for the great time of 5 years,
I also must recognize [@charliermarsh](https://github.com/charliermarsh) and his Ruff project. He made the final stop to full Python 3.11 compatible parser, and actually informed me RustPython parser is actually fast. To be honest, I expected it is a lot slower than CPython parser due to (a lot) smaller amount of engineering power we put in.

The PyO3 project is really awesome. Combining Rust and Python using PyO3 is as easy as combining Rust and RustPython. No reason not to rewrite hot path of any Python program with Rust and PyO3.

Also, a big thanks to [@lifthrasiir](https://github.com/lifthrasiir) for his advices on this project and numerous other works.
