use pyo3::prelude::*;
use rustpython_parser::ast::pyo3::ToPyo3Ast;

fn main() {
    let locate = false;
    let filename = "<unknown>";
    let source = include_str!("../../cpython/Lib/asyncio/unix_events.py");
    use rustpython_parser::{ast::fold::Fold, source_code::{RandomLocator as Locator}};

    pyo3::prepare_freethreaded_python();
    let _: PyResult<()> = pyo3::Python::with_gil(|py| {
        rustpython_ast::pyo3::init(py)?;

        for _ in 0..1000 {
            let parsed =
                rustpython_parser::parse(source, rustpython_parser::Mode::Module, filename)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PySyntaxError, _>(e.to_string()))?;
            if locate {
                let parsed = Locator::new(source).fold(parsed).unwrap();
                parsed.module().unwrap().to_pyo3_ast(py)?;
            } else {
                parsed.module().unwrap().to_pyo3_ast(py)?;
            }
        }
        Ok(())
    });
}
