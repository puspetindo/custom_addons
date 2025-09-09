{
    "name": "Vendor Payment Detail",
    "version": "1.0",
    "category": "Accounting/Vendor Bills",
    "summary": "Integrasi Perincian Pembayaran dengan Vendor Bill",
    "description": "Modul ini mengintegrasikan perincian pembayaran dengan vendor bill dalam satu model terpadu",
    "author": "Your Name",
    "website": "https://your.website.com",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "views/vendor_payment_detail_views.xml",
        "report/perincian_pembayaran_report_action.xml",
        "report/laporan_pemakian_biaya_report_action.xml",
        "report/bukti_bank_keluar_report_action.xml"
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
