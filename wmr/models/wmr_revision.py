from odoo import models, fields

class WmrRevision(models.Model):
    _name = 'wmr.wmr_revision'
    _description = 'WMR Revision'

    wmr_form_id = fields.Many2one('wmr.wmr_form', string='WMR Form')
    revision_no = fields.Integer(string='Revision No')
    date = fields.Date(string='Date')
    nama_dibuat = fields.Char(string='Prepared By')
    nama_diperiksa = fields.Char(string='Checked By')
    nama_disetujui = fields.Char(string='Approved By')
    inisial_dibuat = fields.Char(string='Inisial Dibuat')           # <--- Tambahkan ini
    inisial_diperiksa = fields.Char(string='Inisial Diperiksa')     # <--- Tambahkan ini
    inisial_disetujui = fields.Char(string='Inisial Disetujui')     # <--- Tambahkan ini
    ttd_dibuat = fields.Binary(string='Tanda Tangan Dibuat')
    ttd_diperiksa = fields.Binary(string='Tanda Tangan Diperiksa')     
    ttd_disetujui = fields.Binary(string='Tanda Tangan Disetujui')
