from odoo import fields, models, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ListPOK(models.Model):
    _name = 'list.pok'
    _description = 'list untuk pok'

    pok_form_id = fields.Many2one('pok.form', string='Form POK')
    deskripsi = fields.Char(string='Deskripsi Pekerjaan')
    tipe = fields.Char(string='Tipe')
    kode = fields.Char(string='Kode Mesin / Aset')
    target_selesai = fields.Date(string='Target Selesai')
    tanggal_rencana = fields.Date(string='Tanggal Rencana')
    tanggal_selesai = fields.Date(string="Tanggal Selesai")
    penjelasan = fields.Text(string="Penjelasan Progres")

    @api.onchange('target_selesai', 'tanggal_rencana', 'tanggal_selesai')
    def _onchange_tanggal_validation(self):
        """Validasi tanggal saat field berubah (real-time)"""
        _logger.info("=== VALIDASI ONCHANGE DIPANGGIL ===")
        _logger.info(f"Target Selesai: {self.target_selesai}")
        _logger.info(f"Tanggal Rencana: {self.tanggal_rencana}")
        _logger.info(f"Tanggal Selesai: {self.tanggal_selesai}")
        
        if self.tanggal_rencana and self.target_selesai:
            if self.target_selesai < self.tanggal_rencana:
                # Reset field yang tidak valid
                self.target_selesai = False
                return {
                    'warning': {
                        'title': 'Error Tanggal!',
                        'message': f'Target Selesai tidak boleh kurang dari Tanggal Rencana ({self.tanggal_rencana}).'
                    }
                }
        
        # Validasi 2: Tanggal Selesai tidak boleh kurang dari Tanggal Rencana
        if self.tanggal_selesai and self.tanggal_rencana:
            if self.tanggal_selesai < self.tanggal_rencana:
                # Reset field yang tidak valid
                self.tanggal_selesai = False
                return {
                    'warning': {
                        'title': 'Error Tanggal!',
                        'message': f'Tanggal Selesai tidak boleh kurang dari Tanggal Rencana ({self.tanggal_rencana}). '
                    }
                }
        
        _logger.info("=== VALIDASI ONCHANGE BERHASIL ===")

    # Tetap pertahankan constrains untuk validasi saat save (sebagai backup)
    @api.constrains('target_selesai', 'tanggal_rencana', 'tanggal_selesai')
    def _check_tanggal_validation(self):
        """Validasi tanggal saat save (backup validation)"""
        _logger.info("=== VALIDASI CONSTRAINS DIPANGGIL ===")
        for record in self:
            _logger.info(f"Record ID: {record.id}")
            _logger.info(f"Target Selesai: {record.target_selesai}")
            _logger.info(f"Tanggal Rencana: {record.tanggal_rencana}")
            _logger.info(f"Tanggal Selesai: {record.tanggal_selesai}")
            
            if record.tanggal_rencana and record.target_selesai:
                if record.tanggal_rencana > record.target_selesai:
                    raise ValidationError(
                        f"Target Selesai ({record.target_selesai}) tidak boleh kurang dari "
                        f"Tanggal Rencana ({record.tanggal_rencana})."
                    )
            
            if record.tanggal_selesai and record.tanggal_rencana:
                if record.tanggal_rencana > record.tanggal_selesai:
                    raise ValidationError(
                        f"Tanggal Selesai ({record.tanggal_selesai}) tidak boleh kurang dari "
                        f"Tanggal Rencana ({record.tanggal_rencana})."
                    )
                
        _logger.info("=== VALIDASI CONSTRAINS BERHASIL ===")