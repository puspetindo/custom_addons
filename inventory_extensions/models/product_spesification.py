from odoo import models, fields, api
from odoo.tools import lazy_property

class ProductSpesification(models.Model):
    _name = "product.spesification"
    _description = "model spesifikasi untuk produk"
    _rec_name = 'name'
    
    name = fields.Char(string="Nama Spesifikasi")
    kode_ktg = fields.Char(string="Kode Kategori")
    kategori = fields.Char(string="Kategori")