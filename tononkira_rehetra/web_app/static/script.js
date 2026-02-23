const editor = document.getElementById('editor');
const overlay = document.getElementById('overlay');
const suggestionsBar = document.getElementById('suggestions');
const wordCountDisplay = document.getElementById('word-count');
const statusDisplay = document.getElementById('status-text');
const statusDot = document.getElementById('status-dot');

let debounceTimer;

editor.addEventListener('input', () => {
    updateWordCount();
    syncOverlay();

    // UI Feedback: Busy
    statusDot.classList.add('busy');
    statusDisplay.innerText = "Famakafakana...";

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        analyzeText();
    }, 450);
});

function updateWordCount() {
    const text = editor.value.trim();
    const count = text ? text.split(/\s+/).length : 0;
    wordCountDisplay.innerText = `${count} teny`;
}

function syncOverlay() {
    overlay.innerText = editor.value;
    overlay.scrollTop = editor.scrollTop;
}

editor.addEventListener('scroll', () => {
    overlay.scrollTop = editor.scrollTop;
});

async function analyzeText() {
    const text = editor.value;
    if (!text) {
        overlay.innerHTML = "";
        suggestionsBar.innerHTML = "";
        statusDot.classList.remove('busy');
        statusDisplay.innerText = "Vonona";
        return;
    }

    try {
        // En parallèle : Correction + Prédiction
        const [checkRes, predRes] = await Promise.all([
            fetch('/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            }),
            fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            })
        ]);

        const checkData = await checkRes.json();
        const predData = await predRes.json();

        // 1. Update Errors
        highlightErrors(text, checkData.errors);

        // 2. Update Suggestions
        displaySuggestions(predData.suggestions, predData.type);

        // 3. Update Status
        statusDot.classList.remove('busy');
        if (checkData.errors.length > 0) {
            statusDisplay.innerText = `${checkData.errors.length} fahadisoana`;
        } else {
            statusDisplay.innerText = "Madio";
        }

    } catch (e) {
        console.error("Erreur d'analyse:", e);
        statusDot.classList.remove('busy');
        statusDisplay.innerText = "Erreur Backend";
    }
}

function highlightErrors(text, errors) {
    if (errors.length === 0) {
        overlay.innerText = text;
        return;
    }

    let html = text.replace(/[<>&]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c]));

    // Tri par longueur décroissante pour ne pas casser les remplacements imbriqués
    const sortedErrors = [...new Set(errors)].sort((a, b) => b.length - a.length);

    sortedErrors.forEach(err => {
        // Utilisation d'un regex qui respecte les limites de mots malgaches
        const regex = new RegExp(`\\b${err}\\b`, 'g');
        html = html.replace(regex, `<span class="error">${err}</span>`);
    });

    overlay.innerHTML = html;
}

function displaySuggestions(suggestions, type) {
    suggestionsBar.innerHTML = "";
    if (suggestions.length === 0) return;

    suggestions.forEach(sug => {
        const chip = document.createElement('div');
        chip.className = 'suggestion-chip';

        const icon = type === 'completion' ? '📝' : '➡️';
        chip.innerHTML = `<span class="chip-icon">${icon}</span> ${sug}`;

        chip.onclick = () => applySuggestion(sug, type);
        suggestionsBar.appendChild(chip);
    });
}

function applySuggestion(word, type) {
    const text = editor.value;

    if (type === 'completion') {
        // Remplacer le dernier mot en cours de frappe
        const parts = text.split(/(\s+)/);
        parts[parts.length - 1] = word;
        editor.value = parts.join('') + " ";
    } else {
        // Ajouter le mot prédit
        editor.value = text.trim() + " " + word + " ";
    }

    editor.focus();
    syncOverlay();
    analyzeText(); // Relancer l'analyse immédiatement
}
