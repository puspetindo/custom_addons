from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

class Oi_Js(models.Model):
    _name = 'sales_custom.oi_js'
    _description = 'Order Information JS'
    _rec_name = 'display_name'

    form_type = fields.Selection([
        ('JE', 'Job Equipment'),
        ('JS', 'Job Service')
    ], string="Form Type", required=True, default='JS')
    
    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True)

    job_order_no = fields.Char(string="Job Order No.", readonly=True)
    combo = fields.Char(string="Combo", compute="_compute_combo", store=True)
    distribution_to = fields.Text(string="Distribution To", required=True)
    revision = fields.Integer(string="Revision", readonly=True, default=0)
    revision_date = fields.Date(string="Revision Date", readonly=True)
    date = fields.Date(string="Date", required=True)

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

    # item_purchased = fields.One2many(
    #     'sales_custom.job_item', 'order_id', string="Items"
    # )

    item_purchased_js = fields.One2many(
        'sales_custom.job_item_js', 'order_id', string="Items JS"
    )

    scope_division_ids = fields.One2many(
        'sales_custom.scope_division', 'order_id_js', string='Scope of Work & Supply'
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

    stamp = fields.Boolean(string="Stamp")
    sertifikasi = fields.Selection([
        ('DISNAKEER', 'DISNAKEER'),
        ('MIGAS', 'MIGAS')
    ], string="Sertifikasi")
    delivery_input = fields.Date(string="Delivery Input")
    value_usd = fields.Float(string="Value USD")
    value_idr = fields.Float(string="Value IDR")
    
    tanda_tangan = fields.Binary(string="Signature", required=True)
    by = fields.Many2one('hr.employee', string="By", required=True)
    title = fields.Text(string="Title", required=True)
    
    bast_number = fields.Char(string="Nomor BAST")
    close_date = fields.Date(string="Tanggal Close")
    status = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
    ], string="Status", default='open')

    revision_confirmed = fields.Boolean(string="Revision Confirmed", default=False)

    @api.depends('item_purchased_js.qty')
    def _compute_total_qty(self):
        total_qty = 0.0
        for line in self.item_purchased_js:
            total_qty += line.qty
        self.total_qty = total_qty

    @api.depends('item_purchased_js.weight_ton')
    def _compute_total_weight(self):
        total_weight = 0.0
        for line in self.item_purchased_js:
            total_weight += line.weight_ton
        self.total_weight = total_weight

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        if 'job_order_no' in fields_list:
            form_type = res.get('form_type', 'JS')
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
        for idx, item in enumerate(self.item_purchased_js.sorted('id'), start=1):
            item.sequence = idx
            item.item_no = f"{base[:-2]}{idx:02d}"

    @api.model
    def action_confirm_revision(self):
        return {
            'name': _('Confirm Revision'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sales_custom.oi_js.confirm',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def increment_revision(self):
        self.ensure_one()
        # Update fields directly without triggering write to avoid recursion
        super(Oi_Js, self).write({
            'revision': self.revision + 1,
            'revision_date': fields.Date.today(),
            'revision_confirmed': False,
        })

    def _check_item_usage_before_deletion(self, item_ids):
        """Cek apakah item JS yang akan dihapus sudah digunakan di modul lain"""
        if not item_ids:
            return True, ""
            
        items = self.env['sales_custom.job_item_js'].browse(item_ids)
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
            revision_confirmed_before = record.revision_confirmed
            
            # Validasi penghapusan item JS saat revisi
            if 'item_purchased_js' in vals:
                for command in vals['item_purchased_js']:
                    if command and len(command) == 3 and command[0] == 2:  # DELETE command
                        item_id = command[1]
                        can_delete, message = record._check_item_usage_before_deletion([item_id])
                        if not can_delete:
                            raise UserError(_(f"Tidak dapat menghapus item karena sudah digunakan di: {message}"))
            
            if record.id and not revision_confirmed_before and vals and not ('revision_confirmed' in vals and vals['revision_confirmed'] == True):
                raise UserError(_("You must confirm revision before saving changes. Please click 'Confirm Revision' button."))

        res = super(Oi_Js, self).write(vals)

        for record in self:
            # If revision_confirmed was True before write, increment revision and reset flag
            if revision_confirmed_before:
                # Increment revision inline to avoid recursion
                super(Oi_Js, record).write({
                    'revision': record.revision + 1,
                    'revision_date': fields.Date.today(),
                    'revision_confirmed': False,
                })

        return res
    @api.depends('job_order_no', 'project')
    def _compute_combo(self):
        if self.job_order_no and self.project:
            self.combo = f"{self.job_order_no} - {self.project}"
        else:
            self.combo = self.job_order_no or self.project or ''

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
        scope_remarks = self.env['sales_custom.scope_remarks'].search([])
        existing_remarks = self.scope_division_ids.mapped('remarks')
        missing_remarks = scope_remarks - existing_remarks
        lines_to_add = []
        for remark in missing_remarks:
            lines_to_add.append((0, 0, {
                'remarks': remark.id,
                'detail_scope': '',
                'division': '',
                'order_id_js': self.id,
            }))
        if lines_to_add:
            self.write({'scope_division_ids': lines_to_add})

    @api.onchange('item_purchased_js')
    def _onchange_item_purchased_js(self):
        for item in self.item_purchased_js:
            item._compute_item_no()
            item._compute_sequence()

    def sync_scope_division_lines(self):
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
            self.write({'scope_division_ids': lines_to_add})
                
    def name_get(self):
        result = []
        name = self.combo or 'No Job Order No'
        result.append((self.id, name))
        return result

    @api.depends('combo')
    def _compute_display_name(self):
        self.display_name = self.combo or 'No Job Order No'

    def print_oi_js_report(self):
        return self.env.ref('sales_custom.action_report_oi_js').report_action(self)

    def action_revise(self):
        return {
            'name': _('Confirm Revision'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sales_custom.oi_js.confirm',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def _check_usage_in_other_modules(self):
        """Cek apakah order information JS ini digunakan di modul lain"""
        self.ensure_one()
        
        try:
            # Cek di WMR Form
            if 'wmr.form' in self.env:
                wmr_forms = self.env['wmr.form'].search([('job_number_id', '=', self.id)])
                if wmr_forms:
                    return True, f"WMR Form: {', '.join(wmr_forms.mapped('name'))}"
            
            # Cek di Form Material Requisition
            if 'form.material.requisition' in self.env:
                form_mr = self.env['form.material.requisition'].search([('job_number_id', '=', self.id)])
                if form_mr:
                    return True, f"Form Material Requisition: {', '.join(form_mr.mapped('name'))}"
            
            # Cek di procurement models
            if 'procurement.form_mr' in self.env:
                form_mr = self.env['procurement.form_mr'].search([('job_number_id', '=', self.id)])
                if form_mr:
                    return True, f"Form Material Requisition: {', '.join(form_mr.mapped('name'))}"
            
            # Cek di Form Purchase Order
            if 'form.purchase.order' in self.env:
                form_pp = self.env['form.purchase.order'].search([('pusat_biaya', '=', self.id)])
                if form_pp:
                    return True, f"Form Purchase Order: {', '.join(form_pp.mapped('name'))}"
            
            # Cek di List Purchase Order
            if 'list.purchase.order' in self.env:
                list_pp = self.env['list.purchase.order'].search([('pusat_biaya', '=', self.id)])
                if list_pp:
                    return True, f"List Purchase Order: {', '.join(list_pp.mapped('name'))}"
                    
            # Cek di procurement models lainnya
            if 'procurement.list_pp' in self.env:
                list_pp = self.env['procurement.list_pp'].search([('pusat_biaya', '=', self.id)])
                if list_pp:
                    return True, f"List Purchase Order: {', '.join(list_pp.mapped('name'))}"
                    
            # Cek di Delivery Note
            if 'delivery.note' in self.env:
                delivery_notes = self.env['delivery.note'].search([('job_number_id', '=', self.id)])
                if delivery_notes:
                    return True, f"Delivery Note: {', '.join(delivery_notes.mapped('name'))}"
                    
            # Cek di Invoice
            if 'account.move' in self.env:
                invoices = self.env['account.move'].search([('job_number_id', '=', self.id)])
                if invoices:
                    return True, f"Invoice: {', '.join(invoices.mapped('name'))}"
                    
        except Exception as e:
            pass
            
        return False, ""

    def unlink(self):
        """Override unlink untuk mencegah penghapusan jika sudah digunakan"""
        for record in self:
            is_used, message = record._check_usage_in_other_modules()
            if is_used:
                raise UserError(_(f"Tidak dapat menghapus Order Information JS ini karena sudah digunakan di: {message}"))
        
        return super(Oi_Js, self).unlink()
    
    def action_close_project(self):
        return {
            'name': _('Close Project JS'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            # 'views': [(self.env.ref('sales_custom.view_order_information_js_close_form').id, 'form')],
            'res_model': 'sales_custom.order_information_js.close',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }
    
# class OrderInformationJSClose(models.TransientModel):
#     _name = 'sales_custom.order_information_js.close'
#     _description = 'Order Information JS Close'

#     order_id = fields.Many2one('sales_custom.oi_js', string="Order Information JS", required=True)
#     bast_number = fields.Char(string="Nomor BAST")
#     close_date = fields.Date(string="Tanggal Close")

#     def action_confirm_close(self):
#         self.ensure_one()
#         if not self.bast_number or not self.bast_number.strip() or not self.close_date:
#             raise ValidationError(_("Nomor BAST dan Tanggal Close harus diisi dengan benar untuk menutup proyek."))
#         self.order_id.write({
#             'bast_number': self.bast_number.strip(),
#             'close_date': self.close_date,
#             'status': 'closed',
#             'revision_confirmed': 'True'
#         })
#         return {
#             'type': 'ir.actions.act_window_close',
#             'infos': {
#                 'type': 'ir.actions.client',
#                 'tag': 'display_notification',
#                 'params': {
#                     'title': _('Sukses'),
#                     'message': _('Proyek Sukses di Close'),
#                     'type': 'success',
#                     'sticky': False,
#                 }
#             }
#         }

#     def action_cancel_close(self):
#         return {'type': 'ir.actions.act_window_close'}