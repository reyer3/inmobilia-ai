# Configuración de Git Hooks

Este proyecto utiliza Git Hooks para automatizar el formateo del código con Black e isort antes de cada commit.

## Configuración

Para habilitar los hooks, ejecuta uno de los siguientes comandos según tu sistema operativo:

### Para usuarios de Linux/MacOS

```bash
# Desde la raíz del proyecto
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

### Para usuarios de Windows (PowerShell)

```powershell
# Desde la raíz del proyecto
git config core.hooksPath .githooks
```

Después necesitarás crear un archivo `.git\hooks\pre-commit` con el siguiente contenido:

```bash
#!/bin/sh
pwsh -ExecutionPolicy Bypass -File .githooks/pre-commit.ps1
```

## Uso

Una vez configurado, cada vez que intentes hacer un commit, el hook:

1. Formateará automáticamente tus archivos Python con Black e isort
2. Ejecutará comprobaciones de linting con flake8 y mypy
3. Agregará los archivos formateados al staging area

Si las comprobaciones de linting fallan, el commit será rechazado y deberás corregir los errores antes de intentar de nuevo.

## Saltar los hooks (no recomendado)

Si necesitas hacer un commit sin ejecutar los hooks (situación excepcional):

```bash
git commit --no-verify -m "Tu mensaje de commit"
```

## Comandos de utilidad

También puedes usar los comandos del Makefile para formatear y verificar tu código manualmente:

```bash
# Formateo manual (Linux/macOS)
make format

# Formateo manual (Windows)
make format-win
```
