from dataclasses import dataclass, field
from typing import List, Dict, Any
from .finca import FincaMVP

@dataclass
class ViviendaMVP:
    total_m2: float
    plantas: int
    estancias: List[Dict[str, Any]] = field(default_factory=list)
    extras: Dict[str, Any] = field(default_factory=dict)

    def superficie_total_estancias(self) -> float:
        """Suma los m2 de todas las estancias."""
        return sum(estancia.get('m2', 0) for estancia in self.estancias)

    def validar_contra_finca(self, finca: FincaMVP) -> bool:
        """Devuelve True si la vivienda es válida contra la finca."""
        return (
            self.total_m2 <= finca.superficie_edificable and
            self.superficie_total_estancias() <= finca.superficie_edificable and
            self.plantas <= 2
        )

    def a_dict(self) -> dict:
        """Devuelve un dict JSON-serializable."""
        return {
            'total_m2': self.total_m2,
            'plantas': self.plantas,
            'estancias': self.estancias,
            'extras': self.extras
        }

    @classmethod
    def desde_dict(cls, data: dict) -> "ViviendaMVP":
        """Construye el objeto desde un JSON generado por la IA."""
        return cls(
            total_m2=data.get('total_m2', 0.0),
            plantas=data.get('plantas', 0),
            estancias=data.get('estancias', []),
            extras=data.get('extras', {})
        )