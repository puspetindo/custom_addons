/** @odoo-module **/

import FormController from 'web.FormController';
import Dialog from 'web.Dialog';

const RevisionConfirmFormController = FormController.extend({
    async _onSave(ev) {
        const record = this.model.get(this.handle);
        if (record && record.data.id) {  // existing record
            const confirmed = await new Promise((resolve) => {
                this.trigger_up('dialog', {
                    dialogClass: Dialog,
                    title: 'Confirm Revision',
                    size: 'medium',
                    buttons: [
                        {
                            text: 'Yes',
                            classes: 'btn-primary',
                            close: true,
                            click: () => resolve(true),
                        },
                        {
                            text: 'No',
                            close: true,
                            click: () => resolve(false),
                        },
                    ],
                    $content: $('<div>').text('Are you sure you want to make a revision?'),
                });
            });
            if (!confirmed) {
                ev.preventDefault();
                return;
            }
            // User clicked Yes, set revision_confirmed flag before save
            await this.model.update(this.handle, {revision_confirmed: true});
        }
        return this._super(ev);
    },
});

export default {
    FormController: RevisionConfirmFormController,
};
