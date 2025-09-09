from odoo import api, fields, models

class DeduplicateSpesification(models.TransientModel):
    _name = 'deduplicate.spesification.wizard'
    _description = 'Wizard untuk Menghapus Duplikasi Spesifikasi'

    duplicate_count = fields.Integer(string="Jumlah Duplikasi", readonly=True)
    log_info = fields.Text(string="Informasi Log", readonly=True)
    
    @api.model
    def default_get(self, fields):
        res = super(DeduplicateSpesification, self).default_get(fields)
        
        # Menemukan spesifikasi duplikat
        self._cr.execute("""
            SELECT name, kategori, COUNT(*)
            FROM product_spesification
            GROUP BY name, kategori
            HAVING COUNT(*) > 1
        """)
        duplicates = self._cr.dictfetchall()
        res['duplicate_count'] = len(duplicates)
        
        log = "Ditemukan duplikasi pada spesifikasi berikut:\n\n"
        for dup in duplicates:
            log += f"- '{dup['name']}' (Kategori: {dup['kategori'] or '-'}) : {dup['count']} entri\n"
        
        res['log_info'] = log
        return res
    
    def deduplicate_spesification(self):
        """Proses deduplikasi spesifikasi"""
        self._cr.execute("""
            WITH duplicates AS (
                SELECT name, kategori, MIN(id) as min_id
                FROM product_spesification
                GROUP BY name, kategori
                HAVING COUNT(*) > 1
            )
            SELECT ps.id, ps.name, ps.kategori, d.min_id
            FROM product_spesification ps
            JOIN duplicates d ON ps.name = d.name AND COALESCE(ps.kategori, '') = COALESCE(d.kategori, '')
            WHERE ps.id != d.min_id
        """)
        
        duplicate_specs = self._cr.dictfetchall()
        
        # Untuk setiap spesifikasi duplikat
        log = "Proses deduplikasi:\n\n"
        updated_count = 0
        deleted_count = 0
        
        for dup in duplicate_specs:
            # Update semua produk yang menggunakan spesifikasi duplikat
            self._cr.execute("""
                UPDATE product_template
                SET specification = %s
                WHERE specification = %s
            """, (dup['min_id'], dup['id']))
            
            update_count = self._cr.rowcount
            updated_count += update_count
            
            # Update semua dimensi yang menggunakan spesifikasi duplikat
            self._cr.execute("""
                UPDATE product_dimension
                SET specification_id = %s
                WHERE specification_id = %s
            """, (dup['min_id'], dup['id']))
            
            # Hapus spesifikasi duplikat
            self._cr.execute("""
                DELETE FROM product_spesification
                WHERE id = %s
            """, (dup['id'],))
            
            log += f"- ID:{dup['id']} '{dup['name']}' (Kategori: {dup['kategori'] or '-'}) diubah ke ID:{dup['min_id']} ({update_count} produk diperbarui)\n"
            deleted_count += 1
        
        log += f"\nTotal: {deleted_count} spesifikasi duplikat dihapus dan {updated_count} produk diperbarui."
        
        # Tambahkan constraint unik setelah deduplikasi
        self._cr.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname = 'product_spesification_name_kategori_uniq'
                ) THEN
                    ALTER TABLE product_spesification 
                    ADD CONSTRAINT product_spesification_name_kategori_uniq 
                    UNIQUE (name, kategori);
                END IF;
            END
            $$;
        """)
        
        # Tampilkan summary
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'deduplicate.spesification.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
            'context': {'default_log_info': log}
        }