from odoo import models, fields

class TcProduct(models.Model):
    _name = 'tc.product'
    _description = 'Producto eCommerce'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
    price = fields.Float(string='Precio', required=True)
    stock = fields.Integer(string='Stock disponible', default=0)
    image = fields.Binary(string='Imagen')
    active = fields.Boolean(string='Activo', default=True)
    category_id = fields.Many2one('tc.product.category', string='Categoría')


class TcProductCategory(models.Model):
    _name = 'tc.product.category'
    _description = 'Categoría de Producto'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')