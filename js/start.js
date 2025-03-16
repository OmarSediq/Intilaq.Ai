function selectOption(option) {
    document.querySelectorAll('.option').forEach(opt => opt.classList.remove('active'));
    option.classList.add('active');
}
// Get all checkboxes with the class 'single-choice'
const checkboxes = document.querySelectorAll('.single-choice');

// Add an event listener to each checkbox
checkboxes.forEach(checkbox => {
checkbox.addEventListener('change', () => {
// Uncheck all other checkboxes
checkboxes.forEach(cb => {
if (cb !== checkbox) {
    cb.checked = false;
}
});
});
});