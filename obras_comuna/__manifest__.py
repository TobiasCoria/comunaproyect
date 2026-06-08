{
    'name': 'Obras Comuna',
    'version': '19.0.1.0.0',
    'summary': 'Gestión de obras públicas municipales',
    'description': 'Módulo para planificar obras, registrar avances y asignar cuadrillas',
    'author': 'TC',
    'category': 'Government',
    'depends': ['base', 'mail', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/cuadrilla_views.xml',
        'views/obra_views.xml',
        'report/informe_obra.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}