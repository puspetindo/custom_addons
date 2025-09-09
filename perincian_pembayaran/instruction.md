#### **1. Analisis & Desain Model**

Berdasarkan dokumen "Perincian Pembayaran", kita memerlukan dua model utama:

- **`payment.detail`**: Model ini akan menjadi objek utama yang merepresentasikan satu dokumen perincian pembayaran. Model ini akan menyimpan informasi header (penerima, nomor dokumen), total, referensi dokumen pendukung, dan informasi persetujuan di footer. Untuk nomor urut (`name`), kita akan menggunakan `ir.sequence` untuk otomatisasi. Total bersih (`amount_total_net`) akan dihitung secara otomatis dari total baris rincian.
- **`payment.detail.line`**: Model ini akan menyimpan baris-baris rincian biaya yang ada di tengah dokumen. Ini akan menjadi relasi `One2many` dari `payment.detail`.

Struktur ini memisahkan data header/footer dari data tabular (rincian), yang merupakan praktik terbaik di Odoo.

#### **2. Desain Tampilan Form (XML View)**

Tampilan form akan dirancang untuk mencerminkan tata letak dokumen fisik agar mudah digunakan:

- **Header**: Menggunakan `<group>` untuk menata field "Dibayarkan Kepada", "Jumlah Dibayarkan", dan referensi dokumen utama. Nomor urut akan ditampilkan secara menonjol di bagian atas.
- **Notebook**: Menggunakan `<notebook>` untuk mengorganisir data yang banyak.
  - **Tab 1 - Rincian Biaya**: Akan berisi tabel `line_ids` yang bisa diedit langsung (editable list view) dan field `amount_total_net` yang hanya bisa dibaca (read-only).
  - **Tab 2 - Dokumen Pendukung**: Menggunakan `<group>` dengan beberapa kolom untuk menampilkan _checklist_ dokumen. Field referensi teks (`Ref. ...`) akan muncul secara kondisional jika checkbox di sebelahnya dicentang (`attrs`).
  - **Tab 3 - Keterangan**: Area teks sederhana untuk field `notes`.
- **Footer**: Di bawah notebook, sebuah `<group>` akan digunakan untuk field tanggal dan tanda tangan (user yang terlibat).

#### **3. Generasi Kode Lengkap**

Berikut adalah seluruh file yang dibutuhkan untuk modul `perincian_pembayaran`.

---

### **Struktur File Modul**

```
custom_addons/
└── perincian_pembayaran/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   └── payment_detail.py
    ├── views/
    │   ├── payment_detail_views.xml
    │   └── payment_detail_menus.xml
    ├── data/
    │   └── ir_sequence_data.xml
    └── security/
        └── ir.model.access.csv
```

---

### **`__manifest__.py`**

File ini mendefinisikan modul Anda ke Odoo.

```python
# custom_addons/perincian_pembayaran/__manifest__.py
{
    'name': 'Perincian Pembayaran',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Vendor Payments',
    'summary': 'Modul untuk mencatat dokumen perincian pembayaran vendor.',
    'description': """
        Modul ini digunakan untuk mendigitalkan dan mengelola proses
        pencatatan dokumen perincian pembayaran kepada vendor.
    """,
    'author': 'Your Name',
    'website': 'https://your.website.com',
    'depends': [
        'account',  # Dependensi ke modul Invoicing/Accounting
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/payment_detail_views.xml',
        'views/payment_detail_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
```

**Penjelasan**: File ini mendeklarasikan metadata modul, dependensinya ke modul `account` (penting untuk menu dan fungsionalitas terkait vendor), dan urutan pemuatan file data (security, views, menu).

---

### **`__init__.py`**

File inisialisasi utama.

```python
# custom_addons/perincian_pembayaran/__init__.py
from . import models
```

---

### **`models/__init__.py`**

File inisialisasi untuk direktori models.

```python
# custom_addons/perincian_pembayaran/models/__init__.py
from . import payment_detail
```

---

### **`models/payment_detail.py`**

Definisi model Python untuk `payment.detail` dan `payment.detail.line`.

```python
# custom_addons/perincian_pembayaran/models/payment_detail.py
from odoo import api, fields, models

class PaymentDetail(models.Model):
    _name = 'payment.detail'
    _description = 'Perincian Pembayaran'
    _rec_name = 'name'

    # --- Header Fields ---
    name = fields.Char(
        string='Nomor',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Dibayarkan Kepada',
        required=True,
        domain="[('supplier_rank', '>', 0)]"
    )
    amount_paid = fields.Monetary(string='Jumlah Dibayarkan', required=True)
    source_document_ref = fields.Char(string='No. PO/DK/SPK/Surat/Memo')
    journal_entry_ref = fields.Char(string='No. Jurnal Entri')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    # --- Line Items ---
    line_ids = fields.One2many(
        'payment.detail.line',
        'payment_detail_id',
        string='Rincian Biaya'
    )

    # --- Total & Notes ---
    amount_total_net = fields.Monetary(
        string='Jumlah Bersih',
        compute='_compute_amount_total_net',
        store=True
    )
    notes = fields.Text(string='Keterangan')

    # --- Supporting Documents Checklist ---
    is_memo_attached = fields.Boolean(string="Memo / Surat / Disposisi")
    is_invoice_attached = fields.Boolean(string="Kwitansi / Invoice / Nota")
    invoice_ref = fields.Char(string="Ref. Kwitansi")
    is_tax_invoice_attached = fields.Boolean(string="Faktur Pajak")
    tax_invoice_ref = fields.Char(string="Ref. Faktur Pajak")
    is_po_attached = fields.Boolean(string="PO / OK / SPK")
    po_ref = fields.Char(string="Ref. PO")
    is_late_fee_doc_attached = fields.Boolean(string="Denda Keterlambatan")
    late_fee_doc_ref = fields.Char(string="Ref. Denda")
    is_lpb_attached = fields.Boolean(string="LPB")
    lpb_ref = fields.Char(string="Ref. LPB")
    is_ba_attached = fields.Boolean(string="Berita Acara")
    ba_ref = fields.Char(string="Ref. Berita Acara")
    is_delivery_note_attached = fields.Boolean(string="Surat Jalan /...")
    delivery_note_ref = fields.Char(string="Ref. Surat Jalan")
    is_other_doc_attached = fields.Boolean(string="Lain - lain")
    other_doc_ref = fields.Char(string="Ref. Lain-lain")

    # --- Footer & Signatures ---
    document_date = fields.Date(
        string='Tanggal Dokumen',
        default=fields.Date.context_today,
        required=True
    )
    verifier_user_id = fields.Many2one('res.users', string='Dibuat oleh (Verifikator)', default=lambda self: self.env.user)
    tax_checker_user_id = fields.Many2one('res.users', string='Diperiksa oleh (Pajak)')
    accounting_approver_user_id = fields.Many2one('res.users', string='Diketahui oleh (Akuntansi)')

    # --- Tanda Tangan Digital ---
    verifier_signature = fields.Binary(string='Tanda Tangan Verifikator')
    tax_checker_signature = fields.Binary(string='Tanda Tangan Pajak')
    accounting_approver_signature = fields.Binary(string='Tanda Tangan Akuntansi')

    @api.depends('line_ids.amount')
    def _compute_amount_total_net(self):
        for record in self:
            record.amount_total_net = sum(record.line_ids.mapped('amount'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('payment.detail.sequence') or 'New'
        return super().create(vals_list)

class PaymentDetailLine(models.Model):
    _name = 'payment.detail.line'
    _description = 'Rincian Baris Pembayaran'

    payment_detail_id = fields.Many2one('payment.detail', string='Perincian Pembayaran ID', ondelete='cascade')
    name = fields.Char(string='Keterangan', required=True)
    amount = fields.Monetary(string='Jumlah', required=True)
    currency_id = fields.Many2one(related='payment_detail_id.currency_id')
```

**Penjelasan**:

- **`payment.detail`**: Mendefinisikan semua field sesuai permintaan.
- **`@api.depends('line_ids.amount')`**: Decorator ini memastikan field `amount_total_net` akan dihitung ulang setiap kali ada perubahan pada jumlah di baris rincian.
- **`create` method**: Di-override untuk mengambil nomor urut dari `ir.sequence` yang akan kita definisikan di file XML.
- **`payment.detail.line`**: Model sederhana untuk baris rincian dengan relasi kembali ke model utama.
- **Tanda Tangan Digital**: Menambahkan field Binary untuk tanda tangan digital mengikuti konsep dari form_po.py

---

### **`data/ir_sequence_data.xml`**

File untuk membuat sequence nomor dokumen.

```xml
<odoo>
    <data noupdate="1">
        <record id="seq_payment_detail" model="ir.sequence">
            <field name="name">Nomor Perincian Pembayaran</field>
            <field name="code">payment.detail.sequence</field>
            <field name="prefix">PAYD/</field>
            <field name="padding">5</field>
            <field name="company_id" eval="False"/>
        </record>
    </data>
</odoo>
```

**Penjelasan**: File ini membuat sebuah data sequence di database saat modul diinstal. `code` (`payment.detail.sequence`) harus sama dengan yang dipanggil di model Python.

---

### **`security/ir.model.access.csv`**

File ini mengatur hak akses untuk model baru Anda.

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_payment_detail_user,payment.detail.user,model_payment_detail,base.group_user,1,1,1,1
access_payment_detail_line_user,payment.detail.line.user,model_payment_detail_line,base.group_user,1,1,1,1
```

**Penjelasan**: Memberikan hak akses penuh (baca, tulis, buat, hapus) kepada semua "Internal User" (`base.group_user`) untuk kedua model yang kita buat.

---

### **`views/payment_detail_views.xml`**

File ini mendefinisikan tampilan list (pengganti tree di Odoo 18), form, dan action.

```xml
<odoo>
    <record id="view_payment_detail_list" model="ir.ui.view">
        <field name="name">payment.detail.list</field>
        <field name="model">payment.detail</field>
        <field name="arch" type="xml">
            <list string="Perincian Pembayaran">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="document_date"/>
                <field name="amount_total_net" sum="Total"/>
                <field name="verifier_user_id"/>
            </list>
        </field>
    </record>

    <record id="view_payment_detail_form" model="ir.ui.view">
        <field name="name">payment.detail.form</field>
        <field name="model">payment.detail</field>
        <field name="arch" type="xml">
            <form string="Perincian Pembayaran">
                <sheet>
                    <div class="oe_title">
                        <h1>
                            <field name="name" readonly="1"/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <field name="partner_id"/>
                            <field name="amount_paid"/>
                        </group>
                        <group>
                            <field name="source_document_ref"/>
                            <field name="journal_entry_ref"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Rincian Biaya">
                            <field name="line_ids">
                                <list editable="bottom">
                                    <field name="name"/>
                                    <field name="amount"/>
                                    <field name="currency_id" column_invisible="1"/>
                                </list>
                            </field>
                            <group class="oe_subtotal_footer oe_right">
                                <field name="amount_total_net" class="oe_subtotal_footer_separator"/>
                            </group>
                        </page>
                        <page string="Dokumen Pendukung">
                            <group>
                                <group>
                                    <field name="is_memo_attached"/>
                                    <field name="is_invoice_attached"/>
                                    <field name="invoice_ref" attrs="{'invisible': [('is_invoice_attached', '=', False)]}"/>
                                    <field name="is_tax_invoice_attached"/>
                                    <field name="tax_invoice_ref" attrs="{'invisible': [('is_tax_invoice_attached', '=', False)]}"/>
                                    <field name="is_po_attached"/>
                                    <field name="po_ref" attrs="{'invisible': [('is_po_attached', '=', False)]}"/>
                                </group>
                                <group>
                                    <field name="is_late_fee_doc_attached"/>
                                    <field name="late_fee_doc_ref" attrs="{'invisible': [('is_late_fee_doc_attached', '=', False)]}"/>
                                    <field name="is_lpb_attached"/>
                                    <field name="lpb_ref" attrs="{'invisible': [('is_lpb_attached', '=', False)]}"/>
                                    <field name="is_ba_attached"/>
                                    <field name="ba_ref" attrs="{'invisible': [('is_ba_attached', '=', False)]}"/>
                                    <field name="is_delivery_note_attached"/>
                                    <field name="delivery_note_ref" attrs="{'invisible': [('is_delivery_note_attached', '=', False)]}"/>
                                    <field name="is_other_doc_attached"/>
                                    <field name="other_doc_ref" attrs="{'invisible': [('is_other_doc_attached', '=', False)]}"/>
                                </group>
                            </group>
                        </page>
                        <page string="Keterangan">
                            <field name="notes" placeholder="Tambahkan catatan di sini..."/>
                        </page>
                    </notebook>
                    <group string="Persetujuan">
                        <group>
                            <field name="document_date"/>
                            <field name="verifier_user_id"/>
                            <field name="verifier_signature" widget="signature"/>
                        </group>
                        <group>
                            <field name="tax_checker_user_id"/>
                            <field name="tax_checker_signature" widget="signature"/>
                            <field name="accounting_approver_user_id"/>
                            <field name="accounting_approver_signature" widget="signature"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_payment_detail" model="ir.actions.act_window">
        <field name="name">Perincian Pembayaran</field>
        <field name="res_model">payment.detail</field>
        <field name="view_mode">list,form</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Belum ada perincian pembayaran yang dibuat.
            </p>
        </field>
    </record>
</odoo>
```

**Penjelasan**:

- **`<list>`**: Sesuai konvensi Odoo 18, tag `<tree>` diganti dengan `<list>`.
- **`attrs`**: Digunakan untuk menyembunyikan field referensi secara dinamis.
- **`oe_title`**: Kelas CSS standar Odoo untuk membuat field `name` terlihat seperti judul dokumen.
- **`act_window`**: Record ini yang akan dipanggil oleh menu untuk membuka tampilan list dan form dari model `payment.detail`.
- **Tanda Tangan Digital**: Menambahkan widget signature untuk tanda tangan digital mengikuti konsep dari form_po.py

---

### **`views/payment_detail_menus.xml`**

File untuk menempatkan menu di antarmuka Odoo.

```xml
<odoo>
    <menuitem
        id="menu_payment_detail_root"
        name="Perincian Pembayaran"
        action="action_payment_detail"
        parent="account.menu_finance_payables"
        sequence="20"/>
</odoo>
```

**Penjelasan**:

- **`parent="account.menu_finance_payables"`**: Menempatkan menu ini di bawah menu utama "Vendors".
- **`action="action_payment_detail"`**: Menghubungkan menu ini ke window action yang sudah kita definisikan.
- **`sequence="20"`**: Memberikan urutan agar muncul di bawah menu standar seperti "Payments".

---

### **4. Langkah Verifikasi & Instalasi**

Untuk menguji modul yang baru dibuat:

1.  **Salin Folder**: Salin seluruh folder `perincian_pembayaran` ke dalam direktori addons kustom Anda (`C:\Program Files\Odoo18\server\custom_addons`).
2.  **Restart Service Odoo**: Pastikan Anda me-restart service Odoo agar Odoo dapat mendeteksi modul baru.
3.  **Update Daftar Aplikasi**:
    - Masuk ke Odoo dengan akun admin.
    - Aktifkan **Mode Developer** (Settings -\> General Settings -\> Activate the developer mode).
    - Pergi ke menu **Apps**.
    - Klik **Update Apps List** dan konfirmasi.
4.  **Instal Modul**:
    - Di menu Apps, hilangkan filter "Apps" dan cari "Perincian Pembayaran".
    - Klik tombol **Install**.
5.  **Periksa Hasil**:
    - Setelah instalasi selesai, refresh halaman browser Anda.
    - Pergi ke menu **Invoicing** (atau di mana pun menu Vendors berada).
    - Anda akan melihat menu baru **"Perincian Pembayaran"** di bawah grup "Vendors".
    - Klik menu tersebut dan coba buat record baru. Pastikan nomor urut terisi otomatis dan formnya terlihat sesuai desain.
