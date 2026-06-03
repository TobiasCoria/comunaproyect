{
    'name': 'Padron Vecinal',
    'version': '19.0.1.0.0',
    'summary': 'Padrón de vecinos para comuna municipal',
    'description': 'Gestión del padrón de habitantes de la comuna',
    'author': 'TCSL',
    'category': 'Government',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/padron_views.xml',
        'report/constancia_residencia.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}