Título: Evaluar e implementar módulos nativos (Rust/C++) pendientes

Descripción:
`docs/workflow-log.md` menciona "módulos Rust/C++ nativos pendientes".

Problema:
Falta evaluación y plan para módulos nativos. Necesitamos decidir si implementarlos o documentar alternativas en Python.

Pasos sugeridos:
- Listar requisitos de rendimiento que justificarían natived code.
- Hacer POC (Rust/pyo3 o cffi) y medir mejoras.
- Definir APIs y añadir pruebas y packaging CI para builds nativos (Windows builds en CI si procede).

Asignado sugerido: @doski2
Labels sugeridos: `poc`, `native`, `performance`