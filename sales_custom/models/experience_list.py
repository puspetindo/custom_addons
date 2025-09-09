# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
import io
import xlsxwriter
from datetime import datetime
from odoo.modules.module import get_module_resource


class ExperienceList(models.Model):
    _name = 'experience.list'
    _description = 'Experience List - Daftar Order Information'
    _auto = False  # View model, bukan tabel nyata

    # Fields
    no = fields.Integer(string='No', readonly=True)
    job_no = fields.Char(string='Job No', readonly=True)
    equipment_package = fields.Char(string='Equipment/Package', readonly=True)
    client = fields.Many2one('res.partner', string="Client", readonly=True)
    material = fields.Char(string='Material', readonly=True)
    qty = fields.Integer(string='Qty', readonly=True)
    weight = fields.Float(string='Weight', readonly=True)
    value_idr = fields.Float(string='Value', readonly=True)
    status_open = fields.Date(string='Status Open (Tanggal PO/SPK)', readonly=True)
    status_closed = fields.Date(string='Status Closed (Tanggal BAST)', readonly=True)
    bast_number = fields.Char(string='No. BAST', readonly=True)

    def init(self):
        self._cr.execute("""
            DROP VIEW IF EXISTS experience_list CASCADE
        """)
        self._cr.execute("""
            CREATE OR REPLACE VIEW experience_list AS (
                SELECT 
                    CAST(ROW_NUMBER() OVER (ORDER BY oi.id) AS INTEGER) as id,
                    CAST(ROW_NUMBER() OVER (ORDER BY oi.id) AS INTEGER) as no,
                    oi.job_order_no as job_no,
                    ji.name as equipment_package,
                    oi.customer_id as client,
                    ji.material as material,
                    ji.qty as qty,
                    ji.weight_ton as weight,
                    oi.value_idr as value_idr,
                    oi.date_4 as status_open,
                    oi.close_date as status_closed,
                    oi.bast_number as bast_number
                FROM (
                    SELECT 
                        ji.*,
                        ROW_NUMBER() OVER (PARTITION BY ji.order_id ORDER BY ji.id) as rn
                    FROM sales_custom_job_item ji
                ) ji
                INNER JOIN sales_custom_order_information oi ON ji.order_id = oi.id
                WHERE oi.status != 'cancel'
                  AND ji.rn = 1   -- hanya ambil equipment pertama tiap OI
                ORDER BY oi.id
            )
        """)


    def action_download_excel(self):
        records = self.search([])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Experience List')

        # Insert logo
        logo_path = get_module_resource('sales_custom', 'static/src/image/logo.png')
        worksheet.insert_image('A1', logo_path, {'x_offset': 2, 'y_offset': 2, 'x_scale': 0.62, 'y_scale': 0.62})

        # Format
        title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#C6EFCE', 'align': 'center', 'border': 1})
        cell_format = workbook.add_format({'border': 1, 'align': 'left'})
        number_format = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '#,##0.00'})
        date_format = workbook.add_format({'border': 1, 'align': 'center', 'num_format': 'dd/mm/yyyy'})

        # Set column widths
        worksheet.set_column('A:A', 5)   # No.
        worksheet.set_column('B:B', 15)  # Job No
        worksheet.set_column('C:C', 25)  # Equipment/Package
        worksheet.set_column('D:D', 10)  # Client
        worksheet.set_column('E:E', 15)  # Material
        worksheet.set_column('F:F', 8)   # Qty
        worksheet.set_column('G:G', 12)  # Weight
        worksheet.set_column('H:H', 15)  # Value
        worksheet.set_column('I:I', 15)  # Status Open
        worksheet.set_column('J:J', 15)  # Status Closed
        worksheet.set_column('K:K', 15)  # No. BAST

        # Title
        worksheet.merge_range('A1:K1', 'EXPERIENCE LIST', title_format)
        worksheet.merge_range('A2:K2', str(datetime.today().year), title_format)

        # Header
        headers = [
            'No.', 'Job No', 'Equipment/Package', 'Client', 'Material',
            'Qty', 'Weight', 'Value', 'Status Open', 'Status Closed', 'No. BAST'
        ]
        worksheet.write_row('A5', headers, header_format)

        # Data
        row = 5
        for rec in records:
            worksheet.write(row, 0, rec.no or 0, cell_format)
            worksheet.write(row, 1, rec.job_no or '', cell_format)
            worksheet.write(row, 2, rec.equipment_package or '', cell_format)
            worksheet.write(row, 3, rec.client.name if rec.client else '', cell_format)
            worksheet.write(row, 4, rec.material or '', cell_format)
            worksheet.write(row, 5, rec.qty or 0, cell_format)
            worksheet.write(row, 6, rec.weight or 0, number_format)
            worksheet.write(row, 7, rec.value_idr or 0, number_format)
            worksheet.write(row, 8, rec.status_open or '', date_format)
            worksheet.write(row, 9, rec.status_closed or '', date_format)
            worksheet.write(row, 10, rec.bast_number or '', cell_format)
            row += 1

        workbook.close()
        output.seek(0)

        file_name = 'Experience_List_%s.xlsx' % datetime.today().year
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'res_model': 'experience.list',
            'res_id': False,
        })

        output.close()

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'new',
        }
