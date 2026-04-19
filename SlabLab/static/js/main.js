/* ══════════════════════════════════════════════════════════════════════════════
   SLAB LAB — main.js
   Global JavaScript: theme toggle, auto-dismiss alerts, smooth behavior
   ══════════════════════════════════════════════════════════════════════════════ */

$(document).ready(function () {

    // ── Theme Toggle (Dark / Light) ────────────────────────────────────────
    const $html = $('html');
    const $icon = $('#themeIcon');
    const savedTheme = localStorage.getItem('slablab-theme') || 'dark';

    function applyTheme(theme) {
        $html.attr('data-bs-theme', theme);
        if (theme === 'light') {
            $icon.removeClass('bi-moon-stars').addClass('bi-sun-fill');
        } else {
            $icon.removeClass('bi-sun-fill').addClass('bi-moon-stars');
        }
        localStorage.setItem('slablab-theme', theme);
    }

    applyTheme(savedTheme);

    $('#themeToggle').on('click', function () {
        const current = $html.attr('data-bs-theme');
        applyTheme(current === 'dark' ? 'light' : 'dark');
    });


    // ── Auto-dismiss alerts after 5s ───────────────────────────────────────
    setTimeout(function () {
        $('#messageContainer .alert').each(function () {
            var bsAlert = new bootstrap.Alert(this);
            bsAlert.close();
        });
    }, 5000);


    // ── CSRF Token helper for AJAX ─────────────────────────────────────────
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Set CSRF token for all AJAX POST requests
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            }
        }
    });


    // ── Add-to-cart AJAX ───────────────────────────────────────────────────
    $(document).on('submit', '.add-to-cart-form', function (e) {
        e.preventDefault();
        var $form = $(this);
        var $btn = $form.find('button[type="submit"]');
        var origHtml = $btn.html();

        $btn.html('<i class="bi bi-check-lg me-1"></i>Added!').prop('disabled', true);

        $.ajax({
            url: $form.attr('action'),
            type: 'POST',
            data: $form.serialize(),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function (data) {
                if (data.cart_count !== undefined) {
                    var $badge = $('#navCartBadge');
                    if ($badge.length) {
                        $badge.text(data.cart_count);
                    } else {
                        $('#navCartLink').append('<span class="badge-count" id="navCartBadge">' + data.cart_count + '</span>');
                    }
                }
                setTimeout(function () {
                    $btn.html(origHtml).prop('disabled', false);
                }, 1500);
            },
            error: function () {
                $btn.html(origHtml).prop('disabled', false);
            }
        });
    });


    // ── Wishlist toggle AJAX ──────────────────────────────────────────────
    $(document).on('submit', '.wishlist-form', function (e) {
        e.preventDefault();
        var $form = $(this);
        var $btn = $form.find('button');
        var $icon = $btn.find('i');

        $.ajax({
            url: $form.attr('action'),
            type: 'POST',
            data: $form.serialize(),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function (data) {
                if (data.added) {
                    $icon.removeClass('bi-heart').addClass('bi-heart-fill');
                } else {
                    $icon.removeClass('bi-heart-fill').addClass('bi-heart');
                }
            }
        });
    });


    // ── Lazy load images with IntersectionObserver ──────────────────────────
    if ('IntersectionObserver' in window) {
        var lazyImages = document.querySelectorAll('img[loading="lazy"]');
        var imgObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var img = entry.target;
                    img.classList.add('loaded');
                    imgObserver.unobserve(img);
                }
            });
        });
        lazyImages.forEach(function (img) { imgObserver.observe(img); });
    }

});
