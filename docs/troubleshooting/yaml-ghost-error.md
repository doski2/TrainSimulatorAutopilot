# Error "Expected a scalar value, a sequence, or a mapping" (mensaje fantasma)

⚠️ **Resumen breve**

Algunos parsers o linters YAML muestran un error críptico como "Expected a scalar value, a sequence, or a mapping" que no siempre señala correctamente el origen real del fallo. En nuestro caso, el fallo fue causado por **caracteres de control invisibles** (ej. U+008D) y bytes no UTF-8 (incluyendo NULs o codificaciones incorrectas) en un archivo de documentación (`mkdocs_clean.yml`). También se observó un caso separado donde la clave `"on"` estaba entre comillas y provocó un problema.

---

## ✅ Causa

- Presencia de caracteres de control (p.ej. U+008D) o NUL (0x00) en el contenido del archivo YAML.
- Archivos con codificación distinta a UTF‑8 (p. ej. bytes > 127 sin interpretación correcta).
- En una ocasión, la clave `on` estaba entre comillas (`"on":`) y eso hizo que el validador lo interpretara mal.

---

## 🔎 Detección

Usar el script de diagnóstico incluido en el repo:

```bash
python scripts/check_yaml.py
```

Esto reporta:
- `NUL_CHAR` si encuentra NULs
- `DECODE_ERR` si el archivo no se puede leer como UTF‑8
- `PARSE_ERR` si PyYAML no puede parsearlo

También hay un script para mostrar y limpiar caracteres de control:

```bash
python scripts/show_control_chars.py
python scripts/clean_control_chars.py  # hace backup mkdocs_clean.yml.bak y limpia
```

Para análisis rápido desde PowerShell (ejemplo):

```powershell
# Buscar NULs en todos los YAML
Get-ChildItem -Recurse -Include *.yml,*.yaml -File | ForEach-Object {
  $bytes = [System.IO.File]::ReadAllBytes($_.FullName)
  if ($bytes -contains 0) { Write-Output "NUL en: $($_.FullName)" }
}
```

---

## 🩺 Corrección

1. Hacer backup del archivo afectado:

```powershell
Copy-Item mkdocs_clean.yml mkdocs_clean.yml.bak
```

2. Eliminar control chars o convertir a UTF‑8 (sin BOM):

```powershell
(Get-Content mkdocs_clean.yml -Raw) -replace "`0","" | Set-Content mkdocs_clean.yml -Encoding utf8
```

O usar el script incluido que realiza backup y limpieza:

```bash
python scripts/clean_control_chars.py
```

3. Validar parseo con PyYAML:

```bash
python -c "import yaml; yaml.safe_load(open('mkdocs_clean.yml','r',encoding='utf-8'))"
```

4. Commit + push de la corrección y re-ejecutar workflows/linters.

---

## 🛡 Prevención

- Añadir en la CI una comprobación que ejecute `python scripts/check_yaml.py` antes de publicar o desplegar.
- Habilitar `check-yaml` en `.pre-commit-config.yaml` (ya está presente en el repo). Asegurarse de que el hook se ejecuta localmente:

```bash
pre-commit run --all-files
```

- Evitar colocar claves especiales entre comillas innecesarias (p. ej. `on:` no `"on":`).

---

## 🧾 Registro de la incidencia

- Archivo afectado: `mkdocs_clean.yml`
- Síntoma: mensaje críptico "Expected a scalar value, a sequence, or a mapping"
- Acción: eliminado carácter de control (U+008D), añadido script de diagnóstico y documentación.

---

Si quieres, puedo agregar una tarea en la CI para ejecutar `scripts/check_yaml.py` y bloquear PRs que introduzcan archivos YAML inválidos. ¿Quieres que lo automatice? 
