import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TcShop(http.Controller):

    def _get_or_create_cart(self):
        session_id = request.session.sid
        _logger.info('SESSION ID: %s', session_id)
        cart = request.env['tc.cart'].sudo().search([
            ('session_id', '=', session_id),
            ('state', '=', 'draft')
        ], limit=1)
        _logger.info('CART FOUND: %s LINES: %s', cart.id, len(cart.line_ids))
        if not cart:
            cart = request.env['tc.cart'].sudo().create({
                'session_id': session_id,
            })
        return cart

    @http.route('/tc-shop', auth='public', website=True, multilang=False)
    def shop_index(self, category_id=None, **kwargs):
        domain = [('active', '=', True), ('stock', '>', 0)]
        if category_id:
            domain.append(('category_id', '=', int(category_id)))
        products = request.env['tc.product'].sudo().search(domain)
        categories = request.env['tc.product.category'].sudo().search([])
        cart = self._get_or_create_cart()
        return request.render('tc_ecommerce.shop_index', {
            'products': products,
            'categories': categories,
            'current_category': int(category_id) if category_id else None,
            'cart': cart,
        })

    @http.route('/tc-shop/product/<int:product_id>', auth='public', website=True, multilang=False)
    def shop_product(self, product_id, **kwargs):
        product = request.env['tc.product'].sudo().browse(product_id)
        if not product.exists():
            return request.redirect('/tc-shop')
        cart = self._get_or_create_cart()
        return request.render('tc_ecommerce.shop_product', {
            'product': product,
            'cart': cart,
        })

    @http.route('/tc-shop/cart/add', auth='public', website=True, multilang=False, methods=['POST'])
    def cart_add(self, product_id, quantity=1, **kwargs):
        cart = self._get_or_create_cart()
        product = request.env['tc.product'].sudo().browse(int(product_id))
        if not product.exists():
            return request.redirect('/tc-shop')
        existing_line = cart.line_ids.filtered(lambda l: l.product_id.id == product.id)
        if existing_line:
            existing_line.sudo().write({'quantity': existing_line.quantity + int(quantity)})
        else:
            cart.sudo().write({
                'line_ids': [(0, 0, {
                    'product_id': product.id,
                    'quantity': int(quantity),
                })]
            })
        return request.redirect('/tc-shop/cart')

    @http.route('/tc-shop/cart', auth='public', website=True, multilang=False)
    def cart_view(self, **kwargs):
        cart = self._get_or_create_cart()
        return request.render('tc_ecommerce.shop_cart', {
            'cart': cart,
        })

    @http.route('/tc-shop/cart/remove/<int:line_id>', auth='public', website=True, multilang=False)
    def cart_remove(self, line_id, **kwargs):
        cart = self._get_or_create_cart()
        line = cart.line_ids.filtered(lambda l: l.id == line_id)
        if line:
            line.sudo().unlink()
        return request.redirect('/tc-shop/cart')

    @http.route('/tc-shop/checkout', auth='public', website=True, multilang=False)
    def checkout(self, **kwargs):
        cart = self._get_or_create_cart()
        if not cart.line_ids:
            return request.redirect('/tc-shop')
        return request.render('tc_ecommerce.shop_checkout', {
            'cart': cart,
        })

    @http.route('/tc-shop/checkout/submit', auth='public', website=True, multilang=False, methods=['POST'])
    def checkout_submit(self, partner_name, partner_email, partner_address, partner_phone=None, notes=None, **kwargs):
        cart = self._get_or_create_cart()
        if not cart.line_ids:
            return request.redirect('/tc-shop')
        order = request.env['tc.order'].sudo().create({
            'partner_name': partner_name,
            'partner_email': partner_email,
            'partner_phone': partner_phone,
            'partner_address': partner_address,
            'notes': notes,
            'line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'price': line.price,
            }) for line in cart.line_ids]
        })
        order.action_confirm()
        cart.sudo().write({'state': 'confirmed'})
        return request.render('tc_ecommerce.shop_confirmation', {
            'order': order,
        })