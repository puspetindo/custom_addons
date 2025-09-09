from odoo import fields, api, models
from odoo.exceptions import ValidationError
from datetime import datetime

ROMAN_MONTHS = {
    1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI',
    7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 11: 'XI', 12: 'XII'
}

class PermintaanOrderKerja(models.Model):
    _name = 'pok.form'
    _description = 'Form Permintaan Order Kerja'
    _rec_name = 'number_form'

    number_form = fields.Char(string='No.', required=True, copy=False, readonly=True, default=lambda self: self._get_default_number())
    tanggal_input = fields.Date(string='Tanggal', required=True, default=fields.Date.today)
    ref_pok = fields.Char(string='Ref POK / OK No.')
    revision_count = fields.Integer(string='Revisi', default=0, copy=False, readonly=True)

    from_dept = fields.Many2one('sales_custom.scope_remarks', string="Dari Dept.", required=True)
    to_dept = fields.Many2one('sales_custom.scope_remarks', string="Kepada Dept.", readonly=True)
    tipe_pusat_biaya = fields.Selection(
        [('je', 'JE (Order Information)'),
        ('dept', 'Departemen/Divisi')],
        string='Tipe Pusat Biaya', required=True
    )
    pusat_biaya_je = fields.Many2one('sales_custom.order_information', string='Pusat Biaya (JE)')
    pusat_biaya_dept = fields.Many2one('sales_custom.scope_remarks', string='Pusat Biaya (Dept/Divisi)')
    kode_dept = fields.Char(string='Kode Departemen', readonly=True, compute='_compute_kode_dept')

    list_pok = fields.One2many('list.pok', 'pok_form_id', string='')

    disposisi = fields.Text(string="Disposisi kepada (diisi oleh procurement) :")

    # Peminta order Dibuat
    nama_dibuat = fields.Char(string='Dibuat Oleh')
    tanggal_dibuat = fields.Date(string='Tanggal Dibuat')
    ttd_dibuat = fields.Binary(string='Tanda Tangan', widget='signature', help="Masukkan Tanda Tangan")

    # Peminta order Diperiksa
    nama_diperiksa = fields.Char(string='Diperiksa Oleh')
    tanggal_diperiksa = fields.Date(string='Tanggal Diperiksa')
    ttd_diperiksa = fields.Binary(string='Tanda Tangan', widget='signature', help="Masukkan Tanda Tangan")

    # Peminta order Disetujui
    nama_disetujui = fields.Char(string='Disetujui Oleh')
    tanggal_disetujui = fields.Date(string='Tanggal Disetujui')
    ttd_disetujui = fields.Binary(string='Tanda Tangan', widget='signature', help="Masukkan Tanda Tangan")

    # Procurement Diterima
    nama_penerima = fields.Char(string='Diterima Oleh')
    tanggal_diterima = fields.Date(string='Tanggal Diterima')
    ttd_diterima = fields.Binary(string='Tanda Tangan', widget='signature', help="Masukkan Tanda Tangan")

    # Procurement Disetujui
    nama_disetujui_2 = fields.Char(string='Disetujui Oleh')
    tanggal_disetujui_2 = fields.Date(string='Tanggal Disetujui')
    ttd_disetujui_2 = fields.Binary(string='Tanda Tangan', widget='signature', help="Masukkan Tanda Tangan")

    # Procurement Diselesaikan
    nama_diselesaikan = fields.Char(string='Diselesaikan Oleh')
    tanggal_diselesaikan = fields.Date(string='Tanggal Diselesaikan')
    ttd_diselesaikan = fields.Binary(string='Tanda Tangan', widget='signature', help="Masukkan Tanda Tangan")

    # Peminta Order Diterima
    nama_penerima_1 = fields.Char(string='Diterima Oleh')
    tanggal_diterima_1 = fields.Date(string='Tanggal Diterima')
    ttd_diterima_1 = fields.Binary(string='Tanda Tangan', widget='signature', help="Masukkan Tanda Tangan")

    @api.depends('pusat_biaya_dept')
    def _compute_kode_dept(self):
        for record in self:
            record.kode_dept = record.pusat_biaya_dept.nomor if record.pusat_biaya_dept else False

    @api.onchange('tipe_pusat_biaya')
    def _onchange_tipe_pusat_biaya(self):
        """
        Clear the cost center fields when the type changes to avoid data inconsistency.
        """
        if self.tipe_pusat_biaya == 'je':
            self.pusat_biaya_dept = False
        elif self.tipe_pusat_biaya == 'dept':
            self.pusat_biaya_je = False
        else:
            self.pusat_biaya_je = False
            self.pusat_biaya_dept = False

    def _get_default_number(self, tanggal_input=None, from_dept=None):
        try:
            tanggal = tanggal_input or fields.Date.context_today(self)
            bulan_romawi = ROMAN_MONTHS.get(tanggal.month, '??')
            tahun = tanggal.year

            count = self.search_count([
                ('tanggal_input', '>=', f'{tahun}-01-01'),
                ('tanggal_input', '<=', f'{tahun}-12-31')
            ])
            seq_number = str(count + 1).zfill(3)

            nomor_divisi = '0000'
            if from_dept and hasattr(from_dept, 'nomor'):
                nomor_divisi = str(from_dept.nomor or '0000').zfill(4)

            return f"{seq_number}/POK-E/{nomor_divisi}/{bulan_romawi}/{tahun}"
        except:
            return "001/POK-E/0000/??/????"

    @api.onchange('tanggal_input', 'from_dept')
    def _onchange_generate_number_form(self):
        if self.tanggal_input and self.from_dept:
            self.number_form = self._get_default_number(self.tanggal_input, self.from_dept)
        elif self.tanggal_input:
            self.number_form = self._get_default_number(self.tanggal_input, None)
        elif self.from_dept:
            today = fields.Date.context_today(self)
            self.number_form = self._get_default_number(today, self.from_dept)

        # Fix to_dept ke "Procurement"
        procurement_dept = self.env['sales_custom.scope_remarks'].search([('name', 'ilike', 'Procurement')], limit=1)
        if procurement_dept:
            self.to_dept = procurement_dept

    def write(self, vals):
        """
        Override the write method to increment the revision count on any change.
        """
        # To avoid an infinite loop, we don't increment the revision if
        # the 'revision_count' field is the only one being updated.
        if 'revision_count' in vals and len(vals) == 1:
            return super(PermintaanOrderKerja, self).write(vals)

        # For batch updates, we must iterate to update each record's revision individually.
        for record in self:
            # We create a new dict for vals to avoid modifying it in the loop for other records.
            new_vals = vals.copy()
            new_vals['revision_count'] = record.revision_count + 1
            super(PermintaanOrderKerja, record).write(new_vals)
        return True

    def print_pok_report(self):
        return self.env.ref('wmr.action_report_pok_form').report_action(self)

    @api.model
    def create(self, vals):
        tanggal = vals.get('tanggal_input')
        from_dept_id = vals.get('from_dept')

        if not tanggal:
            raise ValidationError("Tanggal Input harus diisi.")
        if not from_dept_id:
            raise ValidationError("Dari Dept. harus diisi.")

        from_dept = self.env['sales_custom.scope_remarks'].browse(from_dept_id)
        tanggal_dt = fields.Date.from_string(tanggal)

        # Set number_form final
        vals['number_form'] = self._get_default_number(tanggal_dt, from_dept)

        # Fix to_dept ke "Procurement"
        procurement_dept = self.env['sales_custom.scope_remarks'].search([('name', 'ilike', 'Procurement')], limit=1)
        if procurement_dept:
            vals['to_dept'] = procurement_dept.id

        return super(PermintaanOrderKerja, self).create(vals)
