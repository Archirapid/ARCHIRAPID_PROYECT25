# Archirapid - Modelo de Dominio (MVP)

Este documento define el modelo de dominio que debe respetar TODO el código de la app Archirapid.
GitHub Copilot debe usar estas entidades y casos de uso y NO inventar nombres nuevos.

## Entidades principales

### Property (Finca/Terreno)
- id
- owner_id
- location (pais, ciudad, coordenadas)
- cadastral_reference
- surface_m2
- buildable_ratio (por defecto 0.33)
- price
- zoning_type (urbana, industrial)
- media (fotos, videos)
- status (listed, reserved, sold)

### Owner
- id
- name
- email
- phone

### Architect
- id
- name
- studio_name
- email
- phone
- specialization

### Project
- id
- architect_id
- title
- description
- required_plot_m2
- built_area_m2
- floors
- bedrooms
- bathrooms
- has_pool
- has_garage
- files_pdf
- files_cad
- files_3d
- base_price
- status (draft, published, sold)

### Client
- id
- name
- email
- phone

### HouseConfiguration
- id
- client_id
- property_id
- base_project_id (opcional)
- total_built_area_m2
- floors
- bedrooms
- bathrooms
- garage
- pool
- estimated_cost
- status (draft, confirmed)

### DigitalTwin
- id
- property_id
- configuration_id
- geometry_data
- valid (bool)
- validation_messages

### Order
- id
- client_id
- type (property_reservation, property_purchase, project_purchase, configuration_purchase, simulated_payment)
- amount
- currency
- status (pending, paid, failed, simulated)

### Subscription
- id
- architect_id
- plan_type (3_projects, 6_projects, 10_projects)
- price
- status
- valid_until

## Casos de uso (use cases)

- register_property(owner, property_data)
- list_properties(filters)
- reserve_property(client, property, amount)
- register_architect(architect_data)
- upload_project(architect, project_data, files)
- match_projects_with_property(property, filters)
- start_configuration(client, property, base_project)
- update_configuration(config, new_requirements)
- validate_configuration_against_property(config, property)
- generate_digital_twin(property, config)
- export_project(config, format_pdf_or_cad)
- create_order_for_export(client, config, price)
- simulate_payment(order, payment_method)  # pago simulado para MVP, sin pasarela real
