from odoo import api, fields, models

class PaymentDetail(models.Model):
    _name = 'payment.detail'
    _description = 'Perincian Pembayaran'
    _rec_name = 'name'

    # --- Header Fields ---
    name = fields.Char(
        string='Nomor',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Dibayarkan Kepada',
        required=True,
        domain="[('supplier_rank', '>', 0)]"
    )
    amount_paid = fields.Monetary(string='Jumlah Dibayarkan', compute='_compute_amount_paid', readonly=True, store=True)
    amount_paid_terbilang = fields.Char(
    string="Jumlah Dibayarkan (Terbilang)",
    compute="_compute_amount_paid_terbilang",
    store=True
    )

    source_document_ref = fields.Char(string='No. PO/DK/SPK/Surat/Memo')
    journal_entry_ref = fields.Char(string='Job. No. JE/JS')
    recipient_bank_id = fields.Many2one('res.partner.bank', string='Recipient Bank')
    today_date = fields.Date(string='Tanggal Hari Ini', default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    # --- Line Items ---
    line_ids = fields.One2many(
        'payment.detail.line',
        'payment_detail_id',
        string='Rincian Biaya'
    )

    # --- Total & Notes ---
    amount_total_net = fields.Monetary(
        string='Jumlah Bersih',
        compute='_compute_amount_total_net',
        store=True
    )
    notes = fields.Text(string='Keterangan')

    # --- Supporting Documents Checklist ---
    is_memo_attached = fields.Boolean(string="Memo / Surat / Disposisi")
    memo_ref = fields.Char(string="Ref. Memo")
    memo_file = fields.Binary(string="File Memo")
    memo_filename = fields.Char(string="Nama File Memo")
    
    is_invoice_attached = fields.Boolean(string="Kwitansi / Invoice / Nota")
    invoice_ref = fields.Char(string="Ref. Kwitansi")
    invoice_file = fields.Binary(string="File Kwitansi")
    invoice_filename = fields.Char(string="Nama File Kwitansi")
    
    is_tax_invoice_attached = fields.Boolean(string="Faktur Pajak")
    tax_invoice_ref = fields.Char(string="Ref. Faktur Pajak")
    tax_invoice_file = fields.Binary(string="File Faktur Pajak")
    tax_invoice_filename = fields.Char(string="Nama File Faktur Pajak")
    
    is_po_attached = fields.Boolean(string="PO / OK / SPK")
    po_ref = fields.Char(string="Ref. PO")
    po_file = fields.Binary(string="File PO")
    po_filename = fields.Char(string="Nama File PO")
    
    is_late_fee_doc_attached = fields.Boolean(string="Denda Keterlambatan")
    late_fee_doc_file = fields.Binary(string="File Denda Keterlambatan")
    late_fee_doc_filename = fields.Char(string="Nama File Denda Keterlambatan")
    
    is_lpb_attached = fields.Boolean(string="LPB")
    lpb_ref = fields.Char(string="Ref. LPB")
    lpb_file = fields.Binary(string="File LPB")
    lpb_filename = fields.Char(string="Nama File LPB")
    
    is_ba_attached = fields.Boolean(string="Berita Acara")
    ba_file = fields.Binary(string="File Berita Acara")
    ba_filename = fields.Char(string="Nama File Berita Acara")
    
    is_delivery_note_attached = fields.Boolean(string="Surat Jalan /...")
    delivery_note_file = fields.Binary(string="File Surat Jalan")
    delivery_note_filename = fields.Char(string="Nama File Surat Jalan")
    
    is_other_doc_attached = fields.Boolean(string="Lain - lain")
    other_doc_file = fields.Binary(string="File Lain-lain")
    other_doc_filename = fields.Char(string="Nama File Lain-lain")

    # --- Template Trigger ---
    use_template_lines = fields.Boolean(string='Template Rincian Biaya', default=True)

    # --- Footer & Signatures ---
    document_date = fields.Date(
        string='Tanggal Dokumen',
        default=fields.Date.context_today,
        required=True
    )
    verifier_user_id = fields.Many2one('res.users', string='Dibuat oleh (Verifikator)', default=lambda self: self.env.user)
    tax_checker_user_id = fields.Many2one('res.users', string='Diperiksa oleh (Pajak)')
    accounting_approver_user_id = fields.Many2one('res.users', string='Diketahui oleh (Akuntansi)')

    # --- Digital Signatures ---
    verifier_signature = fields.Binary(string='Tanda Tangan Verifikator')
    tax_checker_signature = fields.Binary(string='Tanda Tangan Pajak')
    accounting_approver_signature = fields.Binary(string='Tanda Tangan Akuntansi')

    @api.depends('line_ids.amount')
    def _compute_amount_total_net(self):
        for record in self:
            record.amount_total_net = sum(record.line_ids.mapped('amount'))

    @api.depends('amount_total_net')
    def _compute_amount_paid(self):
        for record in self:
            record.amount_paid = record.amount_total_net

    @api.depends('amount_paid')
    def _compute_amount_paid_terbilang(self):
        for record in self:
            if record.amount_paid:
                # Convert amount to integer (remove decimals)
                amount_int = int(record.amount_paid)
                # Convert to terbilang
                terbilang = self._angka_ke_terbilang(amount_int)
                record.amount_paid_terbilang = terbilang
            else:
                record.amount_paid_terbilang = ''

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('payment.detail.sequence') or 'New'
        records = super().create(vals_list)
        
        # Add template lines if use_template_lines is True
        for record in records:
            if record.use_template_lines:
                record._add_template_lines()
        
        return records

    @api.onchange('use_template_lines')
    def _onchange_use_template_lines(self):
        """Automatically add/remove template lines when checkbox is toggled"""
        if self.use_template_lines:
            # Add template lines if checkbox is checked
            if not self.line_ids:
                self._add_template_lines()
        else:
            # Remove template lines if checkbox is unchecked
            self._remove_template_lines()

    def _remove_template_lines(self):
        """Remove template lines from the current payment detail"""
        template_names = [
            'Nilai / Uang Muka',
            'Biaya Pengiriman',
            'PPN',
            'PPh Psl 23 / Final',
            'Denda Keterlambatan',
            'Lain - lain',
            'UM',
            'Materai'
        ]
        
        # Find and remove lines that match template names
        lines_to_remove = self.line_ids.filtered(lambda l: l.name in template_names and l.amount == 0.0)
        if lines_to_remove:
            self.write({
                'line_ids': [(2, line.id) for line in lines_to_remove]
            })

    def _add_template_lines(self):
        """Add template lines to the current payment detail"""
        template_lines = self.env['payment.detail.line'].search([('is_template', '=', True)])
        
        for template in template_lines:
            # Check if this template line already exists in current record
            existing_line = self.line_ids.filtered(lambda l: l.name == template.name)
            if not existing_line:
                self.write({
                    'line_ids': [(0, 0, {
                        'name': template.name,
                        'amount': 0.0,
                        'tax_id': template.tax_id.id if template.tax_id else False,
                    })]
                })
        
        return True

 # --- Angka ke Terbilang ---
    def _angka_ke_terbilang(self, angka):
        satuan = ['', 'satu', 'dua', 'tiga', 'empat', 'lima',
                  'enam', 'tujuh', 'delapan', 'sembilan']
        belasan = ['sepuluh', 'sebelas', 'dua belas', 'tiga belas',
                   'empat belas', 'lima belas', 'enam belas',
                   'tujuh belas', 'delapan belas', 'sembilan belas']
        puluhan = ['', '', 'dua puluh', 'tiga puluh', 'empat puluh',
                   'lima puluh', 'enam puluh', 'tujuh puluh',
                   'delapan puluh', 'sembilan puluh']

        def convert(n):
            if n < 10:
                return satuan[n]
            elif n < 20:
                return belasan[n-10]
            elif n < 100:
                return puluhan[n//10] + (' ' + satuan[n % 10] if n % 10 != 0 else '')
            elif n < 200:
                return 'seratus ' + convert(n-100)
            elif n < 1000:
                return satuan[n//100] + ' ratus ' + convert(n % 100)
            elif n < 2000:
                return 'seribu ' + convert(n-1000)
            elif n < 1000000:
                return convert(n//1000) + ' ribu ' + convert(n % 1000)
            elif n < 1000000000:
                return convert(n//1000000) + ' juta ' + convert(n % 1000000)
            elif n < 1000000000000:
                return convert(n//1000000000) + ' milyar ' + convert(n % 1000000000)
            elif n < 1000000000000000:
                return convert(n//1000000000000) + ' trilyun ' + convert(n % 1000000000000)
            else:
                return ''

        return convert(angka).strip()
    

class PaymentDetailLine(models.Model):
    _name = 'payment.detail.line'
    _description = 'Rincian Baris Pembayaran'
    wbs = fields.Char(string='WBS')
    rbs = fields.Char(string='RBS')

    payment_detail_id = fields.Many2one('payment.detail', string='Perincian Pembayaran ID', ondelete='cascade')
    name = fields.Char(string='Keterangan', required=True)
    amount = fields.Monetary(string='Jumlah', required=True)
    currency_id = fields.Many2one(related='payment_detail_id.currency_id')
    tax_id = fields.Many2one('account.tax', string='Tax')
    is_template = fields.Boolean(string='Template Baris', default=False)

