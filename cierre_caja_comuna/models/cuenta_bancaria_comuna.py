# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CuentaBancariaComunal(models.Model):
    _name = 'cierre.caja.cuenta.bancaria'
    _description = 'Cuenta Bancaria de la Comuna'
    _order = 'nombre'

    nombre = fields.Char(string='Nombre de la Cuenta', required=True)
    banco = fields.Char(string='Banco', required=True)
    numero_cuenta = fields.Char(string='Número de Cuenta', required=True)
    cbu = fields.Char(string='CBU', size=22)
    alias = fields.Char(string='Alias CBU')
    tipo_cuenta = fields.Selection([
        ('corriente', 'Cuenta Corriente'),
        ('caja_ahorro', 'Caja de Ahorro'),
        ('plazo_fijo', 'Plazo Fijo'),
        ('especial', 'Cuenta Especial'),
    ], string='Tipo de Cuenta', required=True, default='corriente')

    moneda_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        required=True,
        default=lambda self: self.env.ref('base.ARS'),
    )
    saldo_inicial = fields.Monetary(
        string='Saldo Inicial',
        currency_field='moneda_id',
        default=0.0,
    )
    saldo_actual = fields.Monetary(
        string='Saldo Actual',
        currency_field='moneda_id',
        compute='_compute_saldo_actual',
        store=True,
    )
    descripcion = fields.Text(string='Descripción / Observaciones')
    active = fields.Boolean(string='Activa', default=True)
    responsable_id = fields.Many2one('hr.employee', string='Responsable')
    movimiento_ids = fields.One2many(
        'cierre.caja.movimiento',
        'cuenta_id',
        string='Movimientos',
    )

    @api.depends('movimiento_ids', 'movimiento_ids.monto', 'movimiento_ids.tipo_operacion',
                 'movimiento_ids.state', 'saldo_inicial')
    def _compute_saldo_actual(self):
        for rec in self:
            ingresos = sum(
                m.monto for m in rec.movimiento_ids
                if m.tipo_operacion == 'ingreso' and m.state == 'confirmado'
            )
            egresos = sum(
                m.monto for m in rec.movimiento_ids
                if m.tipo_operacion == 'egreso' and m.state == 'confirmado'
            )
            rec.saldo_actual = rec.saldo_inicial + ingresos - egresos

    @api.constrains('cbu')
    def _check_cbu(self):
        for rec in self:
            if rec.cbu and len(rec.cbu) != 22:
                raise ValidationError('El CBU debe tener exactamente 22 dígitos.')

    _sql_constraints = [
        ('numero_cuenta_uniq', 'UNIQUE(numero_cuenta)', 'El número de cuenta debe ser único.'),
    ]
