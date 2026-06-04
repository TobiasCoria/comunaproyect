# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class CierreCajaDiario(models.Model):
    _name = 'cierre.caja.diario'
    _description = 'Cierre de Caja Diario - Comuna'
    _order = 'fecha desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
        tracking=True,
    )
    fecha = fields.Date(
        string='Fecha de Cierre',
        required=True,
        default=fields.Date.today,
        tracking=True,
        index=True,
    )
    responsable_id = fields.Many2one(
        'hr.employee',
        string='Responsable de Caja',
        required=True,
        tracking=True,
        default=lambda self: self.env.user.employee_id,
    )
    aprobado_por_id = fields.Many2one(
        'hr.employee',
        string='Aprobado por',
        tracking=True,
        readonly=True,
    )
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('en_revision', 'En Revisión'),
        ('cerrado', 'Cerrado'),
        ('cancelado', 'Cancelado'),
    ], string='Estado', default='borrador', tracking=True, required=True)

    movimiento_ids = fields.One2many(
        'cierre.caja.movimiento',
        'cierre_id',
        string='Movimientos del Día',
    )

    # ── Totales calculados ──────────────────────────────────────────────────────
    total_ingresos = fields.Monetary(
        string='Total Ingresos',
        currency_field='moneda_id',
        compute='_compute_totales',
        store=True,
    )
    total_egresos = fields.Monetary(
        string='Total Egresos',
        currency_field='moneda_id',
        compute='_compute_totales',
        store=True,
    )
    total_transferencias = fields.Monetary(
        string='Total Transferencias',
        currency_field='moneda_id',
        compute='_compute_totales',
        store=True,
    )
    saldo_neto = fields.Monetary(
        string='Saldo Neto del Día',
        currency_field='moneda_id',
        compute='_compute_totales',
        store=True,
    )
    cantidad_movimientos = fields.Integer(
        string='Cantidad de Movimientos',
        compute='_compute_totales',
        store=True,
    )
    moneda_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.ref('base.ARS'),
        required=True,
    )

    # ── Resumen por cuenta ──────────────────────────────────────────────────────
    resumen_cuenta_ids = fields.One2many(
        'cierre.caja.resumen.cuenta',
        'cierre_id',
        string='Resumen por Cuenta',
        compute='_compute_resumen_cuentas',
        store=True,
    )

    observaciones = fields.Text(string='Observaciones del Cierre')
    fecha_cierre_real = fields.Datetime(string='Fecha/Hora de Cierre Real', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('cierre.caja.diario') or 'Nuevo'
        return super().create(vals_list)

    @api.depends(
        'movimiento_ids.monto',
        'movimiento_ids.tipo_operacion',
        'movimiento_ids.state',
    )
    def _compute_totales(self):
        for rec in self:
            movs_confirmados = rec.movimiento_ids.filtered(lambda m: m.state == 'confirmado')
            rec.total_ingresos = sum(
                m.monto for m in movs_confirmados if m.tipo_operacion == 'ingreso'
            )
            rec.total_egresos = sum(
                m.monto for m in movs_confirmados if m.tipo_operacion == 'egreso'
            )
            rec.total_transferencias = sum(
                m.monto for m in movs_confirmados if m.tipo_operacion == 'transferencia'
            )
            rec.saldo_neto = rec.total_ingresos - rec.total_egresos
            rec.cantidad_movimientos = len(movs_confirmados)

    @api.depends('movimiento_ids', 'movimiento_ids.cuenta_id', 'movimiento_ids.state',
                 'movimiento_ids.monto', 'movimiento_ids.tipo_operacion')
    def _compute_resumen_cuentas(self):
        ResumenCuenta = self.env['cierre.caja.resumen.cuenta']
        for rec in self:
            # Eliminar resúmenes anteriores
            rec.resumen_cuenta_ids.unlink()
            cuentas = rec.movimiento_ids.filtered(
                lambda m: m.state == 'confirmado'
            ).mapped('cuenta_id')
            nuevos_resumenes = []
            for cuenta in cuentas:
                movs = rec.movimiento_ids.filtered(
                    lambda m: m.cuenta_id == cuenta and m.state == 'confirmado'
                )
                ingresos = sum(m.monto for m in movs if m.tipo_operacion == 'ingreso')
                egresos = sum(m.monto for m in movs if m.tipo_operacion == 'egreso')
                nuevos_resumenes.append({
                    'cierre_id': rec.id,
                    'cuenta_id': cuenta.id,
                    'total_ingresos': ingresos,
                    'total_egresos': egresos,
                    'saldo_neto': ingresos - egresos,
                    'cantidad_movimientos': len(movs),
                })
            if nuevos_resumenes:
                ResumenCuenta.create(nuevos_resumenes)

    # ── Flujo de estados ────────────────────────────────────────────────────────
    def action_enviar_revision(self):
        for rec in self:
            if not rec.movimiento_ids:
                raise UserError('No se puede enviar a revisión un cierre sin movimientos.')
            rec.state = 'en_revision'

    def action_cerrar(self):
        for rec in self:
            movs_borrador = rec.movimiento_ids.filtered(lambda m: m.state == 'borrador')
            if movs_borrador:
                raise UserError(
                    f'Hay {len(movs_borrador)} movimiento(s) en borrador. '
                    'Confirme o cancele todos los movimientos antes de cerrar.'
                )
            rec.state = 'cerrado'
            rec.aprobado_por_id = self.env.user.employee_id.id
            rec.fecha_cierre_real = fields.Datetime.now()

    def action_cancelar(self):
        for rec in self:
            if rec.state == 'cerrado':
                raise UserError('No se puede cancelar un cierre ya finalizado.')
            rec.state = 'cancelado'

    def action_reabrir(self):
        for rec in self:
            rec.state = 'borrador'
            rec.aprobado_por_id = False
            rec.fecha_cierre_real = False

    def action_imprimir(self):
        return self.env.ref('cierre_caja_comuna.action_report_cierre_caja').report_action(self)

    @api.constrains('fecha')
    def _check_fecha_unica(self):
        for rec in self:
            duplicado = self.search([
                ('fecha', '=', rec.fecha),
                ('id', '!=', rec.id),
                ('state', '!=', 'cancelado'),
            ], limit=1)
            if duplicado:
                raise ValidationError(
                    f'Ya existe un cierre de caja para la fecha {rec.fecha}. '
                    f'Referencia: {duplicado.name}'
                )


class CierreCajaResumenCuenta(models.Model):
    _name = 'cierre.caja.resumen.cuenta'
    _description = 'Resumen por Cuenta del Cierre de Caja'
    _order = 'cuenta_id'

    cierre_id = fields.Many2one(
        'cierre.caja.diario',
        string='Cierre',
        required=True,
        ondelete='cascade',
        index=True,
    )
    cuenta_id = fields.Many2one(
        'cierre.caja.cuenta.bancaria',
        string='Cuenta',
        required=True,
    )
    moneda_id = fields.Many2one(
        'res.currency',
        related='cuenta_id.moneda_id',
        string='Moneda',
        store=True,
    )
    total_ingresos = fields.Monetary(string='Ingresos', currency_field='moneda_id')
    total_egresos = fields.Monetary(string='Egresos', currency_field='moneda_id')
    saldo_neto = fields.Monetary(string='Saldo Neto', currency_field='moneda_id')
    cantidad_movimientos = fields.Integer(string='Movimientos')
