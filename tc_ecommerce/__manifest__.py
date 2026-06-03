{
    'name': 'TC eCommerce',
    'version': '19.0.1.0.0',
    'summary': 'Simple eCommerce module',
    'description': 'Módulo de eCommerce simple para práctica',
    'author': 'Tobias Coria',
    'website': 'https://github.com/TobiasCoriaGH',
    'category': 'eCommerce',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/shop_templates.xml',
        'views/product_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'tc_ecommerce/static/src/css/shop.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}