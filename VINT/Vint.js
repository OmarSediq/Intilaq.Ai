// جلب عناصر أزرار اللغة
const englishBtn = document.getElementById("englishBtn");
const arabicBtn = document.getElementById("arabicBtn");
const formElements = document.querySelectorAll("#jobTitle, #jobLevel, #jobDescription, #startBtn, #submitBtn");
const modalOverlay = document.getElementById("modalOverlay");
const closeModal = document.getElementById("closeModal");
const pages = document.querySelectorAll(".modal-page");
const dots = document.querySelectorAll(".pagination .dot");
let currentPage = 0;

// تمكين الحقول عند اختيار اللغة
function enableForm() {
    formElements.forEach(el => el.disabled = false);
}

// وظيفة لتحديث واجهة الأزرار بناءً على اللغة المختارة
function updateLanguageUI(selectedLang) {
    enableForm();
    if (selectedLang === "en") {
        englishBtn.classList.add("active");
        englishBtn.style.background = "gray";
        arabicBtn.classList.remove("active");
        arabicBtn.style.background = "transparent";
    } else {
        arabicBtn.classList.add("active");
        arabicBtn.style.background = "gray";
        englishBtn.classList.remove("active");
        englishBtn.style.background = "transparent";
    }
}

// عند الضغط على زر الإنجليزية
englishBtn.addEventListener("click", function () {
    updateLanguageUI("en");
    openModal(); // فتح النافذة المنبثقة بعد اختيار اللغة
});

// عند الضغط على زر العربية
arabicBtn.addEventListener("click", function () {
    updateLanguageUI("ar");
    openModal(); // فتح النافذة المنبثقة بعد اختيار اللغة
});

// عند تحميل الصفحة، إزالة التحديد من الأزرار وتعطيل الحقول
document.addEventListener("DOMContentLoaded", function () {
    englishBtn.classList.remove("active");
    englishBtn.style.background = "transparent";
    arabicBtn.classList.remove("active");
    arabicBtn.style.background = "transparent";
    formElements.forEach(el => el.disabled = true);
});

// زر تشغيل التسجيل الصوتي
document.getElementById("startBtn").addEventListener("click", function () {
    alert("Voice recording started...");
});

// زر إرسال النموذج
document.getElementById("submitBtn").addEventListener("click", function () {
    let jobTitle = document.getElementById("jobTitle").value;
    let jobLevel = document.getElementById("jobLevel").value;
    let jobDescription = document.getElementById("jobDescription").value;

    if (jobTitle && jobLevel && jobDescription) {
        alert("Form Submitted Successfully!");
    } else {
        alert("Please fill in all required fields.");
    }
});

// إظهار الصفحة الحالية وتحديث النقاط
function showPage(index) {
    pages.forEach((page, i) => {
        page.classList.toggle("active", i === index);
    });

    dots.forEach((dot, i) => {
        dot.classList.toggle("active", i === index);
    });

    currentPage = index;
}

// فتح النافذة بعد اختيار اللغة
function openModal() {
    modalOverlay.classList.add("active");
    showPage(0);
}

// إغلاق النافذة
function closeModalFunc() {
    modalOverlay.classList.remove("active");
}

// إغلاق النافذة عند الضغط على زر الإغلاق
closeModal.addEventListener("click", closeModalFunc);

// التحكم في التنقل بين الصفحات وتحديث النقاط
document.getElementById("next1").addEventListener("click", () => showPage(1));
document.getElementById("back1").addEventListener("click", () => showPage(0));
document.getElementById("next2").addEventListener("click", () => showPage(2));
document.getElementById("back2").addEventListener("click", () => showPage(1));

// عند الضغط على "Finish" يتم الإغلاق
document.getElementById("finish").addEventListener("click", closeModalFunc);

// إغلاق النافذة عند الضغط خارجها
modalOverlay.addEventListener("click", (event) => {
    if (event.target === modalOverlay) {
        closeModalFunc();
    }
});
