from odoo import models, fields, api

class OrderKerjaDetail(models.Model):
    _name = 'order.kerja.detail'
    _description = 'Detail Pekerjaan Order Kerja'

    order_kerja_id = fields.Many2one('order.kerja', string='Order Kerja', ondelete='cascade')

    revisi = fields.Integer(string='Rev.')
    jenis_pekerjaan = fields.Char(string='Jenis Pekerjaan')
    uraian_pekerjaan = fields.Char(string='Uraian Pekerjaan')
    kel_biaya = fields.Char(string='Kel. Biaya')
    cost_c = fields.Char(string='Cost.C')
    no_internal_pok = fields.Many2one('pok.form',string='POK')

    pok_with_cost = fields.Char(
        string='POK + Cost',
        compute='_compute_pok_with_cost',
        store=True, invisible=True
    )

    qty = fields.Integer(string='Qty')
    satuan = fields.Char(string='Satuan')
    harga_satuan = fields.Float(string='Harga Satuan')
    jumlah_total = fields.Float(string='Jumlah', compute='_compute_jumlah', store=True)

    @api.depends('qty', 'harga_satuan')
    def _compute_jumlah(self):
        for rec in self:
            rec.jumlah_total = rec.qty * rec.harga_satuan
    
    @api.depends('no_internal_pok.number_form', 'cost_c')
    def _compute_pok_with_cost(self):
        for rec in self:
            if rec.no_internal_pok and rec.cost_c:
                original = rec.no_internal_pok.number_form or ""
                parts = original.split('/')
                if len(parts) >= 5:
                    rec.pok_with_cost = f"{parts[0]}/{rec.cost_c}/POK/{parts[-2]}/{parts[-1]}"
                else:
                    rec.pok_with_cost = original
            else:
                rec.pok_with_cost = ""
