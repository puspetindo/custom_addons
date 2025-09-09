from odoo import models, fields, api

class ProductDimension(models.Model):
    _name = 'product.dimension'
    _description = u'Dimensi Produk'
    _rec_name = 'ukuran_dimensi'
    
    ukuran_dimensi = fields.Char(string='Ukuran Dimensi', required=False)
    specification_id = fields.Many2one('product.spesification', string='Spesifikasi', required=False)
    kategori_name = fields.Char(string='Nama Kategori', store=True)