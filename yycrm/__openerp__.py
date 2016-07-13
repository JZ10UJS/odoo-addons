# -*- coding: utf-8 -*-
{
    'name': "YouYun CRM",

    'summary': """
        CRM, Sales Management""",

    'description': """
        有云CRM v0.1
    """,

    'author': "Zhang.J",
    'website': "http://www.cloudguarding.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm','sale'],

    # always loaded
    'data': [
        'views/yycrm_sale_group.xml',
        'views/crm_team_data.xml',
        'security/ir.model.access.csv',
        'security/res_partner.xml',
        'security/crm_lead_sale_order.xml',
        'security/yycrm_own_record_rule.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'application': True,
}