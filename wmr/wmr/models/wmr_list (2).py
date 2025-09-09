from odoo import models, fields, api
from odoo.exceptions import RedirectWarning

class ListWeldingMaterialRequisition(models.Model):
    _name = 'wmr.wmr_list'
    _description = 'Welding Material Requisition Line'

    wmr_list_id = fields.Many2one('wmr.wmr_form', string="Form WMR", ondelete="cascade")
    nama_barang = fields.Many2one('product.template', string='Nama Barang', required=True)

    specification_domain = fields.Char(string='Domain Spesifikasi', store=False)
    dimensi_domain = fields.Char(string='Domain Dimensi', store=False)

    specification = fields.Many2one(
        'product.spesification',
        string='Spesifikasi',
        required=True,
        domain="[('kategori', '=', specification_domain)]"
    )
    dimension_id = fields.Many2one(
        'product.dimension',
        string='Dimensi',
        required=True,
        domain="[('kategori_name', '=', specification_domain), ('specification_id', '=', dimensi_domain)]"
    )

    quantity = fields.Integer(string='Quantity', required=True, default=1)
    weight = fields.Float(string='Weight')
    additional_requirement = fields.Char(string='Additional Requirement')
    stock_availability = fields.Integer(string='Stock Availability')
    remarks = fields.Char(string='Remarks')

    # 1. Saat nama barang dipilih, isi domain spesifikasi
    @api.onchange('nama_barang')
    def _onchange_nama_barang(self):
        self.specification = False
        self.dimension_id = False
        if self.nama_barang:
            self.specification_domain = self.nama_barang.name
            return {
                'domain': {
                    'specification': [('kategori', '=', self.specification_domain)]
                }
            }
        else:
            self.specification_domain = False
            return {
                'domain': {
                    'specification': [],
                    'dimension_id': []
                }
            }

    # 2. Saat spesifikasi dipilih, isi dimensi_domain
    @api.onchange('specification')
    def _onchange_specification(self):
        self.dimension_id = False
        self.dimensi_domain = self.specification.name if self.specification else False
        return self._get_dimension_domain()

    # 3. Domain dinamis untuk dimension_id
    def _get_dimension_domain(self):
        domain = []
        if self.specification_domain:
            domain.append(('kategori_name', '=', self.specification_domain))
        if self.dimensi_domain:
            domain.append(('specification_id.name', '=', self.dimensi_domain))
        return {
            'domain': {
                'dimension_id': domain
            }
        }

    # 4. Cek duplikasi kombinasi spesifikasi + dimensi
    @api.constrains('specification', 'dimension_id')
    def _check_duplicate_product(self):
        for record in self:
            if record.specification and record.dimension_id:
                domain = [
                    ('specification', '=', record.specification.id),
                    ('dimension_id', '=', record.dimension_id.id),
                    ('id', '!=', record.id),
                ]
                duplicate = self.search(domain)
                if duplicate:
                    first = duplicate[0]
                    action = {
                        'type': 'ir.actions.act_window',
                        'res_model': self._name,
                        'res_id': first.id,
                        'view_mode': 'form',
                        'target': 'current',
                        'name': 'Duplikasi Terdeteksi',
                    }

                    pesan = "Data duplikat ditemukan:\n"
                    for d in duplicate:
                        pesan += f"- {d.nama_barang.name if d.nama_barang else '-'} | Spesifikasi: {d.specification.name} | Dimensi: {d.dimension_id.ukuran_dimensi}\n"

                    raise RedirectWarning(pesan, action, "Lihat Data Duplikat")