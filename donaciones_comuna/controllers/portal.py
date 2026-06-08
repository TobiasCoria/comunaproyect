from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class DonacionPortal(http.Controller):

    @http.route('/donaciones', type='http', auth='public', website=True)
    def portal_donaciones(self, **kwargs):
        return request.render('donaciones_comuna.portal_donacion_form', {
            'page_title': 'Hacer una donación',
        })

    @http.route('/donaciones/confirmar', type='http', auth='public', website=True, methods=['POST'])
    def confirmar_donacion(self, **kwargs):
        nombre = kwargs.get('donante_nombre')
        email = kwargs.get('donante_email')
        telefono = kwargs.get('donante_telefono')
        dni = kwargs.get('donante_dni')
        tipo = kwargs.get('tipo', 'dinero')
        monto = float(kwargs.get('monto', 0))
        descripcion = kwargs.get('descripcion')
        destino = kwargs.get('destino')
        metodo_pago = kwargs.get('metodo_pago', 'mercadopago')

        donacion = request.env['donaciones_comuna.donacion'].sudo().create({
            'donante_nombre': nombre,
            'donante_email': email,
            'donante_telefono': telefono,
            'donante_dni': dni,
            'tipo': tipo,
            'monto': monto,
            'descripcion': descripcion,
            'destino': destino,
            'metodo_pago': metodo_pago,
        })

        if metodo_pago == 'mercadopago' and tipo == 'dinero':
            mp_url = donacion._generar_link_mercadopago()
            if mp_url:
                return request.redirect(mp_url)

        return request.render('donaciones_comuna.portal_donacion_gracias', {
            'donacion': donacion,
        })

    @http.route('/donaciones/mp/success', type='http', auth='public', website=True)
    def mp_success(self, **kwargs):
        payment_id = kwargs.get('payment_id')
        status = kwargs.get('status')
        external_reference = kwargs.get('external_reference')

        if external_reference:
            donacion = request.env['donaciones_comuna.donacion'].sudo().search([
                ('name', '=', external_reference)
            ], limit=1)
            if donacion:
                donacion.write({
                    'mp_payment_id': payment_id,
                    'mp_status': status,
                    'estado': 'recibida' if status == 'approved' else 'pendiente',
                })

        return request.render('donaciones_comuna.portal_donacion_gracias', {
            'donacion': donacion if external_reference else None,
        })

    @http.route('/donaciones/mp/failure', type='http', auth='public', website=True)
    def mp_failure(self, **kwargs):
        return request.render('donaciones_comuna.portal_donacion_error', {
            'mensaje': 'El pago no pudo procesarse. Por favor intentá de nuevo.',
        })

    @http.route('/donaciones/mp/pending', type='http', auth='public', website=True)
    def mp_pending(self, **kwargs):
        return request.render('donaciones_comuna.portal_donacion_error', {
            'mensaje': 'Tu pago está pendiente de confirmación. Te avisaremos por email.',
        })