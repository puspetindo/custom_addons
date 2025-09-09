from odoo import models, fields, api

class ProductSatuan(models.Model):
    _name = 'product.satuan'
    _description = u'Satuan Produk'
    _rec_name = 'nama_satuan'

    nama_satuan = fields.Char(string='Nama Satuan', required=False)
