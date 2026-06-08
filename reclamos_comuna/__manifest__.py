# -*- coding: utf-8 -*-
{
    'name': 'Reclamos Comuna',
    'version': '19.0.1.0.0',
    'summary': 'Gestión de reclamos de vecinos en comuna municipal argentina',
    'description': """
        Módulo para gestionar reclamos de vecinos en una comuna municipal argentina.
        Permite registrar, hacer seguimiento y resolver reclamos ciudadanos.
    """,
    'author': 'Municipalidad',
    'category': 'Government',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'padron_vecinal'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/categoria_views.xml',
        'views/reclamo_views.xml',
        'views/menu_views.xml',
        'report/report_reclamo.xml',
        'report/report_reclamo_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
