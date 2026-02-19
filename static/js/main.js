document.addEventListener('DOMContentLoaded', function () {
    var messages = document.querySelectorAll('.flash-message');
    for (var i = 0; i < messages.length; i++) {
        (function (message) {
            setTimeout(function () {
                message.style.opacity = '0';
                setTimeout(function () {
                    message.remove();
                }, 300);
            }, 5000);
        })(messages[i]);
    }
});
