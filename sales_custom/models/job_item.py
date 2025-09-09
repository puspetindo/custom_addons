from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class JobItem(models.Model):
    _name = 'sales_custom.job_item'
    _description = 'Job Item'
    _rec_name = 'combo'

    order_id = fields.Many2one('sales_custom.order_information', string="Order Information")
    order_form_type = fields.Selection(related='order_id.form_type', store=False, readonly=True)

    type = fields.Selection([
        ('PV', 'PV'),
        ('HE', 'HE'),
        ('TK', 'TK'),
        ('ST', 'ST')
    ], string="Type", required=True)
    
    combo = fields.Char(string="Combo", compute="_compute_combo", store=True)
    name = fields.Char(string="Name", required=True)
    item_no = fields.Char(string="Job Item No.", compute="_compute_item_no", store=True)
    number = fields.Char(string="Number", required=True)
    qty = fields.Integer(string="Quantity", required=True)
    weight_ton = fields.Float(string="Weight (ton)", required=True)
    diameter = fields.Char(string="Diameter", required=True)
    thk = fields.Char(string="Thickness", required=True)
    length = fields.Char(string="Length", required=True)
    material = fields.Char(string="Material", required=True)
    sequence = fields.Integer(string="No", compute="_compute_sequence")

    @api.depends('order_id', 'order_id.item_purchased', 'order_id.job_order_no')
    def _compute_item_no(self):
        for rec in self:
            if rec.order_id:
                items = rec.order_id.item_purchased
                idx = 0
                for i, item in enumerate(items, start=1):
                    if item == rec:
                        idx = i
                        break
                base = rec.order_id.job_order_no or ''
                if base and idx > 0:
                    rec.item_no = f"{base[:-2]}{idx:02d}"
                else:
                    rec.item_no = ''
            else:
                rec.item_no = ''

    @api.depends('order_id', 'order_id.item_purchased')
    def _compute_sequence(self):
        for rec in self:
            if rec.order_id:
                items = rec.order_id.item_purchased
                idx = 0
                for i, item in enumerate(items, start=1):
                    if item == rec:
                        idx = i
                        break
                rec.sequence = idx
            else:
                rec.sequence = 0
    
    @api.depends('item_no', 'name')
    def _compute_combo(self):
        for record in self:
            if record.item_no and record.name:
                record.combo = f"{record.item_no} - {record.name}"
            else:
                record.combo = record.item_no or record.name or ''

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
        res = super(JobItem, self).unlink()
        for order in orders:
            if order.exists():
                order._recompute_sequence()
        return res
