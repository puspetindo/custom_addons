# Custom Addons

## Deskripsi Umum

Folder `custom_addons` berisi kumpulan modul-modul kustom yang dikembangkan untuk memperluas dan menyesuaikan fungsionalitas Odoo sesuai kebutuhan bisnis spesifik. Modul-modul ini meliputi berbagai aspek mulai dari manajemen inventori, penjualan, pembayaran vendor, hingga permintaan material khusus.

## Daftar Modul dan Ringkasan

1. **inventory_extensions**

   - Memperluas modul inventory dengan penambahan spesifikasi produk, dimensi, satuan custom, dan laporan penerimaan barang (LPB).

2. **invoice_extensions**

   - Menambahkan field custom pada invoice untuk informasi purchase order dan pengiriman, serta menyediakan laporan invoice yang disesuaikan.

3. **perincian_pembayaran**

   - Modul untuk mendigitalkan dan mengelola proses pencatatan dokumen perincian pembayaran kepada vendor, lengkap dengan workflow approval dan manajemen dokumen pendukung.

4. **sales_custom**

   - Aplikasi penjualan kustom yang mengelola informasi pesanan, job items, experience list, dan menyediakan workflow serta reporting yang disesuaikan.

5. **vendor_payment_detail**

   - Integrasi perincian pembayaran dengan vendor bill dalam satu model terpadu, dengan fitur template biaya, manajemen dokumen, dan tanda tangan digital.

6. **wmr (Welding Material Requisition)**
   - Sistem manajemen permintaan material pengelasan, termasuk purchase order kontrak, order kerja, dan berbagai laporan terkait.

## Tujuan Folder Custom Addons

- Menyediakan solusi kustom yang tidak tersedia di modul standar Odoo.
- Memudahkan pengembangan dan pemeliharaan fitur bisnis spesifik.
- Memfasilitasi integrasi antar modul kustom dan modul standar Odoo.
- Menyimpan modul-modul yang dapat di-deploy dan di-update secara independen.

## Saran Perbaikan Kedepan

- Menyatukan Custom Modul yang masih berdiri sendiri
- Standarisasi dokumentasi dan struktur modul untuk konsistensi.
- Pengembangan modul tambahan sesuai kebutuhan bisnis yang berkembang.
- Peningkatan testing otomatis untuk setiap modul.
- Optimasi performa dan keamanan modul.


## Cara Instalasi dan Penggunaan

1. Pastikan folder `custom_addons` berada di path addons Odoo.
2. Restart service Odoo untuk mendeteksi modul baru.
3. Update daftar aplikasi melalui menu Apps di Odoo.
4. Install modul yang dibutuhkan sesuai kebutuhan bisnis.
5. Konfigurasi modul melalui menu pengaturan masing-masing modul.
6. Lakukan testing dan verifikasi fungsi modul setelah instalasi.

## Informasi Tambahan
Dokumentasi ini dibuat untuk memudahkan pemahaman dan pengelolaan seluruh modul kustom yang ada di folder `custom_addons`.

