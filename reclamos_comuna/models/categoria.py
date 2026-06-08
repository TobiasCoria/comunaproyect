# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ReclamoCategoria(models.Model):
    _name = 'reclamos_comuna.categoria'
    _description = 'Categoría de Reclamo'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
    )

    description = fields.Text(
        string='Descripción',
        translate=True,
    )

    active = fields.Boolean(
        string='Activo',
        default=True,
    )

    reclamo_count = fields.Integer(
        string='Cantidad de Reclamos',
        compute='_compute_reclamo_count',
    )

    @api.depends('name')
    def _compute_reclamo_count(self):
        for rec in self:
            rec.reclamo_count = self.env['reclamos_comuna.reclamo'].search_count(
                [('categoria_id', '=', rec.id)]
            )

    def action_view_reclamos(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Reclamos',
            'res_model': 'reclamos_comuna.reclamo',
            'view_mode': 'list,form',
            'domain': [('categoria_id', '=', self.id)],
            'context': {
                'default_categoria_id': self.id,
            },
        }