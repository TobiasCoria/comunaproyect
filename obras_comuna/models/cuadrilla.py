from odoo import models, fields

class Cuadrilla(models.Model):
    _name = 'obras_comuna.cuadrilla'
    _description = 'Cuadrilla de trabajo'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    responsable_id = fields.Many2one(
        'res.users',
        string='Responsable'
    )
    descripcion = fields.Text(
        string='Descripción'
    )
    activo = fields.Boolean(
        string='Activo',
        default=True
    )
    miembro_ids = fields.Many2many(
        'res.users',
        'obras_cuadrilla_miembro_rel',
        'cuadrilla_id',
        'user_id',
        string='Miembros'
    )
    obra_ids = fields.One2many(
        'obras_comuna.obra',
        'cuadrilla_id',
        string='Obras asignadas'
    )
    cantidad_obras = fields.Integer(
        string='Obras asignadas',
        compute='_compute_cantidad_obras',
        store=True
    )

    def _compute_cantidad_obras(self):
        for rec in self:
            rec.cantidad_obras = len(rec.obra_ids)