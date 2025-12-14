from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Property:
    id: int
    owner_id: int
    location: str  # pais, ciudad, coordenadas
    cadastral_reference: str
    surface_m2: float
    buildable_ratio: float  # por defecto 0.33
    price: float
    zoning_type: str  # urbana, industrial
    media: List[str]  # fotos, videos
    status: str  # listed, reserved, sold

@dataclass
class Owner:
    id: int
    name: str
    email: str
    phone: str

@dataclass
class Architect:
    id: int
    name: str
    studio_name: str
    email: str
    phone: str
    specialization: str

@dataclass
class Project:
    id: int
    architect_id: int
    title: str
    description: str
    required_plot_m2: float
    built_area_m2: float
    floors: int
    bedrooms: int
    bathrooms: int
    has_pool: bool
    has_garage: bool
    files_pdf: List[str]
    files_cad: List[str]
    files_3d: List[str]
    base_price: float
    status: str  # draft, published, sold

@dataclass
class Client:
    id: int
    name: str
    email: str
    phone: str

@dataclass
class HouseConfiguration:
    id: int
    client_id: int
    property_id: int
    base_project_id: Optional[int]  # opcional
    total_built_area_m2: float
    floors: int
    bedrooms: int
    bathrooms: int
    garage: bool
    pool: bool
    estimated_cost: float
    status: str  # draft, confirmed

@dataclass
class DigitalTwin:
    id: int
    property_id: int
    configuration_id: int
    geometry_data: str
    valid: bool
    validation_messages: List[str]

@dataclass
class Order:
    id: int
    client_id: int
    type: str  # property_reservation, property_purchase, project_purchase, configuration_purchase, simulated_payment
    amount: float
    currency: str
    status: str  # pending, paid, failed, simulated

@dataclass
class Subscription:
    id: int
    architect_id: int
    plan_type: str  # 3_projects, 6_projects, 10_projects
    price: float
    status: str
    valid_until: str
