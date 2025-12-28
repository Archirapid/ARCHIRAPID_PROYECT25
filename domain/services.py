bloblofrom typing import List, Optional
from .models import (
    Property, Owner, Architect, Project, Client,
    HouseConfiguration, DigitalTwin, Order, Subscription
)


def register_property(owner: Owner, property_data: dict) -> Property:
    """
    Registra una nueva propiedad en el sistema.

    Args:
        owner: El propietario de la propiedad
        property_data: Diccionario con los datos de la propiedad

    Returns:
        La propiedad registrada
    """
    pass


def list_properties(filters: dict) -> List[Property]:
    """
    Lista las propiedades disponibles aplicando filtros.

    Args:
        filters: Diccionario con los filtros a aplicar

    Returns:
        Lista de propiedades que cumplen los filtros
    """
    pass


def reserve_property(client: Client, property: Property, amount: float) -> Order:
    """
    Reserva una propiedad para un cliente.

    Args:
        client: El cliente que reserva
        property: La propiedad a reservar
        amount: Monto de la reserva

    Returns:
        La orden de reserva creada
    """
    pass


def register_architect(architect_data: dict) -> Architect:
    """
    Registra un nuevo arquitecto en el sistema.

    Args:
        architect_data: Diccionario con los datos del arquitecto

    Returns:
        El arquitecto registrado
    """
    pass


def upload_project(architect: Architect, project_data: dict, files: List[str]) -> Project:
    """
    Sube un nuevo proyecto de arquitectura.

    Args:
        architect: El arquitecto que sube el proyecto
        project_data: Diccionario con los datos del proyecto
        files: Lista de archivos asociados al proyecto

    Returns:
        El proyecto subido
    """
    pass


def match_projects_with_property(property: Property, filters: dict) -> List[Project]:
    """
    Encuentra proyectos que coincidan con una propiedad.

    Args:
        property: La propiedad para la que buscar proyectos
        filters: Filtros adicionales para la búsqueda

    Returns:
        Lista de proyectos compatibles
    """
    pass


def start_configuration(client: Client, property: Property, base_project: Optional[Project]) -> HouseConfiguration:
    """
    Inicia una nueva configuración de casa.

    Args:
        client: El cliente que inicia la configuración
        property: La propiedad donde se construirá
        base_project: Proyecto base opcional

    Returns:
        La configuración de casa creada
    """
    pass


def update_configuration(config: HouseConfiguration, new_requirements: dict) -> HouseConfiguration:
    """
    Actualiza los requisitos de una configuración de casa.

    Args:
        config: La configuración a actualizar
        new_requirements: Nuevos requisitos

    Returns:
        La configuración actualizada
    """
    pass


def validate_configuration_against_property(config: HouseConfiguration, property: Property) -> bool:
    """
    Valida si una configuración es compatible con una propiedad.

    Args:
        config: La configuración a validar
        property: La propiedad contra la que validar

    Returns:
        True si es válida, False en caso contrario
    """
    pass


def generate_digital_twin(property: Property, config: HouseConfiguration) -> DigitalTwin:
    """
    Genera un gemelo digital para una propiedad y configuración.

    Args:
        property: La propiedad
        config: La configuración de casa

    Returns:
        El gemelo digital generado
    """
    pass


def export_project(config: HouseConfiguration, format_pdf_or_cad: str) -> str:
    """
    Exporta un proyecto en formato PDF o CAD.

    Args:
        config: La configuración a exportar
        format_pdf_or_cad: Formato de exportación ('pdf' o 'cad')

    Returns:
        Ruta o URL del archivo exportado
    """
    pass


def create_order_for_export(client: Client, config: HouseConfiguration, price: float) -> Order:
    """
    Crea una orden para la exportación de un proyecto.

    Args:
        client: El cliente que solicita la exportación
        config: La configuración a exportar
        price: Precio de la exportación

    Returns:
        La orden creada
    """
    pass


def simulate_payment(order: Order, payment_method: str) -> Order:
    """
    Simula un pago para el MVP (sin pasarela real).

    Esta función marca la orden como pagada de forma simulada,
    útil para testing y demostración del MVP.

    Args:
        order: La orden a pagar
        payment_method: Método de pago simulado (ej: 'credit_card', 'paypal')

    Returns:
        La orden con status actualizado a 'simulated'
    """
    order.status = "simulated"
    return order