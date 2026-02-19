function bindStatusForm(form) {
    if (!form || form.dataset.bound === 'true') {
        return;
    }
    form.dataset.bound = 'true';

    var select = form.querySelector('select[name="status"]');
    var submitButton = form.querySelector('button[type="submit"]');
    if (!select || !submitButton) {
        return;
    }

    function syncButtonState() {
        var currentStatus = select.dataset.currentStatus || '';
        var hasChanged = select.value !== currentStatus;
        submitButton.disabled = !hasChanged;
        submitButton.textContent = hasChanged ? 'Update' : 'No Change';
    }

    select.addEventListener('change', syncButtonState);
    form.addEventListener('submit', function (event) {
        if (submitButton.disabled) {
            event.preventDefault();
        }
    });

    syncButtonState();
}

document.addEventListener('DOMContentLoaded', function () {
    var forms = document.querySelectorAll('.status-form');
    for (var i = 0; i < forms.length; i++) {
        bindStatusForm(forms[i]);
    }
});
