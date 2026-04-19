/* ══════════════════════════════════════════════════════════════════════════════
   SLAB LAB — cart_logic.js
   Client-side cart interactions
   ══════════════════════════════════════════════════════════════════════════════ */

$(document).ready(function () {

    // ── Update cart quantity on change ──────────────────────────────────────
    $(document).on('change', '.cart-qty-select', function () {
        var $select = $(this);
        var url = $select.data('url');
        var quantity = $select.val();
        var $item = $select.closest('.cart-item');

        $.ajax({
            url: url,
            type: 'POST',
            data: { quantity: quantity },
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function (data) {
                if (data.success) {
                    if (quantity <= 0) {
                        $item.fadeOut(300, function () { $(this).remove(); });
                    } else {
                        $item.find('.item-subtotal').text('$' + data.item_subtotal);
                    }
                    // Update totals
                    $('#cartTotal').text('$' + data.cart_total);
                    if (data.cart_count !== undefined) {
                        $('#navCartBadge').text(data.cart_count);
                    }
                }
            }
        });
    });

    // ── Remove item AJAX ──────────────────────────────────────────────────
    $(document).on('submit', '.cart-remove-form', function (e) {
        e.preventDefault();
        var $form = $(this);
        var $item = $form.closest('.cart-item');

        $.ajax({
            url: $form.attr('action'),
            type: 'POST',
            data: $form.serialize(),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function (data) {
                if (data.success) {
                    $item.fadeOut(300, function () { $(this).remove(); });
                    if (data.cart_count !== undefined) {
                        $('#navCartBadge').text(data.cart_count);
                    }
                }
            }
        });
    });

});
