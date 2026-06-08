# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TurnosComunaArea(models.Model):
    _name = 'turnos_comuna.area'
    _description = 'Área de Atención'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
    )
    description = fields.Text(
        string='Descripción',
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
    )
    horario_atencion = fields.Text(
        string='Horario de Atención',
        help='Ingrese el horario de atención, ej: Lunes a Viernes de 8:00 a 14:00',
    )
    duracion_turno = fields.Integer(
        string='Duración del Turno (minutos)',
        default=30,
        help='Duración estimada de cada turno en minutos',
    )
    turno_ids = fields.One2many(
        'turnos_comuna.turno',
        'area_id',
        string='Turnos',
    )
    turno_count = fields.Integer(
        string='Cantidad de Turnos',
        compute='_compute_turno_count',
    )

    @api.depends('turno_ids')
    def _compute_turno_count(self):
        for rec in self:
            rec.turno_count = len(rec.turno_ids)

    def action_ver_turnos(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Turnos de %s' % self.name,
            'res_model': 'turnos_comuna.turno',
            'view_mode': 'list,form',
            'domain': [('area_id', '=', self.id)],
            'context': {'default_area_id': self.id},
        }