# -*- coding: utf-8 -*-
{
    'name': 'donacion',

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Minsa",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website','mail','contacts'],

    # always loaded
    'data': [
        'security/donacion_requisito_security.xml',
        'security/mision_requisito_security.xml',
        'security/ir.model.access.csv',
        'templates/templates.xml',
        'templates/templates_mensaje_espera.xml',
        'templates/templates_inicio.xml',
        'templates/templates_requisitos_mision.xml',
        'templates/template.xml',
        'templates/template2.xml',
        'templates/templates_mision.xml',
        'templates/template_alert_ogcti.xml',
        'views/menu.xml',
        'views/views_users.xml',
        'views/views_partner.xml',
        'views/views_mision.xml',
        'views/views_attachement.xml',
        'workflow/mision_workflow.xml',
        'views/views.xml',       
        'workflow/donacion_workflow.xml',
        'data/donacion_categoria_data.xml',
        'data/donacion_roles_data.xml',
        'data/donacion_usuarios_data.xml',
        'data/donacion_categoria_profesional_data.xml',        
        'data/donacion_userdiresas.xml',
        'data/donacion_usuarios_system.xml',

        'static/poschange.xml',      
        'reports/report_proceso_donacion.xml',        
        'reports/report_proceso_mision.xml',        
        'donacion_report.xml',  
        'mision_report.xml',  
    ],
    'qweb': ['static/src/xml/web_printscreen_export.xml'],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',

    ],
}