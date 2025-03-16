document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ JavaScript Loaded Successfully!');

    const steps = document.querySelectorAll('.step');
    const circles = document.querySelectorAll('.circle');
    const descriptions = document.querySelectorAll('.step-description');
    const verticalLine = document.querySelector('.vertical-line');
    const prevBtn = document.getElementById('prevBtn'); // Make sure this exists
    const nextBtn = document.getElementById('nextBtn');

    let currentStep = 0;

    function updateSteps() {
        steps.forEach((step, index) => {
            const circle = circles[index];
            const description = descriptions[index];

            if (index < currentStep) {
                circle.classList.add('active', 'completed');
                description.classList.add('active');
            } else if (index === currentStep) {
                circle.classList.add('active');
                circle.classList.remove('completed');
                description.classList.add('active');
            } else {
                circle.classList.remove('active', 'completed');
                description.classList.remove('active');
            }
        });

        // Update vertical line
        const activeHeight = (currentStep / (steps.length - 1)) * 100;
        if (verticalLine) {
            verticalLine.style.background = `linear-gradient(to bottom, #002465 ${activeHeight}%, #ccc ${activeHeight}%)`;
        }

        // Button states
        if (prevBtn) prevBtn.disabled = currentStep === 0;
        if (nextBtn) nextBtn.disabled = currentStep === steps.length - 1;
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentStep < steps.length - 1) {
                currentStep++;
                updateSteps();
            }
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentStep > 0) {
                currentStep--;
                updateSteps();
            }
        });
    }

    updateSteps();
});

// Function to change active step
function changeStep(step) {
    const allSteps = document.querySelectorAll(".step");
    const allContents = document.querySelectorAll(".content");

    allSteps.forEach((s) => s.classList.remove("active"));
    allContents.forEach((c) => c.classList.remove("active"));

    document.getElementById(`step-${step}-btn`).classList.add("active");
    document.getElementById(`step-${step}-content`).classList.add("active");
}

// Function to add dynamic input field
document.addEventListener('click', function (event) {
    if (event.target.classList.contains('add-btn')) {
        event.preventDefault();

        const button = event.target;
        const parentBox = button.closest('.info-box');

        if (parentBox) {
            const inputContainer = parentBox.querySelector('.input-container');
            const labelSpan = parentBox.querySelector('span');

            if (inputContainer && labelSpan) {
                const newInput = document.createElement('input');
                newInput.type = 'text';
                newInput.placeholder = `Enter ${labelSpan.textContent}`;
                newInput.classList.add('info-input');

                Object.assign(newInput.style, {
                    fontSize: '13px',
                    width: '740px',
                    height: '38px',
                    border: '1px solid #ccc',
                    borderRadius: '8px',
                    padding: '8px',
                    marginBottom: '20px',
                    backgroundColor: 'var(--GreyTint-GreyShade, #F9F9F9)'
                });

                inputContainer.appendChild(newInput);
                button.style.display = 'none';
            }
        }
    }
});

// Function to toggle sections
function toggleSection(sectionId) {
    let content = document.getElementById(sectionId);
    if (!content) return;

    let icon = content.previousElementSibling.querySelector(".toggle-icon");

    if (content.style.display === "block") {
        content.style.display = "none";
        icon.textContent = "+";
    } else {
        content.style.display = "block";
        icon.textContent = "-";
    }
}

document.getElementById("drop-area").addEventListener("click", function() {
    document.getElementById("file-input").click();
});

document.getElementById("file-input").addEventListener("change", function(event) {
    if (event.target.files.length > 0) {
        alert("File Selected: " + event.target.files[0].name);
    }
});

// Function to toggle between Upload Certification & Add Link
function toggleCertifications() {
    let uploadSection = document.getElementById("upload-section");
    let linkSection = document.getElementById("link-section");

    if (uploadSection.style.display === "none") {
        uploadSection.style.display = "block";
        linkSection.style.display = "none";
    } else {
        uploadSection.style.display = "none";
        linkSection.style.display = "block";
    }
}

// Ensure Upload section is visible by default and Link section is hidden
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("upload-section").style.display = "block";
    document.getElementById("link-section").style.display = "none";
});


const uploadArea = document.getElementById("drop-area");
const fileInput = document.getElementById("file-input");
const progressBarContainer = document.getElementById("progress-bar-container");
const progressBar = document.getElementById("progress-bar");
const completionText = document.getElementById("completion-text");

uploadArea.addEventListener("click", function () {
    fileInput.click();
});

fileInput.addEventListener("change", function (event) {
    if (event.target.files.length > 0) {
        simulateUpload();
    }
});

function simulateUpload() {
    progressBarContainer.style.display = "block";
    completionText.style.display = "none";
    progressBar.style.width = "0%";

    let progress = 0;
    const interval = setInterval(() => {
        if (progress >= 100) {
            clearInterval(interval);
            completionText.style.display = "block";
        } else {
            progress += 10;
            progressBar.style.width = progress + "%";
        }
    }, 300);
}

// Rich Text Editor Functionality
document.addEventListener("DOMContentLoaded", () => {
    const textArea = document.getElementById("text-area");

    function applyStyle(command, value = null) {
        document.execCommand(command, false, value);
        textArea.focus();
    }

    document.getElementById("bold-button")?.addEventListener("click", () => {
        applyStyle("bold");
    });

    document.getElementById("italic-button")?.addEventListener("click", () => {
        applyStyle("italic");
    });

    document.getElementById("unordered-list")?.addEventListener("click", () => {
        applyStyle("insertUnorderedList");
    });

    document.getElementById("ordered-list")?.addEventListener("click", () => {
        applyStyle("insertOrderedList");
    });

    document.getElementById("font-size")?.addEventListener("change", (e) => {
        applyStyle("fontSize", "4");
        document.querySelectorAll("#text-area *").forEach(el => {
            if (el.nodeName === "FONT") el.removeAttribute("size");
            el.style.fontSize = e.target.value;
        });
    });

    textArea?.addEventListener("focus", () => {
        if (textArea.textContent === "Select From AI Recommendations...") {
            textArea.textContent = "";
        }
    });

    textArea?.addEventListener("blur", () => {
        if (textArea.textContent.trim() === "") {
            textArea.textContent = "Select From AI Recommendations...";
        }
    });
});



