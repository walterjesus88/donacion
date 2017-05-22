# -*- encoding: utf-8 -*-

{
    'name': 'Remove Export Option',
    'description': 'Remove the \'Export\' option from the \'More\' menu...',
    'version': '1.0',
    'author': 'Kanak Infosystems LLP.',
    'website': 'http://www.kanakinfosystems.com',
    'images': ['static/description/main_screenshot.png'],
    'category': 'Web',
    'description': """

Remove the 'Export' option from the 'More' menu using hide group...
in the list view except for the admin user

""",
    'depends': ['web'],
    'data': [
        'security/partner_extended_security.xml',
        'view/disable_export_view.xml',
    ],
    'auto_install': False,
}
