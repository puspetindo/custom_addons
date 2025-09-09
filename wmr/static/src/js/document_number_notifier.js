/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";

console.log('WMR Document Notifier: Loading patch...');

patch(FormController.prototype, {
    setup() {
        console.log('FormController setup - Model:', this.props?.resModel);
        super.setup();
        
        // Initialize untuk WMR form saja
        if (this.props?.resModel === "wmr.wmr_form") {
            this._prevDocumentNumber = null;
            console.log('WMR form controller initialized');
        }
    },

    async saveRecord(...args) {
        const model = this.props?.resModel;
        console.log('SaveRecord called for model:', model);

        // Validasi khusus untuk WMR form
        if (model === "wmr.wmr_form") {
            console.log('Processing WMR form validation...');
            
            try {
                const items = this.model?.root?.data?.item_purchased || [];
                console.log('Items found:', items.length);
                
                if (items.length === 0) {
                    console.log('No items - showing warning notification');
                    
                    // Coba notification service
                    if (this.env?.services?.notification) {
                        this.env.services.notification.add(
                            "Form WMR harus memiliki minimal 1 item.", 
                            {
                                title: "Gagal Menyimpan",
                                type: "warning",
                            }
                        );
                        console.log('Warning notification sent via notification service');
                    } else if (this.displayNotification) {
                        // Fallback ke displayNotification jika ada
                        this.displayNotification({
                            title: "Gagal Menyimpan",
                            message: "Form WMR harus memiliki minimal 1 item.",
                            type: "warning",
                        });
                        console.log('Warning notification sent via displayNotification');
                    } else {
                        // Ultimate fallback
                        alert("Gagal Menyimpan: Form WMR harus memiliki minimal 1 item.");
                        console.log('Warning shown via alert');
                    }
                    
                    return Promise.resolve();
                }

                // Simpan document number sebelumnya jika belum ada
                if (this._prevDocumentNumber === null) {
                    this._prevDocumentNumber = this.model?.root?.data?.document_number || null;
                    console.log('Previous document number stored:', this._prevDocumentNumber);
                }
            } catch (error) {
                console.error('Error in WMR validation:', error);
            }
        }

        // Panggil original saveRecord
        console.log('Calling original saveRecord...');
        const result = await super.saveRecord(...args);
        console.log('Original saveRecord completed');

        // Check perubahan document number untuk WMR
        if (model === "wmr.wmr_form") {
            try {
                const newDocNumber = this.model?.root?.data?.document_number;
                console.log('Checking document number change:', {
                    new: newDocNumber,
                    previous: this._prevDocumentNumber
                });
                
                if (newDocNumber && newDocNumber !== this._prevDocumentNumber) {
                    console.log('Document number changed - showing success notification');
                    
                    // Coba notification service
                    if (this.env?.services?.notification) {
                        this.env.services.notification.add(
                            `Nomor dokumen berhasil digenerate: ${newDocNumber}`, 
                            {
                                title: "Berhasil",
                                type: "success",
                            }
                        );
                        console.log('Success notification sent via notification service');
                    } else if (this.displayNotification) {
                        this.displayNotification({
                            title: "Berhasil",
                            message: `Nomor dokumen berhasil digenerate: ${newDocNumber}`,
                            type: "success",
                        });
                        console.log('Success notification sent via displayNotification');
                    } else {
                        alert(`Berhasil: Nomor dokumen berhasil digenerate: ${newDocNumber}`);
                        console.log('Success shown via alert');
                    }
                    
                    this._prevDocumentNumber = newDocNumber;
                } else {
                    console.log('No document number change detected');
                }
            } catch (error) {
                console.error('Error checking document number change:', error);
            }
        }

        return result;
    }
});

console.log('WMR Document Notifier: Patch applied successfully');