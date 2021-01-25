const form_fields = document.querySelectorAll('input, select, textarea');
const tracker = document.getElementById(document.querySelector('meta[name="notif-changed-element"]').getAttribute('value'))

const listenForFieldChanged = (event) => {
    tracker.style.display = "block";
    event.target.removeEventListener('change', listenForFieldChanged);
}

const colorFormElements = (event) => {
    colorable = event.target.closest('.form-element');
    colorable.style.borderColor = 'var(--color-warning)';
    event.target.removeEventListener('change', colorFormElements);
}

form_fields.forEach(e => {
    e.addEventListener('change', listenForFieldChanged);
    e.addEventListener('change', colorFormElements);
})
