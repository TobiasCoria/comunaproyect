{
    'name': 'Donaciones Comuna',
    'version': '19.0.1.0.0',
    'summary': 'Gestión de donaciones municipales con Mercado Pago',
    'description': 'Módulo para gestionar donaciones de la comunidad con portal web y pago online',
    'author': 'TC',
    'category': 'Government',
    'depends': ['base', 'mail', 'portal', 'website', 'padron_vecinal'],
    'data': [
        'security/ir.model.access.csv',
        'views/donacion_views.xml',
        'templates/portal_donacion.xml',
        'report/recibo_donacion.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}