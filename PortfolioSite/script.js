// querySelector finds the first page element with the matching ID.
const menuButton = document.querySelector("#menu-toggle");
const navigationLinks = document.querySelector("#primary-menu");

// Keep the menu's visual state and accessibility labels in sync.
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
    // Listen for a click and switch to the opposite open/closed state.
    menuButton.addEventListener("click", function () {
        const menuIsOpen = menuButton.getAttribute("aria-expanded") === "true";
        setMenuOpen(!menuIsOpen);
    });

    // Close the menu after a visitor chooses a navigation link.
    navigationLinks.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
            setMenuOpen(false);
        });
    });

    // Escape is a quick keyboard way to close the open menu.
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

// Store several tips in an array; the index chooses which one to show next.
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
    // Remainder (%) wraps the index back to zero after the last tip.
    nextTipIndex = (nextTipIndex + 1) % learningTips.length;
}

if (learningTipButton) {
    learningTipButton.addEventListener("click", showNextLearningTip);
}

// Check required fields and email format before the browser sends the form to PHP.
const contactForm = document.querySelector("#contact-form");
const formStatus = document.querySelector("#form-status");

function validateContactForm(event) {
    // Select only inputs marked required; the optional subject is skipped.
    const requiredFields = contactForm.querySelectorAll("[required]");
    let firstEmptyField = null;

    requiredFields.forEach(function (field) {
        field.removeAttribute("aria-invalid");

        if (!field.value.trim() && !firstEmptyField) {
            firstEmptyField = field;
        }
    });

    if (firstEmptyField) {
        // Stop submission so the visitor can fix the first missing value.
        event.preventDefault();
        firstEmptyField.setAttribute("aria-invalid", "true");
        formStatus.textContent = "Please complete all required fields.";
        firstEmptyField.focus();
        return;
    }

    const emailField = contactForm.querySelector("#contact-email");
    if (!emailField.checkValidity()) {
        // type="email" gives the browser a built-in email format check.
        event.preventDefault();
        emailField.setAttribute("aria-invalid", "true");
        formStatus.textContent = "Please enter a valid email address.";
        emailField.focus();
        return;
    }

    formStatus.textContent = "";
}

if (contactForm && formStatus) {
    // A valid form continues to contact.php; invalid data stays on this page.
    contactForm.addEventListener("submit", validateContactForm);

    contactForm.addEventListener("input", function (event) {
        event.target.removeAttribute("aria-invalid");
        formStatus.textContent = "";
    });
}
