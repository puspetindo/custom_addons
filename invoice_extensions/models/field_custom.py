from odoo import fields, models, api, _

class FieldCustom(models.Model):
    _inherit = 'account.move'

    #Field Custom
    no_po = fields.Char(string='No.PO')
    date_po = fields.Date(string='Tanggal PO')

    date_ship = fields.Date(string='Date of Shipment')
    ship_by = fields.Char(string='Shipped By')
    ship_from = fields.Char(string='Shipped From')
    ship_to = fields.Char(string='Ship Destination')
    