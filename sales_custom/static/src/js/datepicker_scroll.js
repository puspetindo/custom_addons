/** @odoo-module **/

import { registry } from "@web/core/registry";

// Patch global bootstrap datepicker agar bisa scroll bulan dengan mousewheel
function enableDatepickerScroll() {
    $(document).on('mousewheel DOMMouseScroll', '.datepicker-days', function (e) {
        e.preventDefault();
        const ev = e.originalEvent;
        const delta = ev.wheelDelta || -ev.detail;

        // Cari tombol prev/next
        if (delta > 0) {
            $(this).find('.prev').trigger('click'); // scroll up → bulan sebelumnya
        } else {
            $(this).find('.next').trigger('click'); // scroll down → bulan berikutnya
        }
    });
}

// Jalankan ketika webclient sudah siap
registry.category("web_tour.tours").add("datepicker_scroll_patch", {
    steps: () => [{ trigger: "body", run: enableDatepickerScroll }],
});
