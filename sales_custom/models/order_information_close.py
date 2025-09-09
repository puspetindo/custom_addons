from odoo import models, fields, api, _
from odoo.exceptions import UserError

class OrderInformationClose(models.TransientModel):
    _name = 'sales_custom.order_information.close'
    _description = 'Order Information Close'

    order_id = fields.Many2one('sales_custom.order_information', string="Order Information", required=True)
    bast_number = fields.Char(string="Nomor BAST")
    close_date = fields.Date(string="Tanggal Close")

    def action_confirm_close(self):
        self.ensure_one()
        if not self.bast_number or not self.bast_number.strip() or not self.close_date:
            raise UserError(_("Nomor BAST dan Tanggal Close harus diisi dengan benar untuk menutup proyek."))
        self.order_id.write({
            'bast_number': self.bast_number.strip(),
            'close_date': self.close_date,
            'status': 'closed'
        })
        return {
            'type': 'ir.actions.act_window_close',
            'infos': {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sukses'),
                    'message': _('Proyek Sukses di Close'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        }

    def action_cancel_close(self):
        return {'type': 'ir.actions.act_window_close'}