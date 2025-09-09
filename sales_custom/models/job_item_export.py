from odoo import models, fields, api
import xlsxwriter
import io
import base64
from datetime import datetime

class JobItemExportWizard(models.TransientModel):
    _name = 'sales_custom.job_item.export.wizard'
    _description = 'Job Item Export Wizard'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    job_type = fields.Selection([
        ('fabrication', 'Fabrication'),
        ('machining', 'Machining'),
        ('assembly', 'Assembly'),
        ('painting', 'Painting'),
        ('inspection', 'Inspection'),
        ('packaging', 'Packaging'),
        ('shipping', 'Shipping')
    ], string='Job Type')
    export_file = fields.Binary(string='Export File', readonly=True)
    export_filename = fields.Char(string='Export Filename', readonly=True)

    def action_export_job_items(self):
        """Export job items to Excel based on selected criteria"""
        self.ensure_one()
        
        # Get job items based on criteria
        domain = []
        if self.date_from and self.date_to:
            domain.append(('order_id.date_order', '>=', self.date_from))
            domain.append(('order_id.date_order', '<=', self.date_to))
        if self.job_type:
            domain.append(('type', '=', self.job_type))
        
        job_items = self.env['sales_custom.job.item'].search(domain)
        
        if not job_items:
            raise models.UserError('No job items found for the selected criteria.')
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Job Items')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        cell_format = workbook.add_format({'border': 1})
        number_format = workbook.add_format({'border': 1, 'num_format': '#,##0.00'})
        
        # Set column widths
        worksheet.set_column('A:A', 15)  # Order Number
        worksheet.set_column('B:B', 20)  # Customer
        worksheet.set_column('C:C', 15)  # Date
        worksheet.set_column('D:D', 15)  # Job Type
        worksheet.set_column('E:E', 25)  # Item Name
        worksheet.set_column('F:F', 15)  # Item No
        worksheet.set_column('G:G', 15)  # Number
        worksheet.set_column('H:H', 10)  # Qty
        worksheet.set_column('I:I', 15)  # Weight (Ton)
        worksheet.set_column('J:J', 15)  # Diameter
        worksheet.set_column('K:K', 15)  # Thickness
        worksheet.set_column('L:L', 15)  # Length
        worksheet.set_column('M:M', 20)  # Material
        
        # Write headers
        headers = [
            'Order Number', 'Customer', 'Date', 'Job Type', 'Item Name',
            'Item No', 'Number', 'Qty', 'Weight (Ton)', 'Diameter',
            'Thickness', 'Length', 'Material'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Write data
        row = 1
        for item in job_items:
            worksheet.write(row, 0, item.order_id.name or '', cell_format)
            worksheet.write(row, 1, item.order_id.partner_id.name or '', cell_format)
            worksheet.write(row, 2, item.order_id.date_order.strftime('%Y-%m-%d') if item.order_id.date_order else '', cell_format)
            worksheet.write(row, 3, dict(item._fields['type'].selection).get(item.type, ''), cell_format)
            worksheet.write(row, 4, item.name or '', cell_format)
            worksheet.write(row, 5, item.item_no or '', cell_format)
            worksheet.write(row, 6, item.number or '', cell_format)
            worksheet.write(row, 7, item.qty or 0, number_format)
            worksheet.write(row, 8, item.weight_ton or 0, number_format)
            worksheet.write(row, 9, item.diameter or 0, number_format)
            worksheet.write(row, 10, item.thk or 0, number_format)
            worksheet.write(row, 11, item.length or 0, number_format)
            worksheet.write(row, 12, item.material or '', cell_format)
            row += 1
        
        workbook.close()
        output.seek(0)
        
        # Generate filename
        filename = f"job_items_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Save file
        self.export_file = base64.b64encode(output.read())
        self.export_filename = filename
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/export_file?download=true&filename={filename}',
            'target': 'self',
        }

    def action_download_file(self):
        """Download the generated file"""
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/export_file?download=true&filename={self.export_filename}',
            'target': 'self',
        }
