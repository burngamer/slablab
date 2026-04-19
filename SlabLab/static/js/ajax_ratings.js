/* ══════════════════════════════════════════════════════════════════════════════
   SLAB LAB — ajax_ratings.js
   Interactive star rating widget (AJAX)
   ══════════════════════════════════════════════════════════════════════════════ */

$(document).ready(function () {

    var $starInput = $('#starRatingInput');
    var $ratingValue = $('#ratingInput');

    // ── Click on a star ────────────────────────────────────────────────────
    $starInput.on('click', '.star-clickable', function () {
        var value = $(this).data('value');
        $ratingValue.val(value);

        // Update visual state
        $starInput.find('.star-clickable').each(function () {
            var starVal = $(this).data('value');
            if (starVal <= value) {
                $(this).removeClass('bi-star').addClass('bi-star-fill active');
            } else {
                $(this).removeClass('bi-star-fill active').addClass('bi-star');
            }
        });
    });

    // ── Hover preview ──────────────────────────────────────────────────────
    $starInput.on('mouseenter', '.star-clickable', function () {
        var hoverVal = $(this).data('value');
        $starInput.find('.star-clickable').each(function () {
            var starVal = $(this).data('value');
            if (starVal <= hoverVal) {
                $(this).removeClass('bi-star').addClass('bi-star-fill');
            } else {
                $(this).removeClass('bi-star-fill').addClass('bi-star');
            }
        });
    });

    $starInput.on('mouseleave', function () {
        var selected = parseInt($ratingValue.val()) || 0;
        $starInput.find('.star-clickable').each(function () {
            var starVal = $(this).data('value');
            if (starVal <= selected) {
                $(this).removeClass('bi-star').addClass('bi-star-fill active');
            } else {
                $(this).removeClass('bi-star-fill active').addClass('bi-star');
            }
        });
    });

    // ── AJAX submit review ─────────────────────────────────────────────────
    $('#reviewForm').on('submit', function (e) {
        e.preventDefault();

        var rating = $ratingValue.val();
        if (!rating || rating === '0') {
            alert('Please select a star rating.');
            return;
        }

        var $form = $(this);
        var $btn = $form.find('button[type="submit"]');
        $btn.prop('disabled', true).html('<i class="bi bi-hourglass-split me-1"></i>Submitting...');

        $.ajax({
            url: $form.attr('action'),
            type: 'POST',
            data: $form.serialize(),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function (data) {
                if (data.success) {
                    // Build new review HTML
                    var starsHtml = '';
                    for (var i = 1; i <= 5; i++) {
                        starsHtml += i <= data.rating
                            ? '<i class="bi bi-star-fill text-warning"></i>'
                            : '<i class="bi bi-star text-muted"></i>';
                    }

                    var reviewHtml = '<div class="review-item border-bottom border-secondary py-3">' +
                        '<div class="d-flex justify-content-between align-items-start">' +
                        '<div><strong>' + data.username + '</strong>' +
                        '<div class="star-display">' + starsHtml + '</div></div>' +
                        '<small class="text-muted">' + data.created_at + '</small></div>';
                    if (data.comment) {
                        reviewHtml += '<p class="mt-2 mb-0 text-muted">' + data.comment + '</p>';
                    }
                    reviewHtml += '</div>';

                    // Prepend to reviews list
                    var $reviewsList = $('#reviewsList');
                    if ($reviewsList.length) {
                        $reviewsList.prepend(reviewHtml);
                    } else {
                        $('#reviewsSection').append('<div id="reviewsList">' + reviewHtml + '</div>');
                    }

                    // Hide form
                    $form.closest('div').slideUp();

                    // Show success toast
                    showToast('Review submitted! ★');
                }
            },
            error: function (xhr) {
                $btn.prop('disabled', false).html('Submit Review');
                alert('Error submitting review. Please try again.');
            }
        });
    });

    // ── Simple toast notification ──────────────────────────────────────────
    function showToast(message) {
        var $toast = $('<div class="position-fixed bottom-0 end-0 p-3" style="z-index:9999">' +
            '<div class="toast show glass-alert" role="alert">' +
            '<div class="toast-body d-flex align-items-center gap-2">' +
            '<i class="bi bi-check-circle-fill text-success"></i>' + message +
            '</div></div></div>');
        $('body').append($toast);
        setTimeout(function () { $toast.fadeOut(300, function () { $toast.remove(); }); }, 3000);
    }

});
