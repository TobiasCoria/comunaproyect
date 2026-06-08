# -*- coding: utf-8 -*-
{
    'name': 'Turnos Comuna',
    'version': '19.0.1.0.0',
    'category': 'Government',
    'summary': 'Gestión de turnos de atención al público en comunas municipales',
    'description': """
        Módulo para gestionar turnos de atención al público en comunas municipales argentinas.
        Permite administrar áreas de atención, turnos, estados y generar comprobantes PDF.
    """,
    'author': 'Comuna Municipal',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'padron_vecinal'],
    'data': [
        'security/ir.model.access.csv',
        'views/turnos_comuna_area_views.xml',
        'views/turnos_comuna_turno_views.xml',
        'views/turnos_comuna_menus.xml',
        'report/turnos_comuna_report.xml',
        'report/turnos_comuna_report_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
