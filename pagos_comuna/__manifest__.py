{
    'name': 'Pagos Comuna',
    'version': '19.0.1.0.0',
    'summary': 'Gestión de pagos, tasas y multas municipales',
    'description': 'Módulo para gestionar tasas, servicios, multas y cuotas de la comuna',
    'author': 'TC',
    'category': 'Government',
    'depends': ['base', 'mail', 'padron_vecinal'],
    'data': [
        'security/ir.model.access.csv',
        'views/concepto_views.xml',
        'views/pago_views.xml',
        'report/recibo_pago.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}