{
    "name": "Invoice Extensions",
    "version": "1.0",
    "author": "Rizky Febrian",
    "summary": "Custom fields for invoice extensions",
    "category": "Accounting",
    "depends": ["account"],
    "data": [
        "views/account_move_views.xml",
        "report/invoice_custom_report.xml",
        "report/invoice_report_actions.xml"
    ],
    "assets": {
        "web.report_assets_common": [
            "invoice_extensions/static/img/logo_puspetindo.png",
        ],
    },
    "installable": True,
    "application": False
}
