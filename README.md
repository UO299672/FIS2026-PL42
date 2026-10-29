# Proyecto PL 4 Grupo 2



## Estructura

```
proyecto
├── pyproject.toml     Configuración del paquete y del comando `proyecto`
├── resources/
│   ├── schema.sql     Esquema de la base de datos (se borra y recrea en cada arranque)
│   └── data.sql       Carga inicial de datos
└── src/               Código fuente
    ├── main.py        Punto de entrada y menú principal
    ├── view/          Capa de vista
    └── util/          Acceso a datos, validaciones y excepciones
```

## Requisitos

- Python 3.10+ (probado con 3.11)
- SQLite (incluido en la librería estándar)

## Instalación (entorno virtual)

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -e .
```

En PowerShell, activa el entorno antes de usar el comando instalado:

```powershell
. .\.venv\Scripts\Activate.ps1
proyecto
```

Si no quieres activar el entorno, ejecuta el lanzador con su ruta completa:

```powershell
.\.venv\Scripts\proyecto.exe
```

## Ejecución

> **Importante:** ejecuta siempre el programa desde la **raíz del proyecto**
> (la carpeta que contiene `resources/` y `src/`). Las rutas a los scripts SQL
> y a la base de datos son relativas a esa carpeta.

```powershell
# Con el entorno virtual activado
proyecto

# Sin instalar, desde la raíz del proyecto
python -m src.main
```

En VS Code, abre **Ejecutar y depurar** y selecciona **Ejecutar proyecto**.
La configuración usa `src.main` como módulo para que los imports del paquete
`src` se resuelvan correctamente.

> Nota: en cada arranque se **borra y recrea** el esquema y se recargan los datos
> iniciales (fíjate en `src/main.py`). La base de datos `CompanyDB.db` se crea en
> la raíz del proyecto, se queda solo en tu equipo y no se sube al repositorio.
> El menú se cierra siempre con la opción **0**.

Las reglas de validación de entradas están separadas en `src/util/validation.py`.
