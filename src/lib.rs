use pyo3::prelude::*;

use rustpython_ast::{source_code::SourceLocator, Fold};
use rustpython_ast_pyo3::{wrapper::ToPyWrapper, ToPyAst};

#[pyfunction]
#[pyo3(signature = (source, filename="<unknown>", *, type_comments=false, locate=true))]
pub fn parse_wrap(
    source: &str,
    filename: &str,
    type_comments: bool,
    locate: bool,
    py: Python,
) -> PyResult<PyObject> {
    let parsed = rustpython_parser::parse(source, rustpython_parser::Mode::Module, filename)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PySyntaxError, _>(e.to_string()))?;
    if locate {
        let parsed = SourceLocator::new(source).fold(parsed).unwrap();
        let parsed = Box::leak(Box::new(parsed));
        parsed.to_py_wrapper(py)
    } else {
        let parsed = Box::leak(Box::new(parsed));
        parsed.to_py_wrapper(py)
    }
}

#[pyfunction]
#[pyo3(signature = (source, filename="<unknown>", *, type_comments=false, locate=true))]
pub fn parse<'py>(
    source: &str,
    filename: &str,
    type_comments: bool,
    locate: bool,
    py: Python<'py>,
) -> PyResult<&'py PyAny> {
    use rustpython_parser::{ast::fold::Fold, source_code::SourceLocator};
    let _ = type_comments;
    let parsed = rustpython_parser::parse(source, rustpython_parser::Mode::Module, filename)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PySyntaxError, _>(e.to_string()))?;
    if locate {
        let parsed = SourceLocator::new(source).fold(parsed).unwrap();
        parsed.module().unwrap().to_py_ast(py)
    } else {
        parsed.module().unwrap().to_py_ast(py)
    }
}

#[pymodule]
fn baembal(py: Python, m: &PyModule) -> PyResult<()> {
    rustpython_ast_pyo3::init(py)?;

    let ast = PyModule::new(py, "ast")?;
    rustpython_ast_pyo3::wrapper::located::add_to_module(py, ast)?;
    m.add_submodule(ast)?;

    let ast = PyModule::new(py, "unlocated_ast")?;
    rustpython_ast_pyo3::wrapper::ranged::add_to_module(py, ast)?;
    m.add_submodule(ast)?;

    m.add_function(wrap_pyfunction!(parse, m)?)?;
    m.add_function(wrap_pyfunction!(parse_wrap, m)?)?;

    Ok(())
}
