from odoo import models, fields

class ConceptoPago(models.Model):
    _name = 'pagos_comuna.concepto'
    _description = 'Concepto de Pago'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    tipo = fields.Selection([
        ('tasa', 'Tasa municipal'),
        ('servicio', 'Servicio'),
        ('multa', 'Multa'),
        ('otro', 'Otro'),
    ], string='Tipo', required=True, default='tasa')
    descripcion = fields.Text(
        string='Descripción'
    )
    monto_base = fields.Float(
        string='Monto base',
        digits=(10, 2)
    )
    activo = fields.Boolean(
        string='Activo',
        default=True
    )