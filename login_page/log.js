document.addEventListener("DOMContentLoaded", function () {
    const togglePassword = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("password");
    const loginForm = document.querySelector("form");
  
    if (togglePassword) {
      togglePassword.addEventListener("click", function () {
        const isPassword = passwordInput.getAttribute("type") === "password";
        passwordInput.setAttribute("type", isPassword ? "text" : "password");
        this.classList.toggle("fa-eye-slash", isPassword);
        this.classList.toggle("fa-eye", !isPassword);
      });
    }
  
    loginForm.addEventListener("submit", async function (event) {
      event.preventDefault();
  
      const email = document.getElementById("Email").value.trim();
      const password = passwordInput.value.trim();
  
      if (!email || !password) {
        alert("❌ الرجاء إدخال البريد الإلكتروني وكلمة المرور.");
        return;
      }
  
      const loginData = { email, password };
      const API_URL ="https://revolution-sent-ratings-enabling.trycloudflare.com/api/auth/login/";
  
      try {
        const response = await fetch("https://revolution-sent-ratings-enabling.trycloudflare.com/api/auth/login/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(loginData),
          credentials: "include", // ✅ يسمح بإرسال واستقبال الكوكيز بين السيرفر والمتصفح
        });
  
        if (response.ok) {
          alert("✅ تسجيل الدخول ناجح!");
          window.location.href = "dashboard.html"; // تحويل المستخدم للوحة التحكم
        } else {
          const result = await response.json();
          alert("❌ فشل تسجيل الدخول: " + (result.detail || "حدث خطأ غير معروف"));
        }
      } catch (error) {
        alert("❌ تعذر الاتصال بالخادم!");
        console.error("خطأ:", error);
      }
    });
  });
  