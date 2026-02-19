function setGovFieldState(field, isVisible) {
    if (!field) {
        return;
    }

    field.classList.toggle('hidden', !isVisible);
    field.required = isVisible;

    if (!isVisible) {
        field.value = '';
        field.classList.remove('input-error');
    }
}

function setElementVisibility(element, isVisible) {
    if (!element) {
        return;
    }
    element.classList.toggle('hidden', !isVisible);
}

function setOtpStatus(message, type) {
    var otpStatus = document.getElementById('otpStatus');
    if (!otpStatus) {
        return;
    }

    otpStatus.className = 'inline-status';
    if (type) {
        otpStatus.classList.add('status-' + type);
    }
    otpStatus.textContent = message || '';
}

function startOtpCooldown(button, seconds) {
    if (!button) {
        return;
    }

    var remaining = seconds;
    button.disabled = true;
    button.dataset.cooldownActive = 'true';
    button.textContent = 'Resend OTP (' + remaining + 's)';

    var interval = setInterval(function () {
        remaining -= 1;
        if (remaining <= 0) {
            clearInterval(interval);
            button.disabled = false;
            button.dataset.cooldownActive = 'false';
            button.textContent = 'Resend OTP';
            return;
        }
        button.textContent = 'Resend OTP (' + remaining + 's)';
    }, 1000);
}

function toggleGov() {
    var roleField = document.getElementById('role');
    if (!roleField) {
        return;
    }

    var isGovernment = roleField.value === 'government';
    var govIdField = document.getElementById('govId');
    var govDepartmentField = document.getElementById('govDepartment');
    var govIdLabel = document.getElementById('govIdLabel');
    var govDepartmentLabel = document.getElementById('govDepartmentLabel');
    var govIdError = document.querySelector('[data-error-for="gov_id"]');
    var govDepartmentError = document.querySelector('[data-error-for="department"]');

    setGovFieldState(govIdField, isGovernment);
    setGovFieldState(govDepartmentField, isGovernment);
    setElementVisibility(govIdLabel, isGovernment);
    setElementVisibility(govDepartmentLabel, isGovernment);
    setElementVisibility(govIdError, isGovernment);
    setElementVisibility(govDepartmentError, isGovernment);
}

async function generateOTP() {
    var emailField = document.querySelector('input[name="email"]');
    var mobileField = document.querySelector('input[name="mobile"]');
    var otpButton = document.getElementById('otpButton');

    if (!emailField || !mobileField || !otpButton) {
        setOtpStatus('Unable to prepare OTP right now. Please refresh and try again.', 'error');
        return;
    }

    var email = emailField.value.trim();
    var mobile = mobileField.value.trim();
    var mobilePattern = /^[789]\d{9}$/;

    if (!email || !email.includes('@') || !email.includes('.')) {
        setOtpStatus('Enter a valid email before generating OTP.', 'error');
        emailField.focus();
        return;
    }

    if (!mobilePattern.test(mobile)) {
        setOtpStatus('Enter a valid 10-digit mobile number starting with 7, 8, or 9.', 'error');
        mobileField.focus();
        return;
    }

    if (otpButton.dataset.cooldownActive === 'true') {
        return;
    }

    var originalText = otpButton.textContent;
    otpButton.disabled = true;
    otpButton.textContent = 'Generating...';
    setOtpStatus('Requesting OTP...', 'info');

    try {
        var response = await fetch('/generate-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: email,
                mobile: mobile
            })
        });

        var data = await response.json();

        if (!response.ok || !data.ok) {
            setOtpStatus(data.message || 'Validation failed. Please check your details.', 'error');
            otpButton.disabled = false;
            otpButton.textContent = originalText;
            return;
        }

        setOtpStatus('OTP sent. Demo OTP: ' + data.otp, 'success');
        startOtpCooldown(otpButton, 30);
    } catch (error) {
        console.error('Error generating OTP:', error);
        setOtpStatus('Could not generate OTP. Please try again.', 'error');
        otpButton.disabled = false;
        otpButton.textContent = originalText;
    }
}

document.addEventListener('DOMContentLoaded', toggleGov);
