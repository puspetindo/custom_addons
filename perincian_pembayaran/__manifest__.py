# custom_addons/perincian_pembayaran/__manifest__.py
{
    'name': 'Perincian Pembayaran',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Vendor Payments',
    'summary': 'Modul untuk mencatat dokumen perincian pembayaran vendor.',
    'description': """
        Modul ini digunakan untuk mendigitalkan dan mengelola proses
        pencatatan dokumen perincian pembayaran kepada vendor.
    """,
    'author': 'Your Name',
    'website': 'https://your.website.com',
    'depends': [
        'account',  # Dependensi ke modul Invoicing/Accounting
    ],
    'data': [    
        'data/payment_detail_line_data.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/payment_detail_views.xml',
        'views/payment_detail_menus.xml',
        'report/perincian_pembayaran_report_action.xml',
        'report/perincian_pembayaran_report_template.xml',
        'report/laporan_pemakian_biaya_report_action.xml',
        'report/laporan_pemakian_biaya_report_template_.xml',
        'report/bukti_bank_keluar_report_action.xml',
        'report/bukti_bank_keluar_report_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
