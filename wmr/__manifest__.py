{
    'name': 'Welding Material Requisition',
    'version': '1.0',
    'summary': 'Tes Module WMR',
    'author': 'Lucky Deva',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'depends': ['base','sales_custom','purchase','stock','web'],
    'data': [
        'security/ir.model.access.csv',
        'views/submenu.xml',
        'views/wmr_form_views.xml',
        'views/wmr_list_views.xml',
        'views/pok_form_views.xml',
        'views/pok_list_views.xml',
        'views/order_kerja_views.xml',
        'views/order_kerja_detail_views.xml',
        'report/wmr_report_action.xml',
        'report/wmr_report_template.xml',
        'report/pok_report_action.xml',
        'report/pok_report_template.xml',
        'report/ok_report_action.xml',
        'report/ok_report_template.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'wmr/static/src/img/logo_puspetindo.png',
    ],
},

    'assets': {
        'web.report_assets_common': [
            'wmr/static/src/img/logo_puspetindo.png',
        ],
        'web.assets_backend': [
            'wmr/static/src/img/logo_puspetindo.png',
            'wmr/static/src/js/document_number_notifier.js',
        ],
    },


    "installable": True,
    "application": True
}