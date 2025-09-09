from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
from datetime import datetime
import xlsxwriter
from odoo.modules.module import get_module_resource

class OrderInformationExportWizard(models.TransientModel):
    _name = 'sales_custom.order_information.export.wizard'
    _description = 'Order Information Export Wizard'

    file_data = fields.Binary(string='File Data', readonly=True)
    file_name = fields.Char(string='File Name', readonly=True)

    def action_export_excel_custom(self):
        self.ensure_one()
        
        orders = self.env['sales_custom.order_information'].search([])
        if not orders:
            raise UserError(_('Tidak ada data order information yang ditemukan.'))
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Daftar Project')

        # Tambahkan logo
        # Insert logo
        logo_path = get_module_resource('sales_custom', 'static/src/image/logo.png')
        worksheet.insert_image('A1', logo_path, {'x_offset': 2, 'y_offset': 2, 'x_scale': 0.62, 'y_scale': 0.62})
        
        # Format judul
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter'
        })

        # Format untuk header kanan atas
        header_right = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 10
        })

        # Judul besar di tengah atas
        worksheet.merge_range('A1:P1', 'Daftar Project', title_format)
        worksheet.merge_range('A2:P2', '2025', title_format)

        # ====== Tambahkan blok Form No, Rev, Eff Date di pojok kanan ======
        worksheet.merge_range('Q1:S1', 'Form No. : 2110-FRM-03-05', header_right)
        worksheet.merge_range('Q2:S2', 'Rev.     : 0', header_right)
        worksheet.merge_range('Q3:S3', 'Eff. Date: 5 Januari 2021', header_right)
        # ==================================================================

        # Define formats
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
        cell_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1
        })
        number_format = workbook.add_format({
            'num_format': '#,##0.00',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1
        })
        date_format = workbook.add_format({
            'num_format': 'dd-mm-yyyy',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        # Set column widths
        worksheet.set_column('A:A', 5)   # No
        worksheet.set_column('B:C', 12)  # Date Starting, Delivery
        worksheet.set_column('D:D', 15)  # Project No
        worksheet.set_column('E:E', 20)  # Project Name
        worksheet.set_column('F:F', 15)  # Contract No
        worksheet.set_column('G:G', 20)  # Customer Name
        worksheet.set_column('H:H', 15)  # Quotation No
        worksheet.set_column('I:I', 20)  # Package/Equipment
        worksheet.set_column('J:J', 8)   # Type
        worksheet.set_column('K:K', 8)   # Qty
        worksheet.set_column('L:L', 20)  # Material
        worksheet.set_column('M:M', 10)  # Weight (Ton)
        worksheet.set_column('N:P', 10)  # Dimension (Dia/W, Thk, Length)
        worksheet.set_column('Q:Q', 8)   # Stamp
        worksheet.set_column('R:S', 15)  # Value USD, IDR
        worksheet.set_column('T:T', 15)  # Status
        worksheet.set_column('U:U', 15)  # Remark
        worksheet.set_column('V:X', 20)  # Form Info

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
        worksheet.merge_range('I4:L4', 'EQUIPMENT', header_gray)
        worksheet.write('I5', 'PACKAGE/EQUIPMENT', header_orange)
        worksheet.write('J5', 'TYPE', header_orange)
        worksheet.write('K5', 'QTY', header_orange)
        worksheet.write('L5', 'MATERIAL', header_orange)
        worksheet.merge_range('M4:M5', 'WEIGHT (TON)', header_gray)
        worksheet.merge_range('N4:P4', 'DIMENSION', header_gray)
        worksheet.write('N5', 'DIA/W', header_orange)
        worksheet.write('O5', 'THK', header_orange)
        worksheet.write('P5', 'LENGTH', header_orange)
        worksheet.merge_range('Q4:Q5', 'STAMP', header_gray)
        worksheet.merge_range('R4:S4', 'VALUE', header_gray)
        worksheet.write('R5', 'USD', header_orange)
        worksheet.write('S5', 'IDR', header_orange)
        worksheet.merge_range('T4:T5', 'STATUS', header_gray)
        worksheet.merge_range('U4:U5', 'REMARK', header_gray)
        
        # Isi data
        row = 5
        no = 1
        for order in orders:
            for item in order.item_purchased:
                worksheet.write(row, 0, no, cell_format)
                worksheet.write(row, 1, order.date_1 or '', date_format)
                worksheet.write(row, 2, order.delivery_input or order.date_4 or '', date_format)
                worksheet.write(row, 3, order.job_order_no or '', cell_format)
                worksheet.write(row, 4, order.project or '', cell_format)
                worksheet.write(row, 5, order.pospk_no or '', cell_format)
                worksheet.write(row, 6, order.customer_id.name or '', cell_format)
                worksheet.write(row, 7, order.quotation_no or '', cell_format)
                worksheet.write(row, 8, item.name or '', cell_format)
                worksheet.write(row, 9, dict(item._fields['type'].selection).get(item.type, '') if item.type else '', cell_format)
                worksheet.write(row, 10, item.qty or 0, number_format)
                worksheet.write(row, 11, item.material or '', cell_format)
                worksheet.write(row, 12, item.weight_ton or 0, number_format)
                worksheet.write(row, 13, item.diameter or '', cell_format)
                worksheet.write(row, 14, item.thk or '', cell_format)
                worksheet.write(row, 15, item.length or '', cell_format)
                stamp_val = order.stamp
                if stamp_val is None:
                    stamp_str = ''
                elif isinstance(stamp_val, bool):
                    stamp_str = 'Yes' if stamp_val else 'No'
                else:
                    stamp_str = str(stamp_val)
                worksheet.write(row, 16, stamp_str, cell_format)
                worksheet.write(row, 17, order.value_usd or 0, number_format)
                worksheet.write(row, 18, order.value_idr or 0, number_format)
                worksheet.write(row, 19, order.status or '', cell_format)
                remark_month = ''
                if order.date_1:
                    remark_month = order.date_1.strftime('%b').upper()
                worksheet.write(row, 20, remark_month, cell_format)
                row += 1
                no += 1

        workbook.close()
        output.seek(0)
        file_data = base64.b64encode(output.read())
        output.close()

        self.file_data = file_data
        self.file_name = f'Daftar_Project_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model=sales_custom.order_information.export.wizard&id={self.id}&field=file_data&filename_field=file_name&download=true',
            'target': 'new',
        }
