document.getElementById('togglePassword').addEventListener('click', function () {
    const passwordInput = document.getElementById('password');
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);
  
    // تبديل الأيقونة
    this.classList.toggle('fa-eye');
    this.classList.toggle('fa-eye-slash');
  });
  