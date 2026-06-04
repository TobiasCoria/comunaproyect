# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MovimientoBancario(models.Model):
    _name = 'cierre.caja.movimiento'
    _description = 'Movimiento Bancario de la Comuna'
    _order = 'fecha desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
    )
    cierre_id = fields.Many2one(
        'cierre.caja.diario',
        string='Cierre de Caja',
        ondelete='cascade',
        index=True,
    )
    fecha = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    cuenta_id = fields.Many2one(
        'cierre.caja.cuenta.bancaria',
        string='Cuenta Bancaria',
        required=True,
        tracking=True,
    )
    cuenta_destino_id = fields.Many2one(
        'cierre.caja.cuenta.bancaria',
        string='Cuenta Destino',
        help='Completar sólo para transferencias entre cuentas.',
    )
    tipo_movimiento_id = fields.Many2one(
        'cierre.caja.tipo.movimiento',
        string='Tipo de Movimiento',
        required=True,
        tracking=True,
    )
    tipo_operacion = fields.Selection(
        related='tipo_movimiento_id.tipo',
        string='Operación',
        store=True,
        readonly=True,
    )
    concepto = fields.Char(string='Concepto / Descripción', required=True, tracking=True)
    numero_comprobante = fields.Char(string='N° Comprobante / Referencia')
    monto = fields.Monetary(
        string='Monto',
        currency_field='moneda_id',
        required=True,
        tracking=True,
    )
    moneda_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related='cuenta_id.moneda_id',
        store=True,
        readonly=True,
    )
    responsable_id = fields.Many2one(
        'hr.employee',
        string='Responsable',
        required=True,
        default=lambda self: self.env.user.employee_id,
    )
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ], string='Estado', default='borrador', tracking=True, required=True)

    observaciones = fields.Text(string='Observaciones')
    adjunto_ids = fields.Many2many(
        'ir.attachment',
        string='Documentos Adjuntos',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('cierre.caja.movimiento') or 'Nuevo'
        return super().create(vals_list)

    def action_confirmar(self):
        for rec in self:
            if rec.monto <= 0:
                raise ValidationError('El monto del movimiento debe ser mayor a cero.')
            rec.state = 'confirmado'

    def action_cancelar(self):
        for rec in self:
            rec.state = 'cancelado'

    def action_borrador(self):
        for rec in self:
            rec.state = 'borrador'

    @api.constrains('monto')
    def _check_monto(self):
        for rec in self:
            if rec.monto < 0:
                raise ValidationError('El monto no puede ser negativo.')
