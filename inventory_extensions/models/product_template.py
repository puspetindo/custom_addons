from odoo import models, fields, api
from odoo.exceptions import RedirectWarning

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    kode_barang = fields.Char(string="Kode Barang", store=True, unique=True, help="Kode unik untuk produk, digunakan untuk integrasi dengan sistem lain.") 
    kode_kategori = fields.Char(string="Kode Kategori", store=True, help="Kode unik untuk kategori produk, digunakan untuk integrasi dengan sistem lain.")
    jenis_barang = fields.Selection([
        ('consumable', 'Consumable'),
        ('material_requisition', 'Material Requisition'),
    ], string='Tipe Produk', required=True, default='consumable', help="Digunakan untuk keperluan pengelompokan internal.")

    spesifikasi_domain = fields.Char(string='Spesifikasi Domain', store=True)
    dimensi_domain = fields.Char(string='Dimensi Domain', store=True)

    specification_id = fields.Many2one(
        'product.spesification',
        string='Spesifikasi',
        help='Detail spesifikasi teknis produk',
        domain="[('kategori', '=', spesifikasi_domain)]",
        required=True
    )

    dimension_id = fields.Many2one(
        'product.dimension',
        string='Dimensi',
        help='Informasi dimensi produk',
        required=True,
        domain="[('kategori_name', '=', spesifikasi_domain),('specification_id', '=', dimensi_domain)]",
    )

    nama_satuan = fields.Many2one(
        'product.satuan',
        string='Satuan',
        help='Satuan produk',
        required=True
    )

    kode_biaya = fields.Char(
        string='Kode Biaya',
        help='Kode unik untuk biaya produk, digunakan untuk integrasi dengan sistem lain.'
    )

    stock_awal = fields.Float(
        string="Stock Awal",
        help="Jumlah stok awal produk",
        default=0.0
    )
    stock_akhir = fields.Float(
        string="Stock Akhir",
        compute="_compute_stock_akhir",
        store=True,
        help="Jumlah stok akhir produk berdasarkan transaksi"
    )
    stock_bebas = fields.Float(
        string="Stock Bebas",
        compute="_compute_stock_bebas",
        store=True,
        help="Jumlah stok bebas (stock on hand - reserved)"
    )

    @api.depends('qty_available', 'outgoing_qty')
    def _compute_stock_bebas(self):
        """Stock bebas = On Hand - Reserved"""
        for record in self:
            record.stock_bebas = record.qty_available - record.outgoing_qty

    @api.depends('qty_available', 'stock_awal')
    def _compute_stock_akhir(self):
        """Stock akhir = Stock Awal + On Hand"""
        for record in self:
            record.stock_akhir = record.stock_awal + record.qty_available

    _sql_constraints = [
    ('unique_dimensi_per_spesifikasi', 'unique(ukuran_dimensi, specification_id)', 'Dimensi ini sudah ada untuk spesifikasi tersebut!')
]


    # 1. Saat name diubah -> isi spesifikasi_domain
    @api.onchange('name')
    def _onchange_name(self):
        for record in self:
            record.specification_id = False
            record.spesifikasi_domain = record.name or False
            return {
                'domain': {
                    'specification_id': [('kategori', '=', record.spesifikasi_domain)]
                }
            }

    # 2. Saat specification diubah -> isi dimensi_domain
    @api.onchange('specification_id')
    def _onchange_specification(self):
        for record in self:
            record.dimension_id = False
            record.dimensi_domain = record.specification_id.name if record.specification_id else False
            return record._get_dimension_domain()

    # 3. Generate domain dinamis untuk field dimension_id
    def _get_dimension_domain(self):
        for record in self:
            domain = []
            if record.spesifikasi_domain:
                domain.append(('kategori_name', 'ilike', record.spesifikasi_domain))
            if record.dimensi_domain:
                domain.append(('specification_id', 'ilike', record.dimensi_domain))  # atau field lain di dimensi
            if record.specification_id:
                domain.append(('specification_id', '=', record.specification_id.id))
            return {
                'domain': {
                    'dimension_id': domain
                }
            }
        
    @api.model
    def create(self, vals):
        if not vals.get('kode_barang'):
            sequence = self.env['ir.sequence'].next_by_code('product.template.kode.barang') or '/'
            vals['kode_barang'] = sequence
        return super(ProductTemplate, self).create(vals)

    # 4. Cek duplikasi kombinasi spesifikasi + dimensi
    @api.constrains('specification_id', 'dimension_id')
    def _check_duplicate_product(self):
        if self._context.get('skip_duplicate_check'):
            return

        for record in self:
            if record.specification_id and record.dimension_id:
                domain = [
                    ('specification_id', '=', record.specification_id.id),
                    ('dimension_id', '=', record.dimension_id.id),
                    ('id', '!=', record.id),
                ]
                duplicate_products = self.env['product.template'].search(domain)
                if duplicate_products:
                    first_duplicate = duplicate_products[0]
                    action = {
                        'type': 'ir.actions.act_window',
                        'res_model': 'product.template',
                        'res_id': first_duplicate.id,
                        'view_mode': 'form',
                        'views': [(False, 'form')],
                        'target': 'current',
                        'flags': {'mode': 'readonly', 'clear_breadcrumbs': True},
                        'name': 'Produk Duplikat',
                    }
                    pesan = "Duplikasi produk terdeteksi:\n"
                    for p in duplicate_products:
                        pesan += f"\nKode: {p.kode_barang or '-'}\nNama: {p.name or '-'}\nSpesifikasi: {p.specification_id.display_name or '-'}\nDimensi: {p.dimension_id.display_name or '-'}\n"
                    raise RedirectWarning(pesan, action, "Lihat Duplikat")
