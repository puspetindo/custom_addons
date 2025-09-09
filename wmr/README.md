# Welding Material Requisition (WMR)

## Tujuan Modul

Modul Welding Material Requisition (WMR) adalah sistem terintegrasi untuk mengelola permintaan material pengelasan dalam konteks manufaktur dan konstruksi. Modul ini menyediakan workflow lengkap dari permintaan material hingga pelacakan penggunaan, dengan integrasi yang kuat dengan sistem procurement dan inventory Odoo.

### Fitur Utama:

1. **WMR Management**: Sistem permintaan material pengelasan
2. **Purchase Order Kontrak (POK)**: Manajemen purchase order kontrak
3. **Order Kerja**: Sistem manajemen order kerja dengan detail
4. **Multi-Report System**: Berbagai template laporan untuk kebutuhan berbeda
5. **Integration dengan Procurement**: Seamless integration dengan purchase dan inventory
6. **Document Number Notifier**: Sistem notifikasi nomor dokumen real-time

### Manfaat:

- Memperbaiki koordinasi antara procurement dan production
- Mengurangi waste material dengan tracking yang akurat
- Meningkatkan efisiensi dalam proses pengelasan
- Memudahkan audit trail untuk material usage
- Mempercepat response time untuk material requirements

## Struktur Kode

### Model Utama:

- `wmr`: Model untuk Welding Material Requisition
- `pok`: Model untuk Purchase Order Kontrak
- `order.kerja`: Model untuk Order Kerja
- `order.kerja.detail`: Model detail untuk order kerja

### Komponen View:

- Form views untuk setiap model utama
- List views dengan advanced filtering
- Custom menu structure
- Integrated report actions

### Assets dan Enhancements:

- Custom JavaScript untuk document number notifier
- Company logo integration untuk reports
- Custom paper format untuk printing
- Enhanced UI components

## Dokumentasi Kode

### Model Structure

```python
class WMR(models.Model):
    _name = 'wmr'
    _description = 'Welding Material Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='WMR Number', required=True, copy=False, readonly=True, default='New')
    date_request = fields.Date(string='Request Date', default=fields.Date.today, required=True)
    project_id = fields.Many2one('project.project', string='Project')
    requester_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user)

    # Material Lines
    material_line_ids = fields.One2many('wmr.material.line', 'wmr_id', string='Material Lines')

    # Workflow States
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('procurement', 'In Procurement'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
```

### Document Number Notifier

```javascript
// static/src/js/document_number_notifier.js
odoo.define("wmr.document_number_notifier", function (require) {
  "use strict";

  var FormController = require("web.FormController");

  FormController.include({
    _onFieldChanged: function (ev) {
      this._super.apply(this, arguments);
      // Custom logic untuk notifikasi nomor dokumen
      if (ev.data.changes.name) {
        this._notifyDocumentNumber(ev.data.changes.name);
      }
    },

    _notifyDocumentNumber: function (docNumber) {
      // Implementation untuk notifikasi
      this.displayNotification({
        type: "info",
        title: "Document Number Updated",
        message: "New document number: " + docNumber,
      });
    },
  });
});
```

### Workflow Implementation

```python
def action_submit(self):
    self.write({'state': 'submitted'})
    # Create activity untuk approver
    self.activity_schedule(
        'WMR Approval',
        user_id=self.approver_id.id,
        note='Please review WMR for approval'
    )

def action_approve(self):
    self.write({'state': 'approved'})
    # Trigger procurement process
    self._create_procurement_order()
```

## Saran Perbaikan Kedepan

### 1. Advanced Material Tracking

- RFID/NFC integration untuk real-time tracking
- IoT sensors untuk inventory monitoring
- QR code system untuk material identification
- Blockchain untuk immutable material history

### 2. Predictive Analytics

- AI-powered demand forecasting
- Material usage pattern analysis
- Predictive maintenance untuk welding equipment
- Automated reorder point calculation

### 3. Mobile Application

- Mobile app untuk field technicians
- Offline material request capability
- GPS tracking untuk material delivery
- Photo documentation untuk material condition

### 4. Integration dengan CAD/CAM

- Direct integration dengan CAD software
- Automatic material calculation dari design files
- BOM (Bill of Materials) auto-generation
- CNC machine integration

### 5. Quality Control Integration

- Automated quality checks untuk incoming materials
- Certificate of conformance tracking
- Non-conformance reporting system
- Supplier quality score tracking

### 6. Advanced Reporting

- Real-time dashboard untuk material status
- Cost analysis per project
- Efficiency metrics untuk welding operations
- Trend analysis untuk material consumption

### 7. Multi-Site Support

- Cross-site material transfer
- Centralized inventory management
- Inter-site procurement coordination
- Consolidated reporting untuk multi-site operations

### 8. Environmental Compliance

- Material traceability untuk environmental compliance
- Waste tracking dan reporting
- Sustainable material sourcing
- Carbon footprint calculation

## Teknologi yang Digunakan

- **Odoo Framework**: Versi 18.0
- **Python**: Backend business logic
- **JavaScript**: Frontend enhancements
- **XML**: View dan template definitions
- **QWeb**: Report generation
- **PostgreSQL**: Database management

## Dependencies

- `base`: Core Odoo functionality
- `sales_custom`: Integration dengan sales module
- `purchase`: Procurement system integration
- `stock`: Inventory management
- `web`: Web interface components

## Instalasi dan Konfigurasi

1. Copy module ke custom addons directory
2. Restart Odoo server
3. Install melalui Apps menu
4. Configure sequences untuk document numbering
5. Setup user permissions dan approval workflow
6. Configure integration dengan procurement system

## Testing

Modul telah ditest untuk:

- WMR creation dengan multiple material lines
- Workflow transitions melalui semua states
- Report generation untuk berbagai format
- Integration dengan purchase dan stock modules
- Document number notification functionality

## Maintenance

### Regular Maintenance Tasks:

- Sequence number monitoring
- Database cleanup untuk old records
- Performance optimization untuk large datasets
- Integration testing dengan updated dependencies

### Performance Considerations:

- Material line processing optimization
- Report generation speed monitoring
- Database indexing untuk frequently queried fields
- Cache management untuk improved response times

## Support Guidelines

### Common Issues:

- Document number not updating: Check sequence configuration
- Workflow stuck: Verify user permissions dan transition conditions
- Report generation errors: Check QWeb template syntax
- Integration failures: Verify API endpoints dan data formats

### Troubleshooting Steps:

1. Check Odoo server logs untuk error messages
2. Verify database connections dan constraints
3. Test dengan minimal dataset
4. Check network connectivity untuk external integrations

## Version History

- **v1.0**: Initial release dengan basic WMR functionality
- **v1.1**: Added POK dan Order Kerja modules
- **v1.2**: Enhanced reporting system
- **v1.3**: Performance improvements dan bug fixes

## Future Roadmap

- AI-powered material optimization
- IoT integration untuk smart manufacturing
- Advanced analytics dashboard
- Mobile application development
- Multi-company support enhancement
- Integration dengan Industry 4.0 systems
