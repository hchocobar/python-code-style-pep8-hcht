# python-code-style-pep8-hcht

Colección de skills de estilo de código Python basados en PEP 8 con reglas propias. Cada skill incluye su propia documentación, scripts de verificación (checker) y formateo (formatter), ejemplos y tests unitarios.

## Skills de la colección

### pep8-hcht-naming

Aplica reglas de nomenclatura consistentes: `snake_case` para variables y funciones, `UPPER_SNAKE_CASE` para constantes, `PascalCase` para clases. Todos los nombres deben ser descriptivos y en inglés.

### pep8-hcht-formatting

Aplica reglas de formato consistentes:

- Dos líneas en blanco entre funciones y clases de nivel superior; una entre métodos.
- Sin líneas en blanco al inicio del archivo; una línea en blanco final después del último bloque de código.
- Una línea en blanco entre el docstring de módulo y la primera definición, sin líneas adicionales después del cierre del docstring.
- Sin líneas en blanco internas dentro de las funciones.
- Espacios alrededor de operadores binarios y comillas simples para strings.

### pep8-hcht-vertical-alignment

Aplica alineación vertical obligatoria en construcciones multilínea de Python: llamadas a funciones, definiciones, listas, diccionarios, comprehensions, cadenas de llamadas, operadores binarios y estructuras `if`/`for`/`with`. Indentación de 4 espacios por nivel. El hanging indent está prohibido.

### pep8-hcht-docstrings

Exige docstrings estilo NumPy en todas las funciones y métodos. Verifica presencia, secciones `Parameters`/`Returns`, ausencia de línea en blanco después del docstring y formato correcto de comillas triples en docstrings multilínea.

### pep8-hcht-comments

Aplica reglas de comentarios consistentes: un espacio después del `#`, mayúscula inicial, exactamente dos espacios antes de comentarios inline, comentarios en inglés, sin bloques decorativos y sin comentarios inline dentro de estructuras de datos.

### pep8-hcht-imports

Aplica reglas PEP 8 para imports: un import por línea, agrupados en orden (stdlib primero, non-stdlib después), imports absolutos preferidos, sin wildcard imports y orden alfabético dentro de cada grupo.

## Estructura de cada skill

- `SKILL.md` — documentación y reglas del skill.
- `scripts/` — `check_<topic>.py` (verificación) y `format_<topic>.py` (formateo).
- `examples/good/` y `examples/bad/` — ejemplos válidos e inválidos.
- `tests/` — tests unitarios.