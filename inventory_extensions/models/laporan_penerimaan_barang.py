from odoo import models, fields, api
from datetime import datetime

class LaporanPenerimaanBarang(models.Model):
    _name = 'laporan.penerimaan.barang'
    _description = 'Laporan Penerimaan Barang'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    _order = 'tanggal_lpb desc'
    _rec_name = 'no_lpb'

    no_lpb = fields.Char(string='No. LPB', required=True, readonly=True, default='New', copy=False)
    tanggal_lpb = fields.Date(string='Tanggal LPB', default=fields.Date.context_today, required=True)
    rev_lpb = fields.Integer(string='Revisi', default=0, readonly=True)
    tanggal_kedatangan = fields.Date(string='Tanggal Kedatangan Barang', required=True)
    dibeli_dari = fields.Many2one('res.partner', string='Dibeli dari', required=True)
    no_po = fields.Char(string='No. PO', required=True)
    no_sj = fields.Char(string='Reff. No.', required=True)
    status_pengiriman = fields.Selection([
        ('diterima', 'Diterima'),
        ('sebagian', 'Diterima Sebagian'),
        ('belum', 'Belum Diterima'),
    ], string='Status Pengiriman', default='diterima')

    alamat_pengirim = fields.Char(string='Alamat Pengirim', related='dibeli_dari.contact_address')
    line_ids = fields.One2many('laporan.penerimaan.barang.line', 'laporan_id', string='Detail Barang')
    ttd_wh = fields.Binary(string='Warehouse Officer', widget='signature')
    ttd_prc = fields.Binary(string='Manager Procurement', widget='signature')

    @api.model
    def create(self, vals):
        if vals.get('no_lpb', 'New') == 'New':
            tahun = datetime.today().strftime('%y') 
            seq = self.env['ir.sequence'].next_by_code('laporan.penerimaan.barang') or '000'
            vals['no_lpb'] = f"{seq}-LPB/{tahun}"
        return super().create(vals)
