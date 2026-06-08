# -*- coding: utf-8 -*-
{
    'name': 'Cierre de Caja - Comuna',
    'version': '19.0.1.0.0',
    'category': 'Government',
    'summary': 'Gestión de Cierre de Caja Diario para Comunas Municipales',
    'description': """
        Módulo para la gestión del cierre de caja diario de comunas.
        Permite registrar y controlar todos los movimientos bancarios,
        ingresos, egresos y generar reportes diarios de cierre.
    """,
    'author': 'Desarrollo Municipal',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'hr',
        'mail',
    ],
    'data': [
        'security/cierre_caja_security.xml',
        'security/ir.model.access.csv',
        'data/cierre_caja_sequence.xml',
        'data/tipo_movimiento_data.xml',
        'views/cierre_caja_views.xml',
        'views/movimiento_bancario_views.xml',
        'views/cuenta_bancaria_views.xml',
        'views/menu_views.xml',
        'report/cierre_caja_report.xml',
        'report/cierre_caja_report_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cierre_caja_comuna/static/src/css/cierre_caja.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
