# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TurnosComunaTurno(models.Model):
    _name = "turnos_comuna.turno"
    _description = "Turno de Atencion"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "fecha_hora desc"
    _rec_name = "numero_turno"

    numero_turno = fields.Char(
        string="Numero de Turno",
        readonly=True,
        copy=False,
        default="Nuevo",
        index=True,
    )
    vecino_id = fields.Many2one(
        comodel_name="tc.vecino",
        string="Vecino",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    area_id = fields.Many2one(
        comodel_name="turnos_comuna.area",
        string="Area",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    fecha_hora = fields.Datetime(
        string="Fecha y Hora del Turno",
        required=True,
        tracking=True,
    )
    motivo = fields.Text(
        string="Motivo de la Consulta",
    )
    empleado_id = fields.Many2one(
        comodel_name="res.users",
        string="Empleado Asignado",
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ("reservado", "Reservado"),
            ("confirmado", "Confirmado"),
            ("presente", "Presente"),
            ("ausente", "Ausente"),
            ("cancelado", "Cancelado"),
        ],
        string="Estado",
        default="reservado",
        required=True,
        tracking=True,
    )
    notas = fields.Text(
        string="Notas",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("numero_turno", "Nuevo") == "Nuevo":
                vals["numero_turno"] = (
                    self.env["ir.sequence"].next_by_code("turnos_comuna.turno")
                    or "Nuevo"
                )
        return super().create(vals_list)

    def action_confirmar(self):
        for rec in self:
            if rec.state != "reservado":
                raise UserError(_("Solo se pueden confirmar turnos en estado Reservado."))
            rec.state = "confirmado"

    def action_presente(self):
        for rec in self:
            if rec.state not in ("reservado", "confirmado"):
                raise UserError(_("Solo se puede marcar presente desde Reservado o Confirmado."))
            rec.state = "presente"

    def action_ausente(self):
        for rec in self:
            if rec.state not in ("reservado", "confirmado"):
                raise UserError(_("Solo se puede marcar ausente desde Reservado o Confirmado."))
            rec.state = "ausente"

    def action_cancelar(self):
        for rec in self:
            if rec.state in ("presente", "cancelado"):
                raise UserError(_("No se puede cancelar un turno ya presente o cancelado."))
            rec.state = "cancelado"

    def action_reset_reservado(self):
        for rec in self:
            if rec.state not in ("cancelado", "ausente"):
                raise UserError(_("Solo se puede revertir a Reservado desde Cancelado o Ausente."))
            rec.state = "reservado"

    def action_print_comprobante(self):
        return self.env.ref("turnos_comuna.action_report_comprobante_turno").report_action(self)