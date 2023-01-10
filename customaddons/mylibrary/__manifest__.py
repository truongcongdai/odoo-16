# {
#     'name':'My library',
#     'summary': 'Manage books easily',
#     'decription':"""""",
#     'author':"Dai",
#     'category':'Uncategorized',
#     'website': "http://www.example.com",
#     'version': "13.0.1",
#     'depends': ['base'],
#     'data':[
#         'security/groups.xml',
#         'security/ir.model.access.csv',
#         'views/library_book.xml',
#         'views/library_book_categ.xml',
#         'views/library_book_rent.xml',
#         # 'views/res_config_settings_view.xml',
#         'data/data.xml',
#     ],
#     'demo':[
#         'data/demo.xml'
#     ]
# }

{
    'name': "My Library",  # Module title
    'summary': "Manage books easily",  # Module subtitle phrase
    'description': """
Manage Library
==============
Description related to library.
    """,  # Supports reStructuredText(RST) format
    'author': "Parth Gajjar",
    'website': "http://www.example.com",
    'category': 'Library',
    'version': '14.0.1',
    'depends': ['base'],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/library_book.xml'
    ],

    # This demo data files will be loaded if db initialize with demo data (commented because file is not added in this example)
    # 'demo': [
    #     'demo.xml'
    # ],
}