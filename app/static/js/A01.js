document.addEventListener("DOMContentLoaded", function () {
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');

    const today = new Date().toISOString().split('T')[0];
    startDateInput.setAttribute('max', today);
    endDateInput.setAttribute('max', today);

    startDateInput.addEventListener('change', function () {
        endDateInput.setAttribute('min', this.value);
    });

    endDateInput.setAttribute('min', startDateInput.value);
});