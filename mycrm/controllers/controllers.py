# -*- coding: utf-8 -*-
from openerp import http

class Mycrm(http.Controller):
    @http.route('/mycrm/mycrm/', auth='public')
    def index(self, **kw):
        return "Hello, world"

#     @http.route('/mycrm/mycrm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mycrm.listing', {
#             'root': '/mycrm/mycrm',
#             'objects': http.request.env['mycrm.mycrm'].search([]),
#         })

#     @http.route('/mycrm/mycrm/objects/<model("mycrm.mycrm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mycrm.object', {
#             'object': obj
#         })