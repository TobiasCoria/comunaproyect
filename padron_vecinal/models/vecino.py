from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Vecino(models.Model):
    _name = 'tc.vecino'
    _description = 'Vecino'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'numero_padron'

    # Datos personales
    numero_padron = fields.Char(
        string='Nº Padrón',
        readonly=True,
        copy=False,
        default='Nuevo'
    )
    name = fields.Char(
        string='Nombre completo',
        required=True,
        tracking=True
    )
    dni = fields.Char(
        string='DNI',
        required=True,
        tracking=True
    )
    fecha_nacimiento = fields.Date(
        string='Fecha de nacimiento'
    )
    edad = fields.Integer(
        string='Edad',
        compute='_compute_edad',
        store=False
    )
    genero = fields.Selection([
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
    ], string='Género')
    foto = fields.Image(
        string='Foto',
        max_width=256,
        max_height=256
    )
    estado = fields.Selection([
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('fallecido', 'Fallecido'),
    ], string='Estado', default='activo', tracking=True)

    # Contacto
    direccion = fields.Char(string='Dirección')
    barrio = fields.Char(string='Barrio')
    localidad = fields.Char(string='Localidad', default='')
    telefono = fields.Char(string='Teléfono')
    email = fields.Char(string='Email')

    # Grupo familiar
    familiar_ids = fields.Many2many(
        'tc.vecino',
        'tc_vecino_familiar_rel',
        'vecino_id',
        'familiar_id',
        string='Grupo familiar'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('numero_padron', 'Nuevo') == 'Nuevo':
                vals['numero_padron'] = self.env['ir.sequence'].next_by_code('tc.vecino') or 'Nuevo'
        return super().create(vals_list)

    @api.depends('fecha_nacimiento')
    def _compute_edad(self):
        from datetime import date
        for rec in self:
            if rec.fecha_nacimiento:
                hoy = date.today()
                rec.edad = hoy.year - rec.fecha_nacimiento.year - (
                    (hoy.month, hoy.day) < (rec.fecha_nacimiento.month, rec.fecha_nacimiento.day)
                )
            else:
                rec.edad = 0

    @api.constrains('dni')
    def _check_dni_unico(self):
        for rec in self:
            duplicado = self.search([('dni', '=', rec.dni), ('id', '!=', rec.id)])
            if duplicado:
                raise ValidationError('Ya existe un vecino con ese DNI.')

    def action_generar_constancia(self):
        return self.env.ref('padron_vecinal.action_report_constancia_residencia').report_action(self)