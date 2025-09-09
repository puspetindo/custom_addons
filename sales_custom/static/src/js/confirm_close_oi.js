odoo.define('sales_custom.close_oi_confirm', function (require) {
    "use strict";
    const core = require('web.core');
    const Dialog = require('web.Dialog');
    const rpc = require('web.rpc');

    core.action_registry.add('close_oi_confirm_popup', function(params) {
        new Dialog(null, {
            title: 'Konfirmasi Close Order Information',
            size: 'medium',
            $content: $('<div/>').text('Apakah anda yakin untuk close Order Information ini?'),
            buttons: [
                {text: 'Cancel', close: true},
                {
                    text: 'Setuju',
                    classes: 'btn-primary',
                    click: function() {
                        rpc.query({
                            model: 'sales_custom.order_information.close.wizard',
                            method: 'action_confirm_close',
                            args: [
                                params.active_id,
                                params.no_bast,
                                params.tanggal_bast
                            ]
                        }).then(() => {
                            // notifikasi sukses
                            Dialog.alert(null, 'Order Information berhasil di-close!');
                        });
                        this.close();
                    }
                }
            ]
        }).open();
    });
});
