"""
Modelo y función utilitaria para crear objetos FINCA para el MVP de ARCHIRAPID.
No usa base de datos, ni Streamlit, ni IA.
"""

import math

def crear_finca_mvp(titulo, direccion, provincia, precio, superficie_parcela, porcentaje_edificabilidad, lat, lon):
    """
    Crea un diccionario FINCA sencillo para el MVP.
    Calcula la superficie edificable automáticamente.
    Añade un solar_virtual rectangular simple.
    """
    superficie_edificable = superficie_parcela * porcentaje_edificabilidad
    # Solar virtual: rectángulo con lados iguales (aprox.) y orientación fija 'N'
    lado = math.sqrt(superficie_parcela)
    solar_virtual = {
        "ancho": lado,
        "largo": lado,
        "orientacion": "N"
    }
    finca = {
        "titulo": titulo,
        "direccion": direccion,
        "provincia": provincia,
        "precio": precio,
        "superficie_parcela": superficie_parcela,
        "porcentaje_edificabilidad": porcentaje_edificabilidad,
        "superficie_edificable": superficie_edificable,
        "lat": lat,
        "lon": lon,
        "solar_virtual": solar_virtual,
        "estado": {
            "publicada": True
        }
    }
    return finca

# =====================
# MODELO DATACLASS MVP
# =====================
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, ClassVar
import math

@dataclass
class FincaMVP:
    id: str
    titulo: str
    direccion: str
    provincia: str
    precio: float
    superficie_parcela: float
    porcentaje_edificabilidad: float
    superficie_edificable: float
    lat: Optional[float]
    lon: Optional[float]
    solar_virtual: Dict[str, Any]
    servicios: Dict[str, bool] = field(default_factory=dict)
    estado: Dict[str, Any] = field(default_factory=dict)
    referencia_catastral: str = field(default="")  # Nuevo campo: referencia catastral
    plano_catastral_path: str = field(default="")  # Nuevo campo: ruta del PDF catastral

    def calcular_superficie_edificable(self) -> None:
        """Calcula y actualiza la superficie edificable."""
        self.superficie_edificable = self.superficie_parcela * self.porcentaje_edificabilidad

    @classmethod
    def desde_dict(cls, data: dict) -> "FincaMVP":
        """Crea una instancia de FincaMVP a partir de un diccionario."""
        return cls(
            id=data.get("id", ""),
            titulo=data.get("titulo", ""),
            direccion=data.get("direccion", ""),
            provincia=data.get("provincia", ""),
            precio=float(data.get("precio", 0)),
            superficie_parcela=float(data.get("superficie_parcela", 0)),
            porcentaje_edificabilidad=float(data.get("porcentaje_edificabilidad", 0)),
            superficie_edificable=float(data.get("superficie_edificable", 0)),
            lat=data.get("lat"),
            lon=data.get("lon"),
            solar_virtual=data.get("solar_virtual", {}),
            servicios=data.get("servicios", {}),
            estado=data.get("estado", {}),
            referencia_catastral=data.get("referencia_catastral", ""),  # Nuevo campo
            plano_catastral_path=data.get("plano_catastral_path", "")  # Nuevo campo
        )

    def a_dict(self) -> dict:
        """Devuelve el objeto como un diccionario JSON-serializable."""
        return asdict(self)
