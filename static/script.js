function togglePassword(fieldId) {
    const input = document.getElementById(fieldId);
    const icon = document.getElementById('eye-' + fieldId);
    if (input.type === 'password') {
        input.type = 'text';
        icon.setAttribute('data-lucide', 'eye-off');
    } else {
        input.type = 'password';
        icon.setAttribute('data-lucide', 'eye');
    }
    lucide.createIcons();
}

const slider = document.getElementById("securityRange");
const text = document.getElementById("scoreText");
if (slider && text) {
    let score = Number(slider.dataset.score || 0);
    function updateSlider(score) {
        let color = "";
        if (score < 40) color = "#ef4444";
        else if (score < 70) color = "#facc15";
        else if (score < 85) color = "#22c55e";
        else color = "#00c896";
        slider.style.background =
            `linear-gradient(to right, ${color} 0%, ${color} ${score}%, #2a355a ${score}%, #2a355a 100%)`;

        text.innerText = score + "%";
    }
    updateSlider(score);
}

const select = document.getElementById("vaultType");
const makeCard = document.querySelector(".make");
const forms = {
    password: document.getElementById("passwordForm"),
    card: document.getElementById("cardForm"),
    note: document.getElementById("noteForm"),
    api: document.getElementById("apiForm")
};
select.addEventListener("change", () => {
    makeCard.classList.add("expanded");
    Object.values(forms).forEach(form => {
        form.classList.remove("active");
    });
    if (forms[select.value]) {
        forms[select.value].classList.add("active");
    }
});

function enableEdit(id) {
    const input = document.getElementById(id);
    if (!input) return;
    input.removeAttribute("readonly");
    input.focus();
    input.select();
}

function openPopup() {
    document.getElementById("overlay").style.display = "block";
    document.getElementById("popup").style.display = "block";
}
function closePopup() {
    document.getElementById("overlay").style.display = "none";
    document.getElementById("popup").style.display = "none";
}
function openLearnPopup() {
    document.getElementById("overlay").style.display = "block";
    document.getElementById("learnPopup").style.display = "block";
}
function closeLearnPopup() {
    document.getElementById("overlay").style.display = "none";
    document.getElementById("learnPopup").style.display = "none";
}
const popup = document.getElementById("learnPopup");

if (popup) {
    popup.addEventListener("mousemove", (e) => {
        const rect = popup.getBoundingClientRect();

        // mouse position inside popup
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // convert to percentage
        const moveX = (x / rect.width - 0.5) * 20;
        const moveY = (y / rect.height - 0.5) * 20;

        popup.style.boxShadow = `${-moveX}px ${-moveY}px 30px #14f5bc`;
    });

    popup.addEventListener("mouseleave", () => {
        popup.style.boxShadow = "0 0 20px #14f5bc";
    });
}
function enableEdit(id) {
    let card = event.target.closest(".vault-card");
    let inputs = card.querySelectorAll("input, textarea");
    let button = card.querySelector(".save-btn");

    inputs.forEach(input => {
        input.removeAttribute("readonly");
    });

    button.style.display = "block";
}