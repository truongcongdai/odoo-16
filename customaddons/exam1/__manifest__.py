# -*- coding: utf-8 -*-
{
    'name': "Crm-Sales",

    'summary': """
        Crm-Sales""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Dai",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'crm', 'sale','sale_crm'],

    # always loaded
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/inherit_crm_lead.xml',
        'views/inherit_sales_team.xml',
        'views/s_plan_sale_order.xml',
        'views/s_indicator_evaluation.xml',
        'views/inherit_sale_order.xml',
        'wizard/report_indicator_evaluation.xml',
        'wizard/report_inherit_crm_lead.xml',
    ],

}
