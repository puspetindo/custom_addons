from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
import locale
import logging

_logger = logging.getLogger(__name__)

class OrderInformation(models.Model):
    _name = 'sales_custom.order_information'
    _description = 'Order Information'
    _rec_name = 'display_name'

    form_type = fields.Selection([
        ('JE', 'Job Equipment'),
        ('JS', 'Job Service')
    ], string="Form Type", required=True, default='JE')
    
    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True)

    job_order_no = fields.Char(string="Job Order No.", readonly=True)
    combo = fields.Char(string="Combo", compute="_compute_combo", store=True)
    distribution_to = fields.Text(string="Distribution To", required=True)
    revision = fields.Integer(string="Revision", readonly=True, default=0)
    date = fields.Date(string="Date", required=True)
    revision_date = fields.Date(string="Revision Date", readonly=True)
    
    inquiry_no = fields.Char(string="Inquiry No.", required=True)
    date_1 = fields.Date(string="Date", required=True)
    quotation_no = fields.Char(string="Quotation No.", required=True)
    date_2 = fields.Date(string="Date", required=True)
    loiloa_no = fields.Char(string="LOI/LOA No.", required=True)
    date_3 = fields.Date(string="Date", required=True)
    pospk_no = fields.Char(string="PO/SPK No.", required=True)
    date_4 = fields.Date(string="Date", required=True)

    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    project = fields.Text(string="Project Title", required=True)

    stamp = fields.Boolean(string="Stamp")
    sertifikasi = fields.Selection([
        ('DISNAKEER', 'DISNAKEER'),
        ('MIGAS', 'MIGAS')
    ], string="Sertifikasi")
    delivery_input = fields.Date(string="Delivery Input")
    value_usd = fields.Float(string="Value USD")
    value_idr = fields.Float(string="Value IDR")

    item_purchased = fields.One2many(
        'sales_custom.job_item', 'order_id', string="Items"
    )

    # New computed fields for export
    package_equipment = fields.Char(string="Package/Equipment", compute="_compute_package_equipment", store=True)
    equipment_type = fields.Char(string="Type", compute="_compute_equipment_type", store=True)
    equipment_qty = fields.Float(string="Qty", compute="_compute_equipment_qty", store=True)
    equipment_material = fields.Char(string="Material", compute="_compute_equipment_material", store=True)
    equipment_weight = fields.Float(string="Weight (Ton)", compute="_compute_equipment_weight", store=True)
    equipment_diameter = fields.Char(string="Diameter", compute="_compute_equipment_diameter", store=True)
    equipment_thk = fields.Char(string="Thk", compute="_compute_equipment_thk", store=True)
    equipment_length = fields.Char(string="Length", compute="_compute_equipment_length", store=True)
    stamp_str = fields.Char(string="Stamp", compute="_compute_stamp", store=True)
    value_usd_comp = fields.Float(string="Value USD", compute="_compute_value_usd", store=True)
    value_idr_comp = fields.Float(string="Value IDR", compute="_compute_value_idr", store=True)
    sertifikasi_str = fields.Char(string="Sertifikasi", compute="_compute_sertifikasi", store=True)
    remark_str = fields.Char(string="Remark", compute="_compute_remark", store=True)
    status_str = fields.Char(string="Status", compute="_compute_status", store=True)

    @api.depends('item_purchased.name')
    def _compute_package_equipment(self):
        for record in self:
            record.package_equipment = ', '.join(record.item_purchased.mapped('name'))

    @api.depends('item_purchased.type')
    def _compute_equipment_type(self):
        for record in self:
            types = [t for t in record.item_purchased.mapped('type') if t]
            record.equipment_type = ', '.join(types) if types else ''

    @api.depends('item_purchased.qty')
    def _compute_equipment_qty(self):
        for record in self:
            record.equipment_qty = sum(record.item_purchased.mapped('qty'))

    @api.depends('item_purchased.material')
    def _compute_equipment_material(self):
        for record in self:
            materials = [m for m in record.item_purchased.mapped('material') if m]
            record.equipment_material = ', '.join(materials) if materials else ''

    @api.depends('item_purchased.weight_ton')
    def _compute_equipment_weight(self):
        for record in self:
            record.equipment_weight = sum(record.item_purchased.mapped('weight_ton'))

    @api.depends('item_purchased.diameter')
    def _compute_equipment_diameter(self):
        for record in self:
            diameters = [d for d in record.item_purchased.mapped('diameter') if d]
            record.equipment_diameter = ', '.join(diameters) if diameters else ''

    @api.depends('item_purchased.thk')
    def _compute_equipment_thk(self):
        for record in self:
            thks = [t for t in record.item_purchased.mapped('thk') if t]
            record.equipment_thk = ', '.join(thks) if thks else ''

    @api.depends('item_purchased.length')
    def _compute_equipment_length(self):
        for record in self:
            lengths = [l for l in record.item_purchased.mapped('length') if l]
            record.equipment_length = ', '.join(lengths) if lengths else ''

    @api.depends('stamp')
    def _compute_stamp(self):
        for record in self:
            record.stamp_str = 'Yes' if record.stamp else 'No'

    @api.depends('value_usd')
    def _compute_value_usd(self):
        for record in self:
            record.value_usd_comp = record.value_usd or 0.0

    @api.depends('value_idr')
    def _compute_value_idr(self):
        for record in self:
            record.value_idr_comp = record.value_idr or 0.0

    @api.depends('sertifikasi')
    def _compute_sertifikasi(self):
        for record in self:
            record.sertifikasi_str = record.sertifikasi or ''

    @api.depends('date_4')
    def _compute_remark(self):
        for record in self:
            if record.date_4:
                try:
                    locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
                    record.remark_str = record.date_4.strftime('%B')
                except locale.Error:
                    # Fallback to English if Indonesian locale not available
                    try:
                        locale.setlocale(locale.LC_TIME, '')
                        record.remark_str = record.date_4.strftime('%B')
                    except:
                        record.remark_str = ''
            else:
                record.remark_str = ''

    @api.depends('job_order_no', 'customer_id', 'project')
    def _compute_display_name(self):
        for record in self:
            if record.job_order_no:
                record.display_name = f"{record.job_order_no} - {record.customer_id.name or ''}"
            else:
                record.display_name = f"Draft - {record.customer_id.name or ''}"

    @api.depends('form_type', 'job_order_no')
    def _compute_combo(self):
        for record in self:
            record.combo = f"{record.form_type or ''}-{record.job_order_no or ''}"

    @api.depends('item_purchased')
    def _compute_status(self):
        for record in self:
            if record.item_purchased:
                record.status_str = 'Active'
            else:
                record.status_str = 'Draft'

    @api.model
    def create(self, vals):
        if vals.get('job_order_no', _('New')) == _('New'):
            seq_date = None
            if 'date' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.from_string(vals['date']))
            vals['job_order_no'] = self.env['ir.sequence'].next_by_code('sales_custom.order_information', sequence_date=seq_date) or _('New')
        return super(OrderInformation, self).create(vals)

    def write(self, vals):
        if 'revision' in vals and vals['revision'] > 0:
            vals['revision_date'] = date.today()
        return super(OrderInformation, self).write(vals)

    def action_confirm_revision(self):
        for record in self:
            record.revision += 1
            record.revision_date = date.today()
        return True

    def unlink(self):
        for record in self:
            if record.job_order_no:
                # Check if this order is used in other modules
                if record._check_usage_in_other_modules():
                    raise UserError(_('Cannot delete order that is being used in other modules.'))
        return super(OrderInformation, self).unlink()

    def _check_usage_in_other_modules(self):
        """Check if this order is used in other modules"""
        self.ensure_one()
        # Add checks for WMR, procurement, etc.
        return False  # Placeholder - implement actual checks

    def action_view_items(self):
        self.ensure_one()
        return {
            'name': _('Job Items'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'sales_custom.job_item',
            'domain': [('order_id', '=', self.id)],
            'context': {'default_order_id': self.id},
        }
