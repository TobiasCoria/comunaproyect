from odoo import models, fields, api


class TcCart(models.Model):
    _name = 'tc.cart'
    _description = 'Carrito de Compras'

    session_id = fields.Char(string='Session ID', required=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Cliente')
    line_ids = fields.One2many('tc.cart.line', 'cart_id', string='Líneas')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
    ], default='draft', string='Estado')

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for cart in self:
            cart.total = sum(cart.line_ids.mapped('subtotal'))

    total = fields.Float(string='Total', compute='_compute_total', store=True)


class TcCartLine(models.Model):
    _name = 'tc.cart.line'
    _description = 'Línea de Carrito'

    cart_id = fields.Many2one('tc.cart', string='Carrito', ondelete='cascade')
    product_id = fields.Many2one('tc.product', string='Producto', required=True)
    quantity = fields.Integer(string='Cantidad', default=1)
    price = fields.Float(string='Precio', related='product_id.price', store=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price