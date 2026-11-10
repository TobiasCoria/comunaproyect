# Módulos Odoo para gestión de comunas

Repositorio de módulos Python/XML para procesos de administración local sobre Odoo. Experiencia en desarrollo de módulos y análisis funcional.

## Módulos presentes

`padron_vecinal`, `pagos_comuna`, `cierre_caja_comuna`, `donaciones_comuna`, `obras_comuna`, `reclamos_comuna`, `turnos_comuna`, `tc_ecommerce`.

Los manifiestos revisados de Pagos Comuna y Turnos Comuna declaran versión `19.0.1.0.0`, dependencias `base`, `mail` y `padron_vecinal`, y licencia LGPL-3. La compatibilidad efectiva debe verificarse en una instalación de prueba; no se afirma compatibilidad con otras versiones.

## Organización

Los manifiestos referencian permisos, vistas y reportes. Pagos Comuna describe pagos, tasas y multas. Turnos Comuna describe áreas de atención, estados y comprobantes PDF. Estas descripciones corresponden a manifiestos; no equivalen a pruebas funcionales realizadas.

## Instalación de evaluación

Crear una instancia Odoo de desarrollo con base ficticia y respaldo. Incluir esta carpeta en `addons_path`, actualizar el listado de aplicaciones e instalar primero las dependencias indicadas por cada módulo. Validar permisos, flujos y reportes antes de cualquier uso real. No se ejecutó una instancia Odoo durante esta revisión.

## Publicación

Revisar derechos sobre código de clientes, datos XML/CSV y recursos antes de promocionar el repositorio. Su visibilidad pública actual no reemplaza esa verificación.

## English

Odoo modules for local administration, including residents, payments, works, donations, requests and appointments. Reviewed payment and appointment manifests target version 19.0.1.0.0 and depend on base, mail and the residents module. Runtime compatibility and client publication rights require validation.
