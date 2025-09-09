from odoo import models, fields, api   
from datetime import datetime 

class OrderKerja(models.Model):
    _name = 'order.kerja'
    _description = 'Form Order Kerja'
    _rec_name = 'nomor_ok'

    # Header
    nomor_ok = fields.Char(string='No. OK', readonly=True, default='-', copy=False)
    _sql_constraints = [
    ('nomor_ok_unique', 'unique(nomor_ok)', 'Nomor OK harus unik!')
]
    tanggal_ok = fields.Date(string='Tanggal', default=fields.Date.today, readonly=True)
    revisi = fields.Integer(string='Revisi', default=0, readonly=True)

    # Referensi Kami
    referensi_nomor = fields.Many2one('pok.form',string='Nomor')
    referensi_tanggal = fields.Date(string='Tanggal')

    # Penawaran Saudara
    penawaran_nomor = fields.Char(string='Nomor')
    penawaran_tanggal = fields.Date(string='Tanggal')
    referensi_ok_no = fields.Many2one('order.kerja',string='Ref. OK No.', domain="[('id', '!=', id)]")

    # Syarat-Syarat Utama
    syarat_pembayaran = fields.Char(string='Syarat Pembayaran')
    lokasi_penyerahan = fields.Char(string='Lokasi Penyerahan')
    syarat_penyerahan = fields.Char(string='Syarat Penyerahan')
    tanggal_batas_penyerahan = fields.Date(string='Tanggal Batas Penyerahan')

    # Kepada
    kepada_nama = fields.Many2one('res.partner', string='Kepada')
    kepada_alamat = fields.Text(string='Alamat', compute='_compute_kepada_fields', store=True)
    kepada_kontak = fields.Char(string='Telp', compute='_compute_kepada_fields', store=True)
    kepada_email = fields.Char(string='Email', compute='_compute_kepada_fields', store=True)
    # Detail Pekerjaan
    detail_ids = fields.One2many('order.kerja.detail', 'order_kerja_id', string='Detail Pekerjaan')

    # Total
    sub_total = fields.Float(string='Sub-Total', compute='_compute_subtotal', store=True)
    sub_total_terbilang = fields.Char(
        string='Subtotal (Terbilang)',
        compute='_compute_terbilang',
    )

        # Tanda Tangan dan Catatan
    sign = fields.Binary(string='Tanda Tangan')
    ttd_nama = fields.Char(string='Ditandatangani Oleh', compute='_compute_ttd_nama', store=True)
    ttd_jabatan = fields.Char(string='Jabatan', compute='_compute_ttd_nama', store=True)

    note = fields.Text(string='Catatan', default="""1.Harga tersebut netto franco PT PUSPETINDO
2.Harga tersebut belum termasuk PPN 11%
3.Harga tersebut sudah termasuk sertifikat dari KEMNAKER RI
4.Harga tersebut termasuk training kit
5.Pembayaran dilakukan 100% setelah pelatihan, setelah invoice diterima dengan benar.
6.Pembayaran dilakukan via transfer Bank sesuai yang tertera di tagihan/ invoice""")

    @api.depends('kepada_nama')
    def _compute_kepada_fields(self):
        for rec in self:
            partner = rec.kepada_nama
            rec.kepada_alamat = partner.contact_address or ''
            rec.kepada_kontak = partner.phone or ''
            rec.kepada_email = partner.email or ''
    
    @api.model
    def create(self, vals):
        if vals.get('nomor_ok', '-') == '-':
            tahun = datetime.now().year
            last = self.search([
                ('nomor_ok', 'ilike', f'% - SCO - {tahun}')
            ], order="id desc", limit=1)
            
            if last and last.nomor_ok:
                try:
                    last_seq = int(last.nomor_ok.split(' - ')[0])
                except ValueError:
                    last_seq = 0
            else:
                last_seq = 0

            next_seq = str(last_seq + 1).zfill(3)
            vals['nomor_ok'] = f"{next_seq} - SCO - {tahun}"
        return super(OrderKerja, self).create(vals)

    @api.depends('detail_ids.jumlah_total')
    def _compute_subtotal(self):
        for rec in self:
            rec.sub_total = sum(line.jumlah_total for line in rec.detail_ids)

    @api.depends('sub_total')
    def _compute_terbilang(self):
        for record in self:
            record.sub_total_terbilang = self._angka_ke_terbilang(record.sub_total)

    def _angka_ke_terbilang(self, angka):
        """Konversi angka ke dalam bentuk terbilang (Bahasa Indonesia)"""
        satuan = ['', 'satu', 'dua', 'tiga', 'empat', 'lima', 
                 'enam', 'tujuh', 'delapan', 'sembilan']
        belasan = ['sepuluh', 'sebelas', 'dua belas', 'tiga belas', 
                  'empat belas', 'lima belas', 'enam belas', 
                  'tujuh belas', 'delapan belas', 'sembilan belas']
        puluhan = ['', '', 'dua puluh', 'tiga puluh', 'empat puluh', 
                  'lima puluh', 'enam puluh', 'tujuh puluh', 
                  'delapan puluh', 'sembilan puluh']
        
        def convert_less_than_million(n):
            if n < 10:
                return satuan[n]
            elif 10 <= n < 20:
                return belasan[n-10]
            elif 20 <= n < 100:
                return puluhan[n//10] + (' ' + satuan[n%10] if n%10 !=0 else '')
            elif 100 <= n < 1000:
                if n//100 == 1:
                    return 'seratus ' + convert_less_than_million(n%100)
                else:
                    return satuan[n//100] + ' ratus ' + convert_less_than_million(n%100)
            elif 1000 <= n < 1000000:
                if n//1000 == 1:
                    return 'seribu ' + convert_less_than_million(n%1000)
                else:
                    return convert_less_than_million(n//1000) + ' ribu ' + convert_less_than_million(n%1000)
            else:
                return ''
        
        if angka == 0:
            return 'nol Rupiah'
        
        # Pisahkan bagian desimal (jika ada)
        bilangan_bulat = int(angka)
        bilangan_desimal = round((angka - bilangan_bulat) * 100)
        
        terbilang = ''
        
        # Konversi bagian bulat
        if bilangan_bulat < 0:
            terbilang = 'minus '
            bilangan_bulat = abs(bilangan_bulat)
        
        if bilangan_bulat == 0:
            terbilang += 'nol'
        else:
            bagian = []
            milyar = bilangan_bulat // 1000000000
            if milyar > 0:
                bagian.append(convert_less_than_million(milyar) + ' milyar')
                bilangan_bulat %= 1000000000
            
            juta = bilangan_bulat // 1000000
            if juta > 0:
                bagian.append(convert_less_than_million(juta) + ' juta')
                bilangan_bulat %= 1000000
            
            ribu = bilangan_bulat // 1000
            if ribu > 0:
                bagian.append(convert_less_than_million(ribu) + ' ribu')
                bilangan_bulat %= 1000
            
            if bilangan_bulat > 0:
                bagian.append(convert_less_than_million(bilangan_bulat))
            
            terbilang += ' '.join(bagian)
        
        # Konversi bagian desimal
        if bilangan_desimal > 0:
            terbilang += ' koma ' + convert_less_than_million(bilangan_desimal)
        
        # Tambahkan mata uang
        terbilang += ' Rupiah'
        
        # Kapitalisasi huruf pertama
        return terbilang.capitalize()
    
    @api.depends('sub_total')
    def _compute_ttd_nama(self):
        for rec in self:
            if rec.sub_total <= 20_000_000: 
                rec.ttd_nama = 'Aneng Wicaksono'
                rec.ttd_jabatan = 'Direktur Operasional'
            elif 20_000_000 < rec.sub_total <= 150_000_000:  
                rec.ttd_nama = 'Budi Astoro'
                rec.ttd_jabatan = 'Direktur Keuangan'
            else:  
                rec.ttd_nama = 'Jonni Kurniawan Siregar'
                rec.ttd_jabatan = 'Direktur Utama'

    def write(self, vals):
        if not self.env.context.get('skip_revision_increment'):
            vals['revisi'] = self.revisi + 1
        return super(OrderKerja, self).write(vals)

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'nomor_ok': '-',
            'revisi': self.revisi + 1,
        })
        return super(OrderKerja, self).copy(default)

