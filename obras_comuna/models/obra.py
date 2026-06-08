from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Obra(models.Model):
    _name = 'obras_comuna.obra'
    _description = 'Obra pública'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_inicio desc'

    name = fields.Char(
        string='Nombre de la obra',
        required=True,
        tracking=True
    )
    numero_obra = fields.Char(
        string='Nº Obra',
        readonly=True,
        copy=False,
        default='Nuevo'
    )
    descripcion = fields.Text(
        string='Descripción'
    )
    ubicacion = fields.Char(
        string='Ubicación',
        required=True
    )
    barrio = fields.Char(
        string='Barrio'
    )
    tipo = fields.Selection([
        ('vial', 'Obra vial'),
        ('sanitaria', 'Obra sanitaria'),
        ('electrica', 'Obra eléctrica'),
        ('edilicia', 'Obra edilicia'),
        ('espacio_publico', 'Espacio público'),
        ('otro', 'Otro'),
    ], string='Tipo de obra', required=True)
    prioridad = fields.Selection([
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ], string='Prioridad', default='media', tracking=True)
    estado = fields.Selection([
        ('planificada', 'Planificada'),
        ('en_ejecucion', 'En ejecución'),
        ('pausada', 'Pausada'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ], string='Estado', default='planificada', tracking=True)
    responsable_id = fields.Many2one(
        'res.users',
        string='Responsable',
        tracking=True
    )
    cuadrilla_id = fields.Many2one(
        'obras_comuna.cuadrilla',
        string='Cuadrilla asignada',
        tracking=True
    )
    fecha_inicio = fields.Date(
        string='Fecha de inicio',
        tracking=True
    )
    fecha_fin_estimada = fields.Date(
        string='Fecha fin estimada',
        tracking=True
    )
    fecha_fin_real = fields.Date(
        string='Fecha fin real',
        tracking=True
    )
    presupuesto = fields.Float(
        string='Presupuesto',
        digits=(10, 2)
    )
    costo_real = fields.Float(
        string='Costo real',
        digits=(10, 2)
    )
    porcentaje_avance = fields.Integer(
        string='Avance (%)',
        default=0,
        tracking=True
    )
    avance_ids = fields.One2many(
        'obras_comuna.avance',
        'obra_id',
        string='Registro de avances'
    )
    notas = fields.Text(
        string='Notas'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('numero_obra', 'Nuevo') == 'Nuevo':
                vals['numero_obra'] = self.env['ir.sequence'].next_by_code('obras_comuna.obra') or 'Nuevo'
        return super().create(vals_list)

    def action_iniciar(self):
        for rec in self:
            rec.estado = 'en_ejecucion'

    def action_pausar(self):
        for rec in self:
            rec.estado = 'pausada'

    def action_finalizar(self):
        for rec in self:
            rec.estado = 'finalizada'
            if not rec.fecha_fin_real:
                rec.fecha_fin_real = fields.Date.today()

    def action_cancelar(self):
        for rec in self:
            rec.estado = 'cancelada'

    def action_generar_informe(self):
        return self.env.ref('obras_comuna.action_report_informe_obra').report_action(self)

    @api.constrains('porcentaje_avance')
    def _check_porcentaje(self):
        for rec in self:
            if rec.porcentaje_avance < 0 or rec.porcentaje_avance > 100:
                raise ValidationError('El porcentaje de avance debe estar entre 0 y 100.')


class AvanceObra(models.Model):
    _name = 'obras_comuna.avance'
    _description = 'Avance de obra'
    _order = 'fecha desc'

    obra_id = fields.Many2one(
        'obras_comuna.obra',
        string='Obra',
        required=True,
        ondelete='cascade'
    )
    fecha = fields.Date(
        string='Fecha',
        required=True,
        default=fields.Date.today
    )
    porcentaje = fields.Integer(
        string='Avance (%)',
        required=True
    )
    descripcion = fields.Text(
        string='Descripción del avance',
        required=True
    )
    responsable_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user
    )