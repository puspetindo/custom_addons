from odoo import fields, models, api
import re

class FormWeldingMaterialRequisition(models.Model):
    _name = 'wmr.wmr_form'
    _description = 'Form Welding Material Requisition'
    _rec_name = 'document_number'

    document_number = fields.Char(string='Document Number', readonly=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    
    # Relasi ke order_information
    job_number_id = fields.Many2one('sales_custom.order_information', string='Job Number')
    
    # Menampilkan field dari relasi
    job_order_no = fields.Char(string='Job Order No.', related='job_number_id.job_order_no', store=True, readonly=True)
    job_item_no = fields.Many2one('sales_custom.job_item', string='Job Item No', required=True)
    job_item = fields.Char(string='Job Item', related='job_item_no.item_no', store=True, readonly=True)
    job_item_name = fields.Char(string='Job Item Name', related='job_item_no.name', store=True, readonly=True)
    customer = fields.Many2one('res.partner', string='Customer', related='job_number_id.customer_id', store=True, readonly=True)
    project = fields.Text(string='Project', related='job_number_id.project', store=True, readonly=True)

    item_purchased = fields.One2many('wmr.wmr_list', 'wmr_list_id', string='Items')

    note = fields.Text(string="Note :")

    revision_ids = fields.One2many('wmr.wmr_revision', 'wmr_form_id', string='Revision History')

    # Prepared By
    disiapkan = fields.Many2one('hr.employee', string='Prepared By', tracking=True)
    inisial_dibuat = fields.Char(string='Inisial', related='disiapkan.initials', readonly=True)
    ttd_dibuat = fields.Binary(string='Tanda Tangan', widget='signature')

    # Checked By
    diperiksa = fields.Many2one('hr.employee', string='Checked By', tracking=True)
    inisial_diperiksa = fields.Char(string='Inisial', related='diperiksa.initials', readonly=True)
    ttd_diperiksa = fields.Binary(string='Tanda Tangan', widget='signature')

    # Approved By
    disetujui = fields.Many2one('hr.employee', string='Approved By', tracking=True)
    inisial_disetujui = fields.Char(string='Inisial', related='disetujui.initials', readonly=True)
    ttd_disetujui = fields.Binary(string='Tanda Tangan', widget='signature')

    @api.onchange('job_number_id')
    def _onchange_job_number_id(self):
        if self.job_number_id and self.job_order_no:
            job_order_no = self.job_order_no
            number_part = re.sub(r'^JE-', '', job_order_no) if job_order_no.startswith('JE-') else job_order_no
            existing_docs = self.search([
                ('job_number_id', '=', self.job_number_id.id),
                ('id', '!=', self.id if self.id else False)
            ], order='id desc')
            max_seq = 0
            for doc in existing_docs:
                if doc.document_number:
                    parts = doc.document_number.split(' - QWMR - ')
                    if len(parts) == 2:
                        try:
                            seq_num = int(parts[1])
                            if seq_num > max_seq:
                                max_seq = seq_num
                        except ValueError: 
                            continue
            new_seq = max_seq + 1
            seq_str = str(new_seq).zfill(2)
            self.document_number = f"{number_part} - QWMR - {seq_str}"
        else:
            self.document_number = ''

            
    #Revision Count
    revision_count = fields.Integer(
        string='Revision',
        compute='_compute_revision_count',
        store=True
    )

    @api.depends('revision_ids')
    def _compute_revision_count(self):
        for rec in self:
            rec.revision_count = len(rec.revision_ids) - 1 if rec.revision_ids else 0

    @api.model
    def create(self, vals):
        # Cek apakah document_number sudah ada dari onchange
        if 'document_number' in vals and vals['document_number']:
            # Langsung buat record tanpa regenerate document_number
            record = super().create(vals)
        else:
            # Kalau document_number belum ada, generate seperti biasa
            record = super().create(vals)
            if record.job_number_id and record.job_order_no:
                job_order_no = record.job_order_no
                number_part = re.sub(r'^JE-', '', job_order_no) if job_order_no.startswith('JE-') else job_order_no
                # Cari record lain dengan job_number_id yang sama, kecuali record ini sendiri
                existing_docs = self.search([
                    ('job_number_id', '=', record.job_number_id.id),
                    ('id', '!=', record.id)
                ], order='id desc')
                max_seq = 0
                for doc in existing_docs:
                    if doc.document_number:
                        parts = doc.document_number.split(' - QWMR - ')
                        if len(parts) == 2:
                            try:
                                seq_num = int(parts[1])
                                if seq_num > max_seq:
                                    max_seq = seq_num
                            except ValueError:
                                continue
                new_seq = max_seq + 1
                seq_str = str(new_seq).zfill(2)
                record.document_number = f"{number_part} - QWMR - {seq_str}"
            else:
                record.document_number = False

                # Baris 0: revisi awal
        record.revision_ids.create({
            'wmr_form_id': record.id,
            'date': fields.Date.context_today(self),
            'nama_dibuat': record.disiapkan.name or '',
            'nama_diperiksa': record.diperiksa.name or '',
            'nama_disetujui': record.disetujui.name or '',
            'inisial_dibuat': record.disiapkan.initials or '',
            'inisial_diperiksa': record.diperiksa.initials or '',
            'inisial_disetujui': record.disetujui.initials or '',
            'ttd_dibuat': record.ttd_dibuat,
            'ttd_diperiksa': record.ttd_diperiksa,
            'ttd_disetujui': record.ttd_disetujui,
        })
        return record
    
    def write(self, vals):
        result = super().write(vals)
        for rec in self:
            # Hitung jumlah revisi, maksimal 6
            if len(rec.revision_ids) < 6:
                rec.revision_ids.create({
                    'wmr_form_id': rec.id,
                    'date': fields.Date.context_today(self),
                    'nama_dibuat': rec.disiapkan.name or '',
                    'nama_diperiksa': rec.diperiksa.name or '',
                    'nama_disetujui': rec.disetujui.name or '',
                    'inisial_dibuat': rec.disiapkan.initials or '',
                    'inisial_diperiksa': rec.diperiksa.initials or '',
                    'inisial_disetujui': rec.disetujui.initials or '',
                    'ttd_dibuat': rec.ttd_dibuat,
                    'ttd_diperiksa': rec.ttd_diperiksa,
                    'ttd_disetujui': rec.ttd_disetujui,
                })
        return result

    def print_wmr_report(self):
        # Gunakan referensi ke report action yang benar
        return self.env.ref('wmr.action_wmr_report').report_action(self)