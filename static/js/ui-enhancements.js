// ===================================
// UI ENHANCEMENTS - SIMPLE JAVASCRIPT
// ===================================

document.addEventListener('DOMContentLoaded', function () {
    var flashMessages = document.querySelectorAll('.flash-message');
    for (var i = 0; i < flashMessages.length; i++) {
        hideFlashMessage(flashMessages[i]);
    }

    var currentPath = window.location.pathname;
    var navLinks = document.querySelectorAll('.nav-link');
    for (var j = 0; j < navLinks.length; j++) {
        if (navLinks[j].getAttribute('href') === currentPath) {
            navLinks[j].classList.add('active');
        }
    }

    setupImageLightbox();
    setupFormLoading();
});

function hideFlashMessage(msg) {
    if (!msg) {
        return;
    }

    setTimeout(function () {
        msg.classList.add('hiding');
        setTimeout(function () {
            msg.remove();
        }, 300);
    }, 5000);
}

// ===================================
// IMAGE LIGHTBOX
// ===================================
function setupImageLightbox() {
    var images = document.querySelectorAll('.issue-image');
    if (!images.length) {
        return;
    }

    var lightbox = document.getElementById('lightbox');
    if (!lightbox) {
        lightbox = document.createElement('div');
        lightbox.className = 'lightbox';
        lightbox.id = 'lightbox';
        lightbox.innerHTML = '<div class="lightbox-content">' +
            '<button class="lightbox-close" onclick="closeLightbox()">×</button>' +
            '<img class="lightbox-image" id="lightbox-img" src="" alt="Full size image">' +
            '</div>';
        document.body.appendChild(lightbox);

        lightbox.addEventListener('click', function (e) {
            if (e.target === lightbox) {
                closeLightbox();
            }
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closeLightbox();
            }
        });
    }

    for (var i = 0; i < images.length; i++) {
        addImageClickHandler(images[i]);
    }
}

function addImageClickHandler(img) {
    if (!img || img.dataset.lightboxBound === 'true') {
        return;
    }

    img.dataset.lightboxBound = 'true';
    img.addEventListener('click', function () {
        openLightbox(img.src);
    });
}

function openLightbox(imageSrc) {
    var lightbox = document.getElementById('lightbox');
    var lightboxImg = document.getElementById('lightbox-img');

    if (!lightbox || !lightboxImg) {
        return;
    }

    lightboxImg.src = imageSrc;
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    var lightbox = document.getElementById('lightbox');
    if (!lightbox) {
        return;
    }

    lightbox.classList.remove('active');
    document.body.style.overflow = '';
}

// ===================================
// FORM LOADING STATES
// ===================================
function setupFormLoading() {
    var forms = document.querySelectorAll('form');
    for (var i = 0; i < forms.length; i++) {
        addFormSubmitHandler(forms[i]);
    }
}

function addFormSubmitHandler(form) {
    if (!form || form.dataset.loadingBound === 'true') {
        return;
    }

    form.dataset.loadingBound = 'true';
    form.addEventListener('submit', function () {
        var submitButton = form.querySelector('button[type="submit"]');
        if (submitButton && !submitButton.classList.contains('loading')) {
            submitButton.classList.add('loading');
            submitButton.disabled = true;

            if (!submitButton.dataset.originalText) {
                submitButton.dataset.originalText = submitButton.textContent;
            }
            submitButton.textContent = 'Processing...';
        }
    });
}

window.addEventListener('scroll', function () {
    var scrollBtn = document.getElementById('scroll-top-btn');
    if (!scrollBtn) {
        return;
    }

    scrollBtn.style.display = window.scrollY > 300 ? 'flex' : 'none';
});
