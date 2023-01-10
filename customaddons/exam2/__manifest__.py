{
    'name': "Purchase",
    'sumamary': """Purchase""",
    'description': """Long description of module's purpose""",
    'author': "Dai",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'purchase', 'hr'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/inherit_purchase_order.xml',
        'views/inherit_hr_department.xml',
        'views/s_limit_purchase_order.xml',
        'wizard/report_purchase.xml',
    ],
    'demo': [
        'demo/inherit_hr_department_demo.xml'
    ]
}
