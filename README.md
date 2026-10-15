# python-code-style-pep8-hcht

Colección de skills de estilo de código Python basados en PEP 8 con reglas propias. Cada skill incluye su propia documentación, scripts de verificación (checker) y formateo (formatter), ejemplos y tests unitarios.

## Skills de la colección

### pep8-hcht-vertical-alignment

Aplica alineación vertical obligatoria en construcciones multilínea de Python: llamadas a funciones, definiciones, listas, diccionarios, comprehensions, cadenas de llamadas, operadores binarios y estructuras `if`/`for`/`with`. Indentación de 4 espacios por nivel. El hanging indent está prohibido.

### pep8-hcht-formatting

Aplica reglas de formato consistentes:

- Dos líneas en blanco entre funciones y clases de nivel superior; una entre métodos.
- Sin líneas en blanco al inicio del archivo; una línea en blanco final después del último bloque de código.
- Una línea en blanco entre el docstring de módulo y la primera definición, sin líneas adicionales después del cierre del docstring.
- Sin líneas en blanco internas dentro de las funciones.
- Espacios alrededor de operadores binarios y comillas simples para strings.

## Estructura de cada skill

- `SKILL.md` — documentación y reglas del skill.
- `scripts/` — `check_<topic>.py` (verificación) y `format_<topic>.py` (formateo).
- `examples/good/` y `examples/bad/` — ejemplos válidos e inválidos.
- `tests/` — tests unitarios.