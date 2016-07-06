# -*- coding: utf-8 -*-
from openerp import http

# class Yycrm(http.Controller):
#     @http.route('/yycrm/yycrm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/yycrm/yycrm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('yycrm.listing', {
#             'root': '/yycrm/yycrm',
#             'objects': http.request.env['yycrm.yycrm'].search([]),
#         })

#     @http.route('/yycrm/yycrm/objects/<model("yycrm.yycrm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('yycrm.object', {
#             'object': obj
#         })