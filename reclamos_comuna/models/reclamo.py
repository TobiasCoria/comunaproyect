# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Reclamo(models.Model):
    _name = 'reclamos_comuna.reclamo'
    _description = 'Reclamo de Vecino'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_ingreso desc, name desc'
    _rec_name = 'name'

    # ─── Identificación ───────────────────────────────────────────────────────
    name = fields.Char(
        string='Número de Reclamo',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
        index=True,
    )

    # ─── Datos principales ────────────────────────────────────────────────────
    vecino_id = fields.Many2one(
        comodel_name='tc.vecino',
        string='Vecino',
        required=True,
        tracking=True,
        index=True,
    )
    categoria_id = fields.Many2one(
        comodel_name='reclamos_comuna.categoria',
        string='Categoría',
        required=True,
        tracking=True,
        index=True,
    )
    titulo = fields.Char(
        string='Título',
        required=True,
        tracking=True,
    )
    descripcion = fields.Text(
        string='Descripción',
    )
    direccion_reclamo = fields.Char(
        string='Dirección del Reclamo',
    )

    # ─── Prioridad y estado ───────────────────────────────────────────────────
    prioridad = fields.Selection(
        selection=[
            ('0', 'Baja'),
            ('1', 'Media'),
            ('2', 'Alta'),
        ],
        string='Prioridad',
        default='0',
        tracking=True,
        index=True,
    )
    state = fields.Selection(
        selection=[
            ('nuevo', 'Nuevo'),
            ('en_proceso', 'En Proceso'),
            ('resuelto', 'Resuelto'),
            ('cerrado', 'Cerrado'),
            ('rechazado', 'Rechazado'),
        ],
        string='Estado',
        default='nuevo',
        required=True,
        tracking=True,
        index=True,
        copy=False,
    )

    # ─── Responsable y fechas ─────────────────────────────────────────────────
    responsable_id = fields.Many2one(
        comodel_name='res.users',
        string='Empleado Responsable',
        tracking=True,
        index=True,
    )
    fecha_ingreso = fields.Datetime(
        string='Fecha de Ingreso',
        default=fields.Datetime.now,
        readonly=True,
        copy=False,
    )
    fecha_resolucion = fields.Datetime(
        string='Fecha de Resolución',
        tracking=True,
        copy=False,
    )

    # ─── Notas internas ───────────────────────────────────────────────────────
    notas_internas = fields.Text(
        string='Notas Internas',
    )

    # ─── Campos computados de color ───────────────────────────────────────────
    color = fields.Integer(
        string='Color',
        compute='_compute_color',
    )
    priority = fields.Selection(
        related='prioridad',
        string='Priority',
    )

    # ─── Compute methods ──────────────────────────────────────────────────────
    @api.depends('state')
    def _compute_color(self):
        color_map = {
            'nuevo': 0,
            'en_proceso': 3,   # naranja
            'resuelto': 10,    # verde
            'cerrado': 1,
            'rechazado': 9,    # rojo
        }
        for rec in self:
            rec.color = color_map.get(rec.state, 0)

    # ─── Create (Odoo 19: siempre @api.model_create_multi con vals_list) ──────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'reclamos_comuna.reclamo'
                ) or 'Nuevo'
        return super().create(vals_list)

    # ─── Acciones de botones ──────────────────────────────────────────────────
    def action_tomar_reclamo(self):
        """Asigna el usuario actual como responsable y pasa a 'En Proceso'."""
        for rec in self:
            if rec.state not in ('nuevo', 'en_proceso'):
                raise UserError(
                    _('Solo se puede tomar un reclamo en estado Nuevo o En Proceso.')
                )
            rec.write({
                'responsable_id': self.env.user.id,
                'state': 'en_proceso',
            })
            rec.message_post(
                body=_('Reclamo tomado por %s.') % self.env.user.name,
                subtype_xmlid='mail.mt_note',
            )

    def action_marcar_resuelto(self):
        """Marca el reclamo como resuelto y registra la fecha de resolución."""
        for rec in self:
            if rec.state not in ('nuevo', 'en_proceso'):
                raise UserError(
                    _('Solo se puede resolver un reclamo en estado Nuevo o En Proceso.')
                )
            rec.write({
                'state': 'resuelto',
                'fecha_resolucion': fields.Datetime.now(),
            })
            rec.message_post(
                body=_('Reclamo marcado como resuelto.'),
                subtype_xmlid='mail.mt_note',
            )

    def action_cerrar(self):
        """Cierra el reclamo."""
        for rec in self:
            if rec.state == 'rechazado':
                raise UserError(_('No se puede cerrar un reclamo rechazado.'))
            if rec.state == 'cerrado':
                raise UserError(_('El reclamo ya está cerrado.'))
            rec.write({'state': 'cerrado'})
            rec.message_post(
                body=_('Reclamo cerrado.'),
                subtype_xmlid='mail.mt_note',
            )

    def action_rechazar(self):
        """Rechaza el reclamo."""
        for rec in self:
            if rec.state in ('resuelto', 'cerrado', 'rechazado'):
                raise UserError(
                    _('No se puede rechazar un reclamo %s.') % dict(
                        self._fields['state'].selection
                    ).get(rec.state)
                )
            rec.write({'state': 'rechazado'})
            rec.message_post(
                body=_('Reclamo rechazado.'),
                subtype_xmlid='mail.mt_note',
            )

    def action_print_reclamo(self):
        """Imprime el comprobante de reclamo."""
        return self.env.ref(
            'reclamos_comuna.action_report_reclamo'
        ).report_action(self)
