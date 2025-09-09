from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
import locale
from datetime import date  
import logging


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
    
    item_purchased_js = fields.One2many(
        'sales_custom.job_item_js', 'order_id', string="Items"
    )
    
    status = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed')
    ], string="Status", default='open')
    bast_number = fields.Char(string="Nomor BAST")
    close_date = fields.Date(string="Tanggal Close")

    # New computed fields for export
    package_equipment = fields.Char(string="Package/Equipment", compute="_compute_package_equipment")
    equipment_type = fields.Char(string="Type", compute="_compute_equipment_type")
    equipment_qty = fields.Float(string="Qty", compute="_compute_equipment_qty")
    equipment_material = fields.Char(string="Material", compute="_compute_equipment_material")
    equipment_weight = fields.Float(string="Weight (Ton)", compute="_compute_equipment_weight")
    equipment_diameter = fields.Char(string="Diameter", compute="_compute_equipment_diameter")
    equipment_thk = fields.Char(string="Thk", compute="_compute_equipment_thk")
    equipment_length = fields.Char(string="Length", compute="_compute_equipment_length")
    stamp_str = fields.Char(string="Stamp", compute="_compute_stamp")
    value_usd_comp = fields.Float(string="Value USD", compute="_compute_value_usd")
    value_idr_comp = fields.Float(string="Value IDR", compute="_compute_value_idr")
    sertifikasi_str = fields.Char(string="Sertifikasi", compute="_compute_sertifikasi")
    remark_str = fields.Char(string="Remark", compute="_compute_remark")
    status_str = fields.Char(string="Status", compute="_compute_status")

    @api.constrains('status', 'bast_number', 'close_date')
    def _check_close_requirements(self):
        for rec in self:
            if rec.status == 'closed':
                if not rec.bast_number or not rec.close_date:
                    raise ValidationError(_("Nomor BAST dan Tanggal Close harus diisi sebelum menutup proyek."))

    @api.depends('item_purchased')
    def _compute_package_equipment(self):
        for record in self:
            record.package_equipment = ', '.join(record.item_purchased.mapped('name'))

    @api.depends('item_purchased')
    def _compute_equipment_type(self):
        for record in self:
            types = record.item_purchased.mapped('type')
            record.equipment_type = ', '.join(types) if types else ''

    @api.depends('item_purchased')
    def _compute_equipment_qty(self):
        for record in self:
            record.equipment_qty = sum(record.item_purchased.mapped('qty'))

    @api.depends('item_purchased')
    def _compute_equipment_material(self):
        for record in self:
            materials = record.item_purchased.mapped('material')
            record.equipment_material = ', '.join(materials) if materials else ''

    @api.depends('item_purchased')
    def _compute_equipment_weight(self):
        for record in self:
            record.equipment_weight = sum(record.item_purchased.mapped('weight_ton'))

    @api.depends('item_purchased')
    def _compute_equipment_diameter(self):
        for record in self:
            diameters = record.item_purchased.mapped('diameter')
            record.equipment_diameter = ', '.join(diameters) if diameters else ''

    @api.depends('item_purchased')
    def _compute_equipment_thk(self):
        for record in self:
            thks = record.item_purchased.mapped('thk')
            record.equipment_thk = ', '.join(thks) if thks else ''

    @api.depends('item_purchased')
    def _compute_equipment_length(self):
        for record in self:
            lengths = record.item_purchased.mapped('length')
            record.equipment_length = ', '.join(lengths) if lengths else ''

    @api.depends('stamp')
    def _compute_stamp(self):
        for record in self:
            if isinstance(record.stamp, bool):
                record.stamp_str = 'Yes' if record.stamp else 'No'
            else:
                record.stamp_str = record.stamp or ''

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
                # Jika ingin nama bulan Indonesia, pastikan locale sudah tersedia di server
                try:
                    locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
                    record.remark_str = record.date_4.strftime('%B')
                except:
                    # fallback ke bahasa Inggris jika locale tidak ada
                    record.remark_str = record.date_4.strftime('%B')
            else:
                record.remark_str = ''

    @api.depends('status_str')
    def _compute_status(self):
        for record in self:
            record.status_str = record.status_str or ''

    item_purchased_js = fields.One2many(
        'sales_custom.job_item_js', 'order_id', string="Items JS"
    )

    scope_division_ids = fields.One2many(
        'sales_custom.scope_division', 'order_id', string='Scope of Work & Supply'
    )

    total_qty = fields.Float(string="Total Quantity", compute="_compute_total_qty", store=True)
    total_weight = fields.Float(string="Total Weight", compute="_compute_total_weight", store=True)

    special_note = fields.Text(string="Special Note")

    loiloa = fields.Boolean(string="LOI/LOA")
    purchase_order = fields.Boolean(string="Purchase Order")
    change_order = fields.Boolean(string="Change Order")
    applicable_documents_list = fields.Boolean(string="Applicable Documents List")
    time_schedule = fields.Boolean(string="Time Schedule")
    scope_of_work_supply = fields.Boolean(string="Scope of Work & Supply")
    ceb = fields.Boolean(string="CEB")
    clarification_record_of_contract = fields.Boolean(string="Clarification Record of Contract")
    other_mom_list_of_equipment = fields.Boolean(string="Other MOM List of Equipment")

    tanda_tangan = fields.Binary(string="Signature", required=True)
    by = fields.Many2one('hr.employee', string="By", required=True)
    title = fields.Text(string="Title", required=True)

    revision_confirmed = fields.Boolean(string="Revision Confirmed", default=False)

    def action_revise(self):
        return {
            'name': _('Confirm Revision'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sales_custom.order_information.confirm',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }
    
    def test_increment_revision(self):
        self.ensure_one()
        self.increment_revision()
        return True

    @api.depends('item_purchased.qty')
    def _compute_total_qty(self):
        total_qty = 0.0
        for line in self.item_purchased:
            total_qty += line.qty
        self.total_qty = total_qty

    @api.depends('item_purchased.weight_ton')
    def _compute_total_weight(self):
        total_weight = 0.0
        for line in self.item_purchased:
            total_weight += line.weight_ton
        self.total_weight = total_weight

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        if 'job_order_no' in fields_list:
            form_type = res.get('form_type', 'JE')
            year_suffix = str(date.today().year)[-2:]  # last two digits of current year
            prefix = f"{form_type}-{year_suffix}"
            domain = [('job_order_no', 'like', f'{prefix}%')]
            existing_orders = self.search(domain)
            max_project_seq = 0
            seen_sequences = set()
            for order in existing_orders:
                job_no = order.job_order_no
                if job_no and len(job_no) >= 10 and job_no.endswith("00"):
                    try:
                        project_seq = int(job_no[5:8])
                        if project_seq not in seen_sequences:
                            seen_sequences.add(project_seq)
                            if project_seq > max_project_seq:
                                max_project_seq = project_seq
                    except ValueError:
                        continue
            new_project_seq = max_project_seq + 1
            res['job_order_no'] = f"{prefix}{new_project_seq:03d}00"

        return res

    def _recompute_sequence(self):
        base = self.job_order_no or ''
        for idx, item in enumerate(self.item_purchased.sorted('id'), start=1):
            item.sequence = idx
            item.item_no = f"{base[:-2]}{idx:02d}"

    @api.model
    def action_confirm_revision(self):
        return {
            'name': _('Confirm Revision'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sales_custom.order_information.confirm',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }
    
    def increment_revision(self):
        self.ensure_one()
        # Update fields directly without triggering write to avoid recursion
        super(OrderInformation, self).write({
            'revision': self.revision + 1,
            'revision_date': fields.Date.today(),
            'revision_confirmed': False,
        })

    def _check_item_usage_before_deletion(self, item_ids):
        """Cek apakah item yang akan dihapus sudah digunakan di modul lain"""
        if not item_ids:
            return True, ""
            
        items = self.env['sales_custom.job_item'].browse(item_ids)
        used_items = []
        
        for item in items:
            is_used, message = item._check_usage_in_other_modules()
            if is_used:
                used_items.append(f"{item.name} ({message})")
        
        if used_items:
            return False, ", ".join(used_items)
        return True, ""

    def write(self, vals):
        for record in self:
            # Check if revision_confirmed was True before write
            revision_confirmed_before = record.revision_confirmed
            
            # Validasi penghapusan item saat revisi
            if 'item_purchased' in vals:
                for command in vals['item_purchased']:
                    if command and len(command) == 3 and command[0] == 2:  # DELETE command
                        item_id = command[1]
                        can_delete, message = record._check_item_usage_before_deletion([item_id])
                        if not can_delete:
                            raise UserError(_(f"Tidak dapat menghapus item karena sudah digunakan di: {message}"))
            
            # Allow closing operation without any revision confirmation
            is_closing_operation = 'status' in vals and vals['status'] == 'closed'
            
            # If it's a closing operation, skip all revision checks
            if is_closing_operation:
                # Skip revision confirmation check for closing operations
                pass
            elif (record.id and not revision_confirmed_before and vals and len(vals) > 0 and 
                not ('revision_confirmed' in vals and vals['revision_confirmed'] == True)):
                raise UserError(_("You must confirm revision before saving changes. Please click 'Confirm Revision' button."))
        
        res = super(OrderInformation, self).write(vals)

        for record in self:
            # If revision_confirmed was True before write, increment revision and reset flag
            if revision_confirmed_before:
                # Increment revision inline to avoid recursion
                super(OrderInformation, record).write({
                    'revision': record.revision + 1,
                    'revision_date': fields.Date.today(),
                    'revision_confirmed': False,
                })

        return res

    @api.depends('job_order_no', 'project')
    def _compute_combo(self):
        for record in self:
            if self.job_order_no and self.project:
                record.combo = f"{self.job_order_no} - {self.project}"
            else:
                record.combo = self.job_order_no or self.project or ''

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._recompute_sequence()
        if not record.scope_division_ids:
            scope_remarks = self.env['sales_custom.scope_remarks'].search([])
            lines = []
            for remark in scope_remarks:
                lines.append((0, 0, {
                    'remarks': remark.id,
                    'detail_scope': '',
                    'division': '',
                }))
            record.write({'scope_division_ids': lines})
        return record

    @api.onchange('scope_division_ids')
    def _onchange_scope_division_ids(self):
        for record in self:
            scope_remarks = self.env['sales_custom.scope_remarks'].search([])
            existing_remarks = self.scope_division_ids.mapped('remarks')
            missing_remarks = scope_remarks - existing_remarks
            lines_to_add = []
            for remark in missing_remarks:
                lines_to_add.append((0, 0, {
                    'remarks': remark.id,
                    'detail_scope': '',
                    'division': '',
                }))
            if lines_to_add:
                record.write({'scope_division_ids': lines_to_add})

    @api.onchange('item_purchased')
    def _onchange_item_purchased(self):
        for order in self:
            for item in self.item_purchased:
                item._compute_item_no()
                item._compute_sequence()

    def sync_scope_division_lines(self):
        for record in self:
            scope_remarks = self.env['sales_custom.scope_remarks'].search([])
            existing_remarks = self.scope_division_ids.mapped('remarks')
            missing_remarks = scope_remarks - existing_remarks
            lines_to_add = []
            for remark in missing_remarks:
                lines_to_add.append((0, 0, {
                    'remarks': remark.id,
                    'detail_scope': '',
                    'division': '',
                }))
            if lines_to_add:
                record.write({'scope_division_ids': lines_to_add})
                
    def name_get(self):
        result = []
        for record in self:
            name = self.combo or 'No Job Order No'
            result.append((self.id, name))
        return result

    @api.depends('combo')
    def _compute_display_name(self):
        for record in self:
            self.display_name = self.combo or 'No Job Order No'

    def print_order_information_report(self):
        return self.env.ref('sales_custom.action_report_order_information').report_action(self)

    def _check_usage_in_other_modules(self):
        """Cek apakah order information ini digunakan di modul lain"""
        self.ensure_one()
        
        try:
            # Cek di WMR Form
            if 'wmr.form' in self.env:
                wmr_forms = self.env['wmr.form'].search([('job_number_id', '=', self.id)])
                if wmr_forms:
                    return True, f"Order Information ini digunakan di WMR Form: {', '.join(wmr_forms.mapped('name'))}"
            
            # Cek di Form Material Requisition
            if 'form.material.requisition' in self.env:
                form_mr = self.env['form.material.requisition'].search([('job_number_id', '=', self.id)])
                if form_mr:
                    return True, f"Order Information ini digunakan di Form Material Requisition: {', '.join(form_mr.mapped('name'))}"
            
            # Cek di procurement models
            if 'procurement.form_mr' in self.env:
                form_mr = self.env['procurement.form_mr'].search([('job_number_id', '=', self.id)])
                if form_mr:
                    return True, f"Order Information ini digunakan di Form Material Requisition: {', '.join(form_mr.mapped('name'))}"
            
            # Cek di Form Purchase Order
            if 'form.purchase.order' in self.env:
                form_pp = self.env['form.purchase.order'].search([('pusat_biaya', '=', self.id)])
                if form_pp:
                    return True, f"Order Information ini digunakan di Form Purchase Order: {', '.join(form_pp.mapped('name'))}"
            
            # Cek di List Purchase Order
            if 'list.purchase.order' in self.env:
                list_pp = self.env['list.purchase.order'].search([('pusat_biaya', '=', self.id)])
                if list_pp:
                    return True, f"Order Information ini digunakan di List Purchase Order: {', '.join(list_pp.mapped('name'))}"
                    
            # Cek di procurement models lainnya
            if 'procurement.list_pp' in self.env:
                list_pp = self.env['procurement.list_pp'].search([('pusat_biaya', '=', self.id)])
                if list_pp:
                    return True, f"Order Information ini digunakan di List Purchase Order: {', '.join(list_pp.mapped('name'))}"
                    
        except Exception as e:
            # Log error untuk debugging
            pass
            
        return False, ""

    def unlink(self):
        """Override unlink untuk mencegah penghapusan jika sudah digunakan"""
        for record in self:
            is_used, message = record._check_usage_in_other_modules()
            if is_used:
                raise UserError(_(f"Tidak dapat menghapus Order Information ini. {message}"))
        
        return super(OrderInformation, self).unlink()
    
    def action_close(self):
        self.ensure_one()
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info(f"Closing order {self.id} with current status: {self.status}")
        self.write({
            'status': 'closed',
            'close_date': fields.Date.today()
        })
        # Show success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Proyek berhasil di-close'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_close(self):
        return {
            'name': _('Close Project'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sales_custom.order_information.close',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_bast_number': self.bast_number or '',
                'default_close_date': self.close_date or False,
            },
        }
        
    @api.constrains('status', 'bast_number', 'close_date')
    def _check_close_requirements(self):
        for rec in self:
            if rec.status == 'closed':
                if not rec.bast_number or not rec.close_date:
                    raise ValidationError(_("Nomor BAST dan Tanggal Close harus diisi sebelum menutup proyek."))