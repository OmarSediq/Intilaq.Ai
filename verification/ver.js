document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.querySelectorAll('.code-box');
    const resendLink = document.querySelector('.resend-link');
    const emailSpan = document.querySelector('.email');
    let countdownTimer;

    // ✅ جلب البريد الإلكتروني من API عند تحميل الصفحة
    fetchUserEmail();

    async function fetchUserEmail() {
        try {
            const response = await fetch("https://api.example.com/get-user-email", {
                method: "GET",
                credentials: "include",  // 🔹 يدعم الكوكيز بدلاً من LocalStorage
            });

            if (response.ok) {
                const data = await response.json();
                emailSpan.textContent = data.email;
            } else {
                console.error("Failed to fetch email");
            }
        } catch (error) {
            console.error("Error fetching email:", error);
        }
    }

    // ✅ التحكم في التنقل بين مربعات الإدخال والتحقق التلقائي عند إدخال الكود
    inputs.forEach((input, index) => {
        input.addEventListener('input', async () => {
            if (input.value.length > 0 && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }

            const otp = Array.from(inputs).map(input => input.value).join('');
            if (otp.length === inputs.length) {
                await verifyOTP(otp);  // 🔹 إضافة await لضمان انتظار التحقق
            }
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && input.value === '' && index > 0) {
                inputs[index - 1].focus();
            }
        });
    });

    // ✅ دالة التحقق من OTP عبر API
    async function verifyOTP(otp) {
        console.log("Sending OTP:", otp);

        try {
            const response = await fetch("https://api.example.com/verify-otp", {
                method: "POST",
                credentials: "include", // 🔹 دعم الكوكيز
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ otp })
            });

            const data = await response.json();

            if (response.ok) {
                alert("✅ OTP Verified Successfully!");
                window.location.href = "/dashboard"; // ✅ توجيه بعد النجاح
            } else {
                alert("❌ Invalid OTP, please try again.");
                inputs.forEach(input => input.value = "");
                inputs[0].focus();
            }
        } catch (error) {
            console.error("Error:", error);
            alert("⚠ Something went wrong, please try again.");
        }
    }

    // ✅ دالة إعادة إرسال OTP مع عداد تنازلي
    async function resendOTP() {
        try {
            const response = await fetch("https://api.example.com/resend-otp", {
                method: "POST",
                credentials: "include", // 🔹 دعم الكوكيز
                headers: {
                    "Content-Type": "application/json"
                }
            });

            if (response.ok) {
                alert("📩 A new OTP has been sent to your email.");
                startCountdown(30); // 🔹 تشغيل العداد لمدة 30 ثانية
            } else {
                alert("⚠ Failed to resend OTP. Please try again later.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("⚠ Something went wrong, please try again.");
        }
    }

    // ✅ دالة بدء العداد التنازلي
    function startCountdown(seconds) {
        let remainingTime = seconds;
        resendLink.style.pointerEvents = "none";

        countdownTimer = setInterval(() => {
            resendLink.textContent = `Resend in (${remainingTime}s)`;
            remainingTime--;

            if (remainingTime < 0) {
                clearInterval(countdownTimer);
                resendLink.textContent = "Resend";
                resendLink.style.pointerEvents = "auto";
            }
        }, 1000);
    }

    // ✅ تشغيل العداد عند تحميل الصفحة إن كان هناك وقت متبقٍ
    const storedTime = localStorage.getItem("resendTimer");
    if (storedTime && (Date.now() - storedTime) < 30000) {
        startCountdown(30 - Math.floor((Date.now() - storedTime) / 1000));
    }

    // ✅ ربط دالة إعادة الإرسال بزر "Resend"
    resendLink.addEventListener("click", (e) => {
        e.preventDefault();
        localStorage.setItem("resendTimer", Date.now()); // تخزين وقت بدء العداد
        resendOTP();
    });
});
