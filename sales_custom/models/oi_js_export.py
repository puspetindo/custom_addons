from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
from datetime import datetime
import xlsxwriter
from odoo.modules.module import get_module_resource

class OiJsExportWizard(models.TransientModel):
    _name = 'sales_custom.oi_js.export.wizard'
    _description = 'Order Information JS Export Wizard'

    file_data = fields.Binary(string='File Data', readonly=True)
    file_name = fields.Char(string='File Name', readonly=True)

    def action_export_excel_js(self):
        self.ensure_one()
        
        orders = self.env['sales_custom.oi_js'].search([])
        if not orders:
            raise UserError(_('Tidak ada data Order Information JS yang ditemukan.'))
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Daftar Project JS')

        # Logo
        logo_path = get_module_resource('sales_custom', 'static/src/image/logo.png')
        worksheet.insert_image('A1', logo_path, {'x_offset': 2, 'y_offset': 2, 'x_scale': 0.6, 'y_scale': 0.6})

        # Format judul
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter'
        })

        header_right = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 10
        })

        # Judul utama
        worksheet.merge_range('A1:L1', 'Daftar Project JS', title_format)
        worksheet.merge_range('A2:L2', str(datetime.today().year), title_format)

        worksheet.merge_range('M1:O1', 'Form No. : 2110-FRM-03-05', header_right)
        worksheet.merge_range('M2:O2', 'Rev.     : 0', header_right)
        worksheet.merge_range('M3:O3', 'Eff. Date: 5 Januari 2021', header_right)

        # Format tabel
        header_gray = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D9D9D9',
            'border': 1
        })
        header_orange = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#F79646',
            'border': 1
        })
        cell_format = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'border': 1})
        number_format = workbook.add_format({'num_format': '#,##0.00', 'align': 'right', 'valign': 'vcenter', 'border': 1})
        date_format = workbook.add_format({'num_format': 'dd-mm-yyyy', 'align': 'center', 'valign': 'vcenter', 'border': 1})

        # Atur lebar kolom (bisa sesuaikan lagi)
        worksheet.set_column('A:A', 5)  # No
        worksheet.set_column('B:C', 12) # Date Starting & Delivery
        worksheet.set_column('D:D', 15) # Project No.
        worksheet.set_column('E:E', 20) # Project Name
        worksheet.set_column('F:F', 15) # Contract No
        worksheet.set_column('G:G', 20) # Customer Name
        worksheet.set_column('H:H', 15) # Quotation No.
        worksheet.set_column('I:I', 20) # Package/Equipment
        worksheet.set_column('J:J', 8)  # Qty
        worksheet.set_column('K:K', 20) # Material
        worksheet.set_column('L:L', 10) # Weight (Ton)
        worksheet.set_column('M:M', 8)  # Stamp
        worksheet.set_column('N:O', 15) # Value USD, IDR
        worksheet.set_column('P:P', 15) # Status
        worksheet.set_column('Q:Q', 15) # Remark

        # Header tabel
        worksheet.merge_range('A4:A5', 'No', header_gray)
        worksheet.merge_range('B4:C4', 'DATE', header_gray)
        worksheet.write('B5', 'STARTING', header_orange)
        worksheet.write('C5', 'DELIVERY', header_orange)
        worksheet.merge_range('D4:D5', 'PROJECT NO.', header_gray)
        worksheet.merge_range('E4:E5', 'PROJECT NAME', header_gray)
        worksheet.merge_range('F4:F5', 'CONTRACT NO', header_gray)
        worksheet.merge_range('G4:G5', 'CUSTOMER NAME', header_gray)
        worksheet.merge_range('H4:H5', 'QUOTATION NO.', header_gray)
        worksheet.merge_range('I4:K4', 'EQUIPMENT', header_gray)
        worksheet.write('I5', 'PACKAGE/EQUIPMENT', header_orange)
        worksheet.write('J5', 'QTY', header_orange)
        worksheet.write('K5', 'MATERIAL', header_orange)
        worksheet.merge_range('L4:L5', 'WEIGHT (TON)', header_gray)
        worksheet.merge_range('M4:M5', 'STAMP', header_gray)
        worksheet.merge_range('N4:O4', 'VALUE', header_gray)
        worksheet.write('N5', 'USD', header_orange)
        worksheet.write('O5', 'IDR', header_orange)
        worksheet.merge_range('P4:P5', 'STATUS', header_gray)
        worksheet.merge_range('Q4:Q5', 'REMARK', header_gray)

        # Isi data
        row = 5
        no = 1
        for order in orders:
            for item in order.item_purchased_js:
                worksheet.write(row, 0, no, cell_format)
                worksheet.write(row, 1, order.date_1 or '', date_format)
                worksheet.write(row, 2, order.delivery_input or order.date_4 or '', date_format)
                worksheet.write(row, 3, order.job_order_no or '', cell_format)
                worksheet.write(row, 4, order.project or '', cell_format)
                worksheet.write(row, 5, order.pospk_no or '', cell_format)
                worksheet.write(row, 6, order.customer_id.name or '', cell_format)
                worksheet.write(row, 7, order.quotation_no or '', cell_format)
                worksheet.write(row, 8, item.name or '', cell_format)
                worksheet.write(row, 9, item.qty or 0, number_format)
                worksheet.write(row, 10, item.material or '', cell_format)
                worksheet.write(row, 11, item.weight_ton or 0, number_format)
                worksheet.write(row, 12, 'Yes' if order.stamp else 'No', cell_format)
                worksheet.write(row, 13, order.value_usd or 0, number_format)
                worksheet.write(row, 14, order.value_idr or 0, number_format)
                worksheet.write(row, 15, order.status or '', cell_format)
                remark_month = ''
                if order.date_1:
                    remark_month = order.date_1.strftime('%b').upper()
                worksheet.write(row, 16, remark_month, cell_format)
                row += 1
                no += 1

        workbook.close()
        output.seek(0)
        file_data = base64.b64encode(output.read())
        output.close()

        self.file_data = file_data
        self.file_name = f'Daftar_Project_JS_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=sales_custom.oi_js.export.wizard&id={self.id}&field=file_data&filename_field=file_name&download=true',
            'target': 'new',
        }
