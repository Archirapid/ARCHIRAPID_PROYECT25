"""
Test script para verificar cálculo de tiempo de respuesta en propuestas.
"""
from datetime import datetime, timedelta

def calculate_response_time(created_at_str, responded_at_str):
    """Calcula tiempo de respuesta entre dos timestamps ISO."""
    try:
        created = datetime.fromisoformat(created_at_str)
        responded = datetime.fromisoformat(responded_at_str)
        delta = responded - created
        hours = delta.total_seconds() / 3600
        
        if hours < 24:
            return f"{hours:.1f} horas"
        else:
            days = delta.days
            return f"{days} día{'s' if days > 1 else ''}"
    except Exception as e:
        return f"Error: {e}"

# Tests
print("=== Test 1: Respuesta en 2 horas ===")
created = datetime.now()
responded = created + timedelta(hours=2)
result = calculate_response_time(created.isoformat(), responded.isoformat())
print(f"Resultado: {result}")
assert "2.0 horas" in result, f"Expected '2.0 horas', got '{result}'"
print("✅ PASS\n")

print("=== Test 2: Respuesta en 1 día ===")
created = datetime.now()
responded = created + timedelta(days=1)
result = calculate_response_time(created.isoformat(), responded.isoformat())
print(f"Resultado: {result}")
assert "1 día" in result, f"Expected '1 día', got '{result}'"
print("✅ PASS\n")

print("=== Test 3: Respuesta en 5 días ===")
created = datetime.now()
responded = created + timedelta(days=5)
result = calculate_response_time(created.isoformat(), responded.isoformat())
print(f"Resultado: {result}")
assert "5 días" in result, f"Expected '5 días', got '{result}'"
print("✅ PASS\n")

print("=== Test 4: Respuesta en 30 minutos (0.5 horas) ===")
created = datetime.now()
responded = created + timedelta(minutes=30)
result = calculate_response_time(created.isoformat(), responded.isoformat())
print(f"Resultado: {result}")
assert "0.5 horas" in result, f"Expected '0.5 horas', got '{result}'"
print("✅ PASS\n")

print("=== Test 5: Timestamp inválido ===")
result = calculate_response_time("invalid", "2024-01-01T12:00:00")
print(f"Resultado: {result}")
assert "Error" in result, f"Expected error message, got '{result}'"
print("✅ PASS\n")

print("=" * 50)
print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
print("=" * 50)
