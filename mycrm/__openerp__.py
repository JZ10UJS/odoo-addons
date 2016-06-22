# -*- coding: utf-8 -*-
{
    'name': "YouYun CRM",

    'summary': """
        This is a customized CRM for YouYun based on the basic CRM""",

    'description': """
        Dada...
    """,

    'author': "Zhang Jie",
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
        'views/sale_group.xml',
        'security/ir.model.access.csv',
        'security/calendar_rule_for_all.xml',
        'views/views.xml',
        'views/templates.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application':True,
}