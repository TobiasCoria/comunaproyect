from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class PagoComuna(models.Model):
    _name = 'pagos_comuna.pago'
    _description = 'Pago'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_vencimiento'

    name = fields.Char(
        string='Nº Comprobante',
        readonly=True,
        copy=False,
        default='Nuevo'
    )
    vecino_id = fields.Many2one(
        'tc.vecino',
        string='Vecino',
        required=True,
        tracking=True
    )
    concepto_id = fields.Many2one(
        'pagos_comuna.concepto',
        string='Concepto',
        required=True,
        tracking=True
    )
    tipo = fields.Selection(
        related='concepto_id.tipo',
        string='Tipo',
        store=True
    )
    fecha_emision = fields.Date(
        string='Fecha de emisión',
        default=fields.Date.today,
        required=True
    )
    fecha_vencimiento = fields.Date(
        string='Fecha de vencimiento',
        required=True,
        tracking=True
    )
    fecha_pago = fields.Date(
        string='Fecha de pago',
        tracking=True
    )
    monto = fields.Float(
        string='Monto',
        digits=(10, 2),
        required=True
    )
    cuota_nro = fields.Integer(
        string='Cuota Nº'
    )
    cuota_total = fields.Integer(
        string='Total cuotas'
    )
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('vencido', 'Vencido'),
        ('anulado', 'Anulado'),
    ], string='Estado', default='pendiente', tracking=True)
    notas = fields.Text(string='Notas')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('pagos_comuna.pago') or 'Nuevo'
        return super().create(vals_list)

    @api.onchange('concepto_id')
    def _onchange_concepto(self):
        if self.concepto_id:
            self.monto = self.concepto_id.monto_base

    def action_marcar_pagado(self):
        for rec in self:
            rec.estado = 'pagado'
            rec.fecha_pago = date.today()

    def action_marcar_vencido(self):
        for rec in self:
            if rec.estado == 'pendiente':
                rec.estado = 'vencido'

    def action_anular(self):
        for rec in self:
            rec.estado = 'anulado'

    def action_generar_recibo(self):
        return self.env.ref('pagos_comuna.action_report_recibo_pago').report_action(self)

    @api.constrains('fecha_vencimiento', 'fecha_emision')
    def _check_fechas(self):
        for rec in self:
            if rec.fecha_vencimiento and rec.fecha_emision:
                if rec.fecha_vencimiento < rec.fecha_emision:
                    raise ValidationError('La fecha de vencimiento no puede ser anterior a la fecha de emisión.')