document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirmPassword");
    const togglePassword = document.getElementById("togglePassword");
    const toggleConfirmPassword = document.getElementById("toggleConfirmPassword");
    const registerBtn = document.querySelector(".login-btn");
  
    function togglePasswordVisibility(input, toggleIcon) {
        if (input.type === "password") {
            input.type = "text";
            toggleIcon.classList.remove("fa-eye-slash");
            toggleIcon.classList.add("fa-eye");
        } else {
            input.type = "password";
            toggleIcon.classList.remove("fa-eye");
            toggleIcon.classList.add("fa-eye-slash");
        }
    }
  
    togglePassword.addEventListener("click", function () {
        togglePasswordVisibility(passwordInput, togglePassword);
    });
  
    toggleConfirmPassword.addEventListener("click", function () {
        togglePasswordVisibility(confirmPasswordInput, toggleConfirmPassword);
    });
  
    registerBtn.addEventListener("click", async function () {
        const username = document.getElementById("Username").value.trim();
        const email = document.getElementById("Email").value.trim();
        const password = passwordInput.value.trim();
        const confirmPassword = confirmPasswordInput.value.trim();
  
        if (!username || !email || !password || !confirmPassword) {
            alert("Please fill in all fields.");
            return;
        }
  
        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }
  
        const userData = {
            username: username,
            email: email,
            password: password,
            confirm_password: confirmPassword
        };
  
        try {
            const response = await fetch("https://worse-mg-showed-beans.trycloudflare.com/api/users/register/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(userData)
            });
  
            const result = await response.json();
  
            if (response.ok) {
                sessionStorage.setItem("userEmail", email); // حفظ الإيميل مؤقتًا لاستخدامه في صفحة التحقق
                alert("Account created successfully!");
                window.location.href = "ver.html"; // التوجيه إلى صفحة OTP
            } else {
                alert(`Error: ${result.detail || "Failed to create account"}`);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Something went wrong. Please try again.");
        }
    });
  });
  