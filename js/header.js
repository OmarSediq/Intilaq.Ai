document.addEventListener('DOMContentLoaded', () => {
  const steps = document.querySelectorAll('.step');
  const circles = document.querySelectorAll('.circle');
  const descriptions = document.querySelectorAll('.step-description');
  const verticalLine = document.querySelector('.vertical-line');
  // const prevBtn = document.getElementById('prevBtn');
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
    verticalLine.style.background = `linear-gradient(to bottom, #002465 ${activeHeight}%, #ccc ${activeHeight}%)`;

    // Button states
    prevBtn.disabled = currentStep === 0;
    nextBtn.disabled = currentStep === steps.length - 1;
  }

  nextBtn.addEventListener('click', () => {
    if (currentStep < steps.length - 1) {
      currentStep++;
      updateSteps();
    }
  });

  prevBtn.addEventListener('click', () => {
    if (currentStep > 0) {
      currentStep--;
      updateSteps();
    }
  });

  updateSteps();
});

function changeStep(step) {
  // Remove "active" class from all steps and content
  const allSteps = document.querySelectorAll(".step");
  const allContents = document.querySelectorAll(".content");

  allSteps.forEach((s) => s.classList.remove("active"));
  allContents.forEach((c) => c.classList.remove("active"));

  // Add "active" class to the selected step and corresponding content
  document.getElementById(`step-${step}-btn`).classList.add("active");
  document.getElementById(`step-${step}-content`).classList.add("active");
}

document.addEventListener('click', function (event) {
  // Check if the clicked element has the class 'add-btn'
  if (event.target.classList.contains('add-btn')) {
    // Prevent any default actions or bubbling issues
    event.preventDefault();

    const button = event.target;

    // Ensure the clicked element is indeed a button before proceeding
    if (button.tagName === 'BUTTON') {
      // Find the closest parent with the 'info-box' class
      const parentBox = button.closest('.info-box');

      // Ensure the parent box and its elements exist to prevent errors
      if (parentBox) {
        const inputContainer = parentBox.querySelector('.input-container');
        const labelSpan = parentBox.querySelector('span');

        if (inputContainer && labelSpan) {
          // Create a new input box
          const newInput = document.createElement('input');
          newInput.type = 'text';
          newInput.placeholder = `Enter ${labelSpan.textContent}`;
          newInput.classList.add('info-input');
          newInput.style.fontSize = '13px';
          newInput.style.width = '740px';
          newInput.style.height = '38px';
          newInput.style.border = '1px';
          newInput.style.borderRadius = '8px';
          newInput.style.padding = '8px';
          newInput.style.marginBottom = '20px';
          newInput.style.top = '1px';
          newInput.style.backgroundColor = 'var(--GreyTint-GreyShade, #F9F9F9)';
          

          // Append the new input to the container
          inputContainer.appendChild(newInput);

          // Hide the "+" button
          button.style.display = 'none';
        }
      }
    }
  }
  document.querySelector('.dynamic-inputs').appendChild(newInput);
});



document.querySelector('.edit-btn').addEventListener('click', function (event) {
  event.preventDefault(); // Prevent page reload or default button action
  
  const inputField = document.querySelector('#nameInput');

  if (inputField.hasAttribute('readonly')) {
    // Enable editing mode
    inputField.removeAttribute('readonly');
    inputField.focus(); // Focus on the input box
    inputField.style.border = '1px solid #ccc'; // Optional: Add visual indication of editing mode
  } else {
    // Disable editing mode
    inputField.setAttribute('readonly', true);
    inputField.style.border = 'none'; // Optional: Revert visual indication
  }
});

document.querySelector('.edit-btn2').addEventListener('click', function (event) {
  event.preventDefault(); // Prevent page reload or default button action
  
  const inputField = document.querySelector('#emailInput');

  if (inputField.hasAttribute('readonly')) {
    // Enable editing mode
    inputField.removeAttribute('readonly');
    inputField.focus(); // Focus on the input box
    inputField.style.border = '1px solid #ccc'; // Optional: Add visual indication of editing mode
  } else {
    // Disable editing mode
    inputField.setAttribute('readonly', true);
    inputField.style.border = 'none'; // Optional: Revert visual indication
  }
});


function addInput(containerId) {
  let container = document.getElementById(containerId);

  let newInput = document.createElement("input");
  newInput.type = "text";
  newInput.placeholder = "Enter " + (containerId.includes("portfolio") ? "Portfolio" : "GitHub") + " URL";
  newInput.className = "input-field";

  container.appendChild(newInput);
}

function nextStep(url) {
  window.location.href = url;
}


