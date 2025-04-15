# Contribución al Proyecto Inmobilia AI

Gracias por tu interés en contribuir a Inmobilia AI. Este documento proporciona las directrices para contribuir al proyecto siguiendo GitFlow.

## Proceso de GitFlow

Este proyecto utiliza el flujo de trabajo GitFlow. Por favor, sigue estos pasos:

### Ramas Principales

- `main`: Código de producción estable
- `develop`: Rama principal de desarrollo

### Ramas de Funcionalidad

1. Crea una rama para tu funcionalidad desde `develop`:
   ```
   git checkout develop
   git pull
   git checkout -b feature/nombre-funcionalidad
   ```

2. Realiza tus cambios en la rama de funcionalidad.

3. Asegúrate de añadir pruebas y documentación adecuadas.

4. Envía tu rama al repositorio remoto:
   ```
   git push -u origin feature/nombre-funcionalidad
   ```

5. Crea un Pull Request a `develop`.

### Releases

Para preparar una release:

1. Crea una rama de release desde `develop`:
   ```
   git checkout develop
   git pull
   git checkout -b release/x.y.z
   ```

2. Realiza ajustes finales, versiona y prepara para producción.

3. Cuando esté listo, fusiona con `main` y `develop`:
   ```
   git checkout main
   git merge --no-ff release/x.y.z
   git tag -a vx.y.z -m "Version x.y.z"
   git push origin main --tags
   
   git checkout develop
   git merge --no-ff release/x.y.z
   git push origin develop
   ```

### Hotfixes

Para correcciones urgentes en producción:

1. Crea una rama hotfix desde `main`:
   ```
   git checkout main
   git pull
   git checkout -b hotfix/descripcion-breve
   ```

2. Realiza la corrección.

3. Fusiona con `main` y `develop`:
   ```
   git checkout main
   git merge --no-ff hotfix/descripcion-breve
   git tag -a vx.y.z -m "Hotfix x.y.z"
   git push origin main --tags
   
   git checkout develop
   git merge --no-ff hotfix/descripcion-breve
   git push origin develop
   ```

## Estándares de Código

- Sigue las convenciones de PEP 8 para Python
- Escribe pruebas unitarias para tu código
- Incluye docstrings para todas las funciones, clases y módulos
- Mantén una cobertura de pruebas adecuada

## Proceso de Revisión

- Los Pull Requests requieren al menos una revisión
- Las pruebas automatizadas deben pasar
- La documentación debe estar actualizada

## Versionado

Seguimos el versionado semántico (SemVer):

- **MAJOR**: Cambios incompatibles con versiones anteriores
- **MINOR**: Nuevas funcionalidades compatibles con versiones anteriores
- **PATCH**: Correcciones de errores compatibles con versiones anteriores