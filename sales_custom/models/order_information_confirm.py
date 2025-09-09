from odoo import models, fields, api, _

class OrderInformationConfirm(models.TransientModel):
    _name = 'sales_custom.order_information.confirm'
    _description = 'Order Information Confirm'

    order_id = fields.Many2one('sales_custom.order_information', string="Order Information", required=True)

    def action_confirm(self):
        self.order_id.sudo().write({'revision_confirmed': True})
        return {'type': 'ir.actions.act_window_close'}
