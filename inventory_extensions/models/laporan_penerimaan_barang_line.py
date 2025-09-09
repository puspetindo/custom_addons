from odoo import models, fields, api

class LaporanPenerimaanBarangLine(models.Model):
    _name = 'laporan.penerimaan.barang.line'
    _description = 'Detail Barang di LPB'

    laporan_id = fields.Many2one('laporan.penerimaan.barang', string='LPB', ondelete='cascade')
    rev_line = fields.Integer(string='Revisi', default=0, readonly=True)
    product_id = fields.Many2one('product.template', string='Nama Barang', required=True)
    kode_barang = fields.Char(string='Kode Barang', related='product_id.default_code', readonly=True)
    job_dept = fields.Char(string='Job/Dept')
    spesification_id = fields.Many2one('product.spesification', string='Spesifikasi Produk')
    satuan_custom_id = fields.Many2one('product.satuan', string='Satuan Custom')
    dimension_id = fields.Many2one('product.dimension', string='Dimensi Produk')
    jumlah = fields.Float(string='Jumlah', required=True)
    satuan = fields.Many2one('uom.uom', string='Satuan', related='product_id.uom_id', readonly=True)
    job_dept = fields.Char(string='Job/Dept')
    keterangan = fields.Text(string='Keterangan')
    stock_unit = fields.Float(string='Stock Unit')  # Bisa otomatis dari quant