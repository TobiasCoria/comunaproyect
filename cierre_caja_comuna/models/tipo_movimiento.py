# -*- coding: utf-8 -*-
from odoo import models, fields


class TipoMovimiento(models.Model):
    _name = 'cierre.caja.tipo.movimiento'
    _description = 'Tipo de Movimiento de Caja'
    _order = 'nombre'

    nombre = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
    )
    codigo = fields.Char(
        string='Código',
        required=True,
        size=10,
    )
    tipo = fields.Selection([
        ('ingreso', 'Ingreso'),
        ('egreso', 'Egreso'),
        ('transferencia', 'Transferencia'),
    ], string='Tipo', required=True, default='ingreso')

    descripcion = fields.Text(string='Descripción')
    active = fields.Boolean(string='Activo', default=True)
    color = fields.Integer(string='Color', default=0)

    _sql_constraints = [
        ('codigo_uniq', 'UNIQUE(codigo)', 'El código del tipo de movimiento debe ser único.'),
    ]
