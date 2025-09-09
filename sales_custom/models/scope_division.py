from odoo import models, fields, api
from odoo.exceptions import UserError

class ScopeDivision(models.Model):
    _name = 'sales_custom.scope_division'
    _description = 'Scope Division'

    active = fields.Boolean(string='Active', default=True)

    remarks = fields.Many2one('sales_custom.scope_remarks', string="Description", required=True)
    detail_scope = fields.Text(string="Detail Scope of Work and Supply")
    division = fields.Char(string="Remarks")
    order_id = fields.Many2one('sales_custom.order_information', string="Order Information")
    order_id_js = fields.Many2one('sales_custom.oi_js', string="Order Information JS")

    def unlink(self):
        raise UserError("Deletion of Scope Division lines is not allowed. Please archive the record instead.")

    def action_archive(self):
        self.active = False

    def write(self, vals):
        if 'remarks' in vals or 'detail_scope' in vals:
            raise UserError("You cannot edit Description or Detail Scope of Work and Supply directly. Please use the Edit Detail button.")
        return super().write(vals)

    def open_detail_scope_wizard(self):
        self.ensure_one()
        return {
            'name': 'Edit Detail Scope',
            'type': 'ir.actions.act_window',
            'res_model': 'scope.division.detail.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_scope_division_id': self.id},
        }

class ScopeDivisionDetailWizard(models.TransientModel):
    _name = 'scope.division.detail.wizard'
    _description = 'Wizard to edit Detail Scope of Work and Supply'

    scope_division_id = fields.Many2one('sales_custom.scope_division', string="Scope Division", required=True)
    detail_scope = fields.Text(string="Detail Scope of Work and Supply", required=True)

    def action_save(self):
        if not self.detail_scope:
            raise UserError("Detail Scope of Work and Supply is mandatory.")
        self.scope_division_id.write({'detail_scope': self.detail_scope})
        return {'type': 'ir.actions.act_window_close'}
