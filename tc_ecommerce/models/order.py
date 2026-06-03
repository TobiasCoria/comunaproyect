from odoo import models, fields, api


class TcOrder(models.Model):
    _name = 'tc.order'
    _description = 'Pedido'

    name = fields.Char(string='Número de pedido', readonly=True, default='Nuevo')
    partner_name = fields.Char(string='Nombre', required=True)
    partner_email = fields.Char(string='Email', required=True)
    partner_phone = fields.Char(string='Teléfono')
    partner_address = fields.Text(string='Dirección', required=True)
    line_ids = fields.One2many('tc.order.line', 'order_id', string='Líneas')
    state = fields.Selection([
        ('draft', 'Nuevo'),
        ('confirmed', 'Confirmado'),
        ('done', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ], default='draft', string='Estado')
    total = fields.Float(string='Total', compute='_compute_total', store=True)
    date = fields.Datetime(string='Fecha', default=fields.Datetime.now)
    notes = fields.Text(string='Notas')

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for order in self:
            order.total = sum(order.line_ids.mapped('subtotal'))

    def action_confirm(self):
        for order in self:
            order.state = 'confirmed'
            order.name = self.env['ir.sequence'].next_by_code('tc.order') or 'Nuevo'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancelled'


class TcOrderLine(models.Model):
    _name = 'tc.order.line'
    _description = 'Línea de Pedido'

    order_id = fields.Many2one('tc.order', string='Pedido', ondelete='cascade')
    product_id = fields.Many2one('tc.product', string='Producto', required=True)
    quantity = fields.Integer(string='Cantidad', default=1)
    price = fields.Float(string='Precio')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price