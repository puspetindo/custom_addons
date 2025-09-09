odoo.define('sales_custom.scope_division', function (require) {
"use strict";

var ListRenderer = require('web.ListRenderer');
var Dialog = require('web.Dialog');
var core = require('web.core');
var _t = core._t;

ListRenderer.include({
    _onCellClicked: function (event) {
        console.log("Cell clicked - Start processing"); // DEBUG 1
        
        var self = this;
        var $cell = $(event.currentTarget);
        var fieldName = $cell.data('name');
        var recordId = $cell.closest('tr').data('id');
        
        console.log("Field:", fieldName, "Record ID:", recordId); // DEBUG 2

        if (fieldName === 'detail_scope' || fieldName === 'division') {
            event.stopPropagation();
            event.preventDefault();
            
            console.log("Valid field - Checking checkbox status"); // DEBUG 3
            
            this._rpc({
                model: 'sales_custom.scope_division',
                method: 'read',
                args: [[recordId], ['is_checked']],
            }).then(function(result) {
                console.log("RPC Result:", result); // DEBUG 4
                
                // Auto-check the box if not checked
                if (result.length > 0 && !result[0].is_checked) {
                    self._rpc({
                        model: 'sales_custom.scope_division',
                        method: 'write',
                        args: [[recordId], {'is_checked': true}],
                    }).then(function() {
                        console.log("Checkbox auto-checked");
                        self._openEditor(recordId, fieldName);
                    });
                } else if (result.length > 0 && result[0].is_checked) {
                    console.log("Checkbox active - Opening editor"); // DEBUG 5
                    self._openEditor(recordId, fieldName);
                } else {
                    console.log("Checkbox inactive - Showing warning"); // DEBUG 6
                    self.do_warn(_t("Warning"), _t("Please check the box first!"));
                }
            }).catch(function(error) {
                console.error("RPC Error:", error); // DEBUG 7
            });
            
            return;
        }
        return this._super.apply(this, arguments);
    },

    _openEditor: function(recordId, fieldName) {
        console.log("Opening editor for", fieldName); // DEBUG 8
        
        var self = this;
        var popupTitle = fieldName === 'detail_scope' ? 
            _t("Edit Detail Scope") : 
            _t("Edit Remarks");

        this._rpc({
            model: 'sales_custom.scope_division',
            method: 'read',
            args: [[recordId], [fieldName]],
        }).then(function(result) {
            console.log("Current value:", result[0][fieldName]); // DEBUG 9
            
            new Dialog(self, {
                title: popupTitle,
                $content: $('<div>').append(
                    $('<textarea>')
                        .css({'width':'100%', 'height':'200px'})
                        .val(result[0][fieldName] || '')
                        .on('click', function(e) { e.stopPropagation(); })
                ),
                buttons: [{
                    text: _t("Save"),
                    classes: 'btn-primary',
                    click: function() {
                        console.log("Saving value..."); // DEBUG 10
                        self._rpc({
                            model: 'sales_custom.scope_division',
                            method: 'write',
                            args: [[recordId], {
                                [fieldName]: this.$('textarea').val()
                            }],
                        }).then(function() {
                            console.log("Value saved"); // DEBUG 11
                            self.trigger_up('reload');
                        });
                    }
                }, {
                    text: _t("Cancel"),
                    close: true
                }]
            }).open();
        });
    }
});
});
