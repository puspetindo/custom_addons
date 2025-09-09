from odoo import models, fields, api, _

class OiJsConfirm(models.TransientModel):
    _name = 'sales_custom.oi_js.confirm'
    _description = 'Order Information JS Confirm'

    order_id = fields.Many2one('sales_custom.oi_js', string="Order Information JS", required=True)

    def action_confirm(self):
        self.order_id.sudo().write({'revision_confirmed': True})
        return {'type': 'ir.actions.act_window_close'}
