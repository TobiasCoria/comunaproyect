from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class Donacion(models.Model):
    _name = 'donaciones_comuna.donacion'
    _description = 'Donación'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc'

    name = fields.Char(
        string='Nº Donación',
        readonly=True,
        copy=False,
        default='Nuevo'
    )
    donante_nombre = fields.Char(
        string='Nombre del donante',
        required=True,
        tracking=True
    )
    donante_email = fields.Char(
        string='Email del donante',
        required=True
    )
    donante_telefono = fields.Char(
        string='Teléfono'
    )
    donante_dni = fields.Char(
        string='DNI'
    )
    vecino_id = fields.Many2one(
        'tc.vecino',
        string='Vecino vinculado'
    )
    tipo = fields.Selection([
        ('dinero', 'Dinero'),
        ('ropa', 'Ropa'),
        ('alimentos', 'Alimentos'),
        ('materiales', 'Materiales'),
        ('otro', 'Otro'),
    ], string='Tipo de donación', required=True, default='dinero', tracking=True)
    monto = fields.Float(
        string='Monto',
        digits=(10, 2)
    )
    descripcion = fields.Text(
        string='Descripción'
    )
    destino = fields.Char(
        string='Destino de la donación'
    )
    fecha = fields.Datetime(
        string='Fecha',
        default=fields.Datetime.now,
        tracking=True
    )
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('recibida', 'Recibida'),
        ('rechazada', 'Rechazada'),
    ], string='Estado', default='pendiente', tracking=True)
    metodo_pago = fields.Selection([
        ('mercadopago', 'Mercado Pago'),
        ('transferencia', 'Transferencia bancaria'),
        ('efectivo', 'Efectivo'),
        ('otro', 'Otro'),
    ], string='Método de pago', default='mercadopago')
    mp_payment_id = fields.Char(
        string='ID de pago MP',
        readonly=True
    )
    mp_status = fields.Char(
        string='Estado MP',
        readonly=True
    )
    notas = fields.Text(
        string='Notas internas'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('donaciones_comuna.donacion') or 'Nuevo'
        return super().create(vals_list)

    def action_marcar_recibida(self):
        for rec in self:
            rec.estado = 'recibida'

    def action_rechazar(self):
        for rec in self:
            rec.estado = 'rechazada'

    def action_generar_recibo(self):
        return self.env.ref('donaciones_comuna.action_report_recibo_donacion').report_action(self)

    def _generar_link_mercadopago(self):
        import requests as req
        ICP = self.env['ir.config_parameter'].sudo()
        access_token = ICP.get_param('donaciones_comuna.mp_access_token')
        base_url = ICP.get_param('web.base.url')

        if not access_token:
            _logger.warning('No se configuró el access token de Mercado Pago')
            return False

        payload = {
            "items": [{
                "title": f"Donación a la Comuna - {self.name}",
                "quantity": 1,
                "unit_price": float(self.monto),
                "currency_id": "ARS",
            }],
            "payer": {
                "name": self.donante_nombre,
                "email": self.donante_email,
            },
            "back_urls": {
                "success": f"{base_url}/donaciones/mp/success",
                "failure": f"{base_url}/donaciones/mp/failure",
                "pending": f"{base_url}/donaciones/mp/pending",
            },
            "auto_return": "approved",
            "external_reference": self.name,
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = req.post(
                "https://api.mercadopago.com/checkout/preferences",
                json=payload,
                headers=headers,
                timeout=10
            )
            data = response.json()
            return data.get('init_point')
        except Exception as e:
            _logger.error(f"Error al crear preferencia MP: {e}")
            return False

    @api.constrains('monto', 'tipo')
    def _check_monto(self):
        for rec in self:
            if rec.tipo == 'dinero' and rec.monto <= 0:
                raise ValidationError('El monto debe ser mayor a cero para donaciones en dinero.')