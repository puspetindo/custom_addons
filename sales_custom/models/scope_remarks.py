from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class ScopeRemarks(models.Model):
    _name = 'sales_custom.scope_remarks'
    _description = 'Master Scope Description'

    name = fields.Char(string='Division Name')
    nomor = fields.Integer(string='Number', help='Unique number for the division')
    active = fields.Boolean(string='Active', default=True)

    def unlink(self):
        for record in self:
            if self.env['sales_custom.scope_division'].search([('remarks', '=', record.id)]):
                raise UserError("Cannot delete this remark because it is referenced by Scope Division records. Please archive it instead.")
        return super(ScopeRemarks, self).unlink()

    def action_archive(self):
        self.active = False
