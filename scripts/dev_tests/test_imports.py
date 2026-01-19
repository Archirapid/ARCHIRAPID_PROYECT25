try:
    from flask import Flask, request, jsonify
    import logging
    import sys
    from pathlib import Path

    # Agregar el directorio raíz al path para imports absolutos
    _backend_dir = Path(__file__).parent
    _project_root = _backend_dir.parent
    if str(_project_root) not in sys.path:
        sys.path.insert(0, str(_project_root))

    # Import del servicio de generación de planos
    try:
        from backend.services.planGenerator import generar_plano
    except ImportError:
        # Fallback si se ejecuta desde el directorio backend
        sys.path.insert(0, str(_backend_dir.parent))
        from backend.services.planGenerator import generar_plano

    # Imports para planos ASCII
    import math
    sys.path.insert(0, str(_project_root))
    from modules.marketplace import ai_engine_groq as ai
    from modules.marketplace.ascii_generator import ascii_square

    print('All imports successful')
except Exception as e:
    print(f'Import error: {e}')
    import traceback
    traceback.print_exc()