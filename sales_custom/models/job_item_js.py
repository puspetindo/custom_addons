from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class JobItemJS(models.Model):
    _name = 'sales_custom.job_item_js'
    _description = 'Job Item JS'

    order_id = fields.Many2one('sales_custom.oi_js', string="Order Information")

    item_no = fields.Char(string="Job Item No.", compute="_compute_item_no", store=True)
    name = fields.Char(string="Name", required=True)
    # number = fields.Char(string="Number", required=True)
    qty = fields.Integer(string="Quantity", required=True)
    weight_ton = fields.Float(string="Weight (ton)", required=True)
    material = fields.Char(string="Material", required=True)
    sequence = fields.Integer(string="No", compute="_compute_sequence")

    @api.depends('order_id', 'order_id.item_purchased_js', 'order_id.job_order_no')
    def _compute_item_no(self):
        for rec in self:
            if rec.order_id:
                items = rec.order_id.item_purchased_js
                idx = 0
                for i, item in enumerate(items, start=1):
                    if item == rec:
                        idx = i
                        break
                base = rec.order_id.job_order_no or ''
                if base and idx > 0:
                    # Remove last two digits from base and append idx as two digits
                    rec.item_no = f"{base[:-2]}{idx:02d}"
                else:
                    rec.item_no = ''
            else:
                rec.item_no = ''

    @api.depends('order_id', 'order_id.item_purchased_js')
    def _compute_sequence(self):
        for rec in self:
            if rec.order_id:
                items = rec.order_id.item_purchased_js
                idx = 0
                for i, item in enumerate(items, start=1):
                    if item == rec:
                        idx = i
                        break
                rec.sequence = idx
            else:
                rec.sequence = 0

    @api.constrains('qty', 'weight_ton')
    def _check_qty_weight_not_zero(self):
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError("Quantity tidak boleh 0 atau negatif.")
            if rec.weight_ton <= 0:
                raise ValidationError("Weight tidak boleh 0 atau negatif.")

    def unlink(self):
        """Override unlink untuk recompute sequence setelah penghapusan"""
        orders = self.mapped('order_id')
        res = super().unlink()
        for order in orders:
            order._recompute_sequence()
        return res
