from odoo import api, fields, models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_template = fields.Boolean(string='Template Baris', default=False)

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    # --- State remains standard ---
    
    # --- Payment Detail Fields ---
    amount_residual_terbilang = fields.Char(
        string="Jumlah Dibayarkan (Terbilang)",
        compute="_compute_amount_residual_terbilang",
        store=True
    )
    
    source_document_ref = fields.Char(string='No. PO/DK/SPK/Surat/Memo')
    journal_entry_ref = fields.Char(string='Job. No. JE/JS')
    recipient_bank_id = fields.Many2one('res.partner.bank', string='Recipient Bank')
    today_date = fields.Date(string='Tanggal Hari Ini', default=fields.Date.context_today)

    # --- Template Trigger ---
    use_template_lines = fields.Boolean(string='Template Rincian Biaya', default=True)

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
    
    # --- Footer & Signatures ---
    verifier_user_id = fields.Many2one('res.users', string='Dibuat oleh (Verifikator)', default=lambda self: self.env.user)
    tax_checker_user_id = fields.Many2one('res.users', string='Diperiksa oleh (Pajak)')
    accounting_approver_user_id = fields.Many2one('res.users', string='Diketahui oleh (Akuntansi)')
    
    # --- Digital Signatures ---
    verifier_signature = fields.Binary(string='Tanda Tangan Verifikator')
    tax_checker_signature = fields.Binary(string='Tanda Tangan Pajak')
    accounting_approver_signature = fields.Binary(string='Tanda Tangan Akuntansi')
    
    # --- Computed Fields ---
    @api.depends('amount_residual')
    def _compute_amount_residual_terbilang(self):
        for record in self:
            if record.amount_residual:
                # Convert amount to integer (remove decimals)
                amount_int = int(record.amount_residual)
                # Convert to terbilang
                terbilang = self._angka_ke_terbilang(amount_int)
                record.amount_residual_terbilang = terbilang
            else:
                record.amount_residual_terbilang = ''
    
    # --- State transitions removed ---
    
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

        if angka == 0:
            return 'nol'

        def convert(n):
            if n < 0:
                return "minus " + convert(abs(n))
            if n < 10:
                return satuan[int(n)]
            elif n < 20:
                return belasan[int(n-10)]
            elif n < 100:
                return puluhan[int(n//10)] + (' ' + satuan[int(n % 10)] if n % 10 != 0 else '')
            elif n < 200:
                return 'seratus ' + convert(n-100)
            elif n < 1000:
                return satuan[int(n//100)] + ' ratus ' + convert(n % 100)
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
                return 'Angka terlalu besar'
        
        return convert(angka).strip()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.use_template_lines and record.move_type == 'in_invoice' and record.id:
                record._add_template_lines()
        return records

    @api.onchange('use_template_lines')
    def _onchange_use_template_lines(self):
        """Automatically add/remove template lines when checkbox is toggled"""
        if not self.id:
            return
        if self.use_template_lines:
            # Add template lines if checkbox is checked and no lines exist
            if not self.invoice_line_ids:
                self._add_template_lines()
        else:
            # Remove template lines if checkbox is unchecked
            self._remove_template_lines()

    def _remove_template_lines(self):
        """Remove template lines from the current invoice"""
        if not self.id:
            return

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

        # Find and remove lines that match template names and are templates with zero amount
        lines_to_remove = self.invoice_line_ids.filtered(lambda l: l.name in template_names and l.is_template and l.price_unit == 0.0)
        if lines_to_remove:
            self.write({
                'invoice_line_ids': [(2, line.id) for line in lines_to_remove]
            })

    def _add_template_lines(self):
        """Add template lines to the current invoice"""
        if not self.id:
            return

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

        for name in template_names:
            # Check if this template line already exists
            existing_line = self.invoice_line_ids.filtered(lambda l: l.name == name and l.is_template)
            if not existing_line:
                # Get a default account, e.g., first expense account
                default_account = self.env['account.account'].search([
                    ('account_type', 'in', ['expense', 'off_balance']),
                ], limit=1)
                self.write({
                    'invoice_line_ids': [(0, 0, {
                        'name': name,
                        'quantity': 1,
                        'price_unit': 0.0,
                        'is_template': True,
                        'account_id': default_account.id if default_account else False,
                        'currency_id': self.currency_id.id if self.currency_id else False,
                    })]
                })

        return True
