# Python Project

This is a Python project created with a basic structure.

## Project Structure

```
.
├── src/           # Source code files
├── tests/         # Test files
├── requirements.txt   # Project dependencies
└── README.md      # Project documentation
```

## Getting Started

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```
     .\venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```
     source venv/bin/activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Development

Place your source code in the `src` directory and tests in the `tests` directory.

## ⚠️ Estructura Crítica del Proyecto

### Ubicación Crítica: `compute_edificability.py`
Este archivo **DEBE** permanecer siempre en la **raíz** del proyecto. Todos los módulos de ArchiRapid dependen de esta ubicación para acceder a los datos de edificabilidad validados.

**❌ NO mover a subcarpetas** - Si se mueve, los módulos no podrán encontrar los m² exactos.

### Verificación de Integridad
Para verificar que el proyecto está correctamente configurado:
```bash
python verify_integrity.py
```

Este script confirmará que `compute_edificability.py` está en la ubicación correcta y que todos los archivos relacionados están presentes.