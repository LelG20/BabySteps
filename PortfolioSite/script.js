// Open and close the mobile navigation menu.
const menuButton = document.querySelector("#menu-toggle");
const navigationLinks = document.querySelector("#primary-menu");

function setMenuOpen(isOpen) {
    if (!menuButton || !navigationLinks) {
        return;
    }

    navigationLinks.classList.toggle("is-open", isOpen);
    menuButton.setAttribute("aria-expanded", isOpen);
    menuButton.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
    menuButton.querySelector(".menu-toggle-label").textContent = isOpen ? "Close" : "Menu";
}

if (menuButton && navigationLinks) {
    menuButton.addEventListener("click", function () {
        const menuIsOpen = menuButton.getAttribute("aria-expanded") === "true";
        setMenuOpen(!menuIsOpen);
    });

    navigationLinks.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
            setMenuOpen(false);
        });
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            setMenuOpen(false);
        }
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > 680) {
            setMenuOpen(false);
        }
    });
}

// Show a different beginner-friendly learning tip each time the button is clicked.
const learningTipButton = document.querySelector("#learning-tip-button");
const learningTip = document.querySelector("#learning-tip");
const learningTips = [
    "Build a small project to practise each new HTML or CSS idea.",
    "Use clear names for classes and variables so your code is easier to read.",
    "Test your page on a phone as well as on a desktop.",
    "When something breaks, change one thing at a time and test again."
];
let nextTipIndex = 0;

function showNextLearningTip() {
    if (!learningTip) {
        return;
    }

    learningTip.textContent = learningTips[nextTipIndex];
    learningTip.hidden = false;
    nextTipIndex = (nextTipIndex + 1) % learningTips.length;
}

if (learningTipButton) {
    learningTipButton.addEventListener("click", showNextLearningTip);
}

// Check required fields and the email format before sending the form to PHP.
const contactForm = document.querySelector("#contact-form");
const formStatus = document.querySelector("#form-status");

function validateContactForm(event) {
    const requiredFields = contactForm.querySelectorAll("[required]");
    let firstEmptyField = null;

    requiredFields.forEach(function (field) {
        field.removeAttribute("aria-invalid");

        if (!field.value.trim() && !firstEmptyField) {
            firstEmptyField = field;
        }
    });

    if (firstEmptyField) {
        event.preventDefault();
        firstEmptyField.setAttribute("aria-invalid", "true");
        formStatus.textContent = "Please complete all required fields.";
        firstEmptyField.focus();
        return;
    }

    const emailField = contactForm.querySelector("#contact-email");
    if (!emailField.checkValidity()) {
        event.preventDefault();
        emailField.setAttribute("aria-invalid", "true");
        formStatus.textContent = "Please enter a valid email address.";
        emailField.focus();
        return;
    }

    formStatus.textContent = "";
}

if (contactForm && formStatus) {
    contactForm.addEventListener("submit", validateContactForm);

    contactForm.addEventListener("input", function (event) {
        event.target.removeAttribute("aria-invalid");
        formStatus.textContent = "";
    });
}
