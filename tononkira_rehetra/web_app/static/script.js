const editor = document.getElementById('editor');
const overlay = document.getElementById('overlay');
const suggestionsBar = document.getElementById('suggestions');
const wordCountDisplay = document.getElementById('word-count');
const statusDisplay = document.getElementById('status');

let debounceTimer;

editor.addEventListener('input', () => {
    updateWordCount();
    updateOverlay();

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        checkSpelling();
        getPredictions();
    }, 400); // Un peu plus rapide
});

function updateWordCount() {
    const text = editor.value.trim();
    const count = text ? text.split(/\s+/).length : 0;
    wordCountDisplay.innerText = `${count} teny`;
}

function updateOverlay() {
    overlay.innerText = editor.value;
    overlay.scrollTop = editor.scrollTop;
}

editor.addEventListener('scroll', () => {
    overlay.scrollTop = editor.scrollTop;
});

async function checkSpelling() {
    const text = editor.value;
    if (!text) {
        overlay.innerHTML = "";
        return;
    }

    try {
        const response = await fetch('/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await response.json();
        const errors = data.errors;

        if (errors.length > 0) {
            statusDisplay.innerText = `Sava-ria: ${errors.length} fahadisoana hita`;
            highlightErrors(text, errors);
        } else {
            statusDisplay.innerText = "Sava-ria: Madio";
            overlay.innerText = text;
        }
    } catch (e) {
        console.error("Erreur de correction:", e);
    }
}

function highlightErrors(text, errors) {
    let html = text;
    const sortedErrors = [...new Set(errors)].sort((a, b) => b.length - a.length);

    sortedErrors.forEach(err => {
        const regex = new RegExp(`\\b${err}\\b`, 'g');
        html = html.replace(regex, `<span class="error">${err}</span>`);
    });

    overlay.innerHTML = html;
}

async function getPredictions() {
    const text = editor.value;
    if (!text) {
        suggestionsBar.innerHTML = "";
        return;
    }

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await response.json();
        displaySuggestions(data.suggestions, data.type);
    } catch (e) {
        console.error("Erreur de prédiction:", e);
    }
}

function displaySuggestions(suggestions, type) {
    suggestionsBar.innerHTML = "";
    suggestions.forEach(sug => {
        const chip = document.createElement('div');
        chip.className = 'suggestion-chip';
        // Icône différente selon le mode
        chip.innerText = type === 'completion' ? `📝 ${sug}` : `➡️ ${sug}`;
        chip.onclick = () => applySuggestion(sug, type);
        suggestionsBar.appendChild(chip);
    });
}

function applySuggestion(word, type) {
    const text = editor.value;

    if (type === 'completion') {
        const words = text.split(' ');
        words[words.length - 1] = word;
        editor.value = words.join(' ') + " ";
    } else {
        editor.value = text.trim() + " " + word + " ";
    }

    editor.focus();
    updateOverlay();
    suggestionsBar.innerHTML = "";
    checkSpelling();
}
