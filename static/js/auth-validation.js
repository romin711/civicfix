function isVisibleField(field) {
    return field && !field.classList.contains('hidden') && field.offsetParent !== null;
}

function getErrorElement(field) {
    if (!field || !field.name) {
        return null;
    }
    return document.querySelector('[data-error-for="' + field.name + '"]');
}

function setFieldError(field, message) {
    var errorElement = getErrorElement(field);
    if (!field) {
        return;
    }

    field.classList.toggle('input-error', Boolean(message));
    if (errorElement) {
        errorElement.textContent = message || '';
    }
}

function validateField(field) {
    if (!field || field.disabled) {
        return true;
    }

    if (!isVisibleField(field) && !field.required) {
        setFieldError(field, '');
        return true;
    }

    var value = (field.value || '').trim();
    var fieldName = field.name || 'This field';

    if (field.required && value === '') {
        setFieldError(field, 'This field is required.');
        return false;
    }

    if (fieldName === 'email') {
        var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (value && !emailPattern.test(value)) {
            setFieldError(field, 'Enter a valid email address.');
            return false;
        }
    }

    if (fieldName === 'mobile') {
        var mobilePattern = /^[789]\d{9}$/;
        if (value && !mobilePattern.test(value)) {
            setFieldError(field, 'Enter a 10-digit mobile number starting with 7, 8, or 9.');
            return false;
        }
    }

    var minLengthAttr = parseInt(field.getAttribute('minlength') || '', 10);
    if (!isNaN(minLengthAttr) && value && value.length < minLengthAttr) {
        setFieldError(field, 'Must be at least ' + minLengthAttr + ' characters.');
        return false;
    }

    if (fieldName === 'otp') {
        var otpPattern = /^\d{6}$/;
        if (value && !otpPattern.test(value)) {
            setFieldError(field, 'Enter a valid 6-digit OTP.');
            return false;
        }
    }

    setFieldError(field, '');
    return true;
}

function bindAuthValidation(form) {
    if (!form || form.dataset.validationBound === 'true') {
        return;
    }
    form.dataset.validationBound = 'true';

    var fields = form.querySelectorAll('input, select, textarea');
    for (var i = 0; i < fields.length; i++) {
        (function (field) {
            field.addEventListener('blur', function () {
                validateField(field);
            });
            field.addEventListener('input', function () {
                if (getErrorElement(field) && getErrorElement(field).textContent) {
                    validateField(field);
                }
            });
        })(fields[i]);
    }

    form.addEventListener('submit', function (event) {
        var isValid = true;
        var firstInvalid = null;

        for (var j = 0; j < fields.length; j++) {
            var field = fields[j];
            var valid = validateField(field);
            if (!valid && !firstInvalid && isVisibleField(field)) {
                firstInvalid = field;
            }
            if (!valid) {
                isValid = false;
            }
        }

        if (!isValid) {
            event.preventDefault();
            if (firstInvalid) {
                firstInvalid.focus();
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    var forms = document.querySelectorAll('form[data-auth-validate]');
    for (var i = 0; i < forms.length; i++) {
        bindAuthValidation(forms[i]);
    }
});
