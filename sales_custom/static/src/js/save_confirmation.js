/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";

class ConfirmSaveController extends FormController {
    async saveRecord() {
        if (this.props.resModel === "sales_custom.order_information") {
            const confirmed = await this.dialogService.confirm("Yakin ingin menyimpan data ini?");
            if (!confirmed) {
                return Promise.reject("Simpan dibatalkan");
            }
        }
        return super.saveRecord();
    }
}

registry.category("views").add("form", {
    ...registry.category("views").get("form"),
    Controller: ConfirmSaveController,
});
