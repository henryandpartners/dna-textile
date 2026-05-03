/**
 * DNA Textile Pattern Generator — Web Interface
 *
 * Client-side logic for the interactive web preview.
 * Communicates with the Python backend for pattern generation.
 */

(function () {
    'use strict';

    // ── DOM References ──────────────────────────────────────
    const dnaInput = document.getElementById('dna-input');
    const patternType = document.getElementById('pattern-type');
    const community = document.getElementById('community');
    const gridSize = document.getElementById('grid-size');
    const gridSizeVal = document.getElementById('grid-size-val');
    const stitchRatio = document.getElementById('stitch-ratio');
    const stitchRatioVal = document.getElementById('stitch-ratio-val');
    const complexity = document.getElementById('complexity');
    const seedInput = document.getElementById('seed');
    const patternCanvas = document.getElementById('pattern-canvas');
    const repeatCanvas = document.getElementById('repeat-canvas');
    const repeatSection = document.getElementById('repeat-section');
    const repeatInfo = document.getElementById('repeat-info');
    const statusEl = document.getElementById('status');
    const loadingOverlay = document.getElementById('loading-overlay');
    const autoGenerate = document.getElementById('auto-generate');
    const seqLength = document.getElementById('seq-length');
    const presetSelect = document.getElementById('preset-select');

    const ctx = patternCanvas.getContext('2d');
    const rctx = repeatCanvas.getContext('2d');

    let currentData = null; // Last generated pattern data
    let debounceTimer = null;

    // ── API Base URL ────────────────────────────────────────
    const API_BASE = window.location.origin;

    // ── Utility Functions ───────────────────────────────────
    function setStatus(msg) {
        statusEl.textContent = msg;
    }

    function showLoading(show) {
        loadingOverlay.classList.toggle('hidden', !show);
    }

    function updateSeqLength() {
        const seq = dnaInput.value.replace(/[^ATGCatgc]/g, '');
        seqLength.textContent = `Length: ${seq.length}`;
    }

    // ── Canvas Rendering ────────────────────────────────────
    function renderPattern(data) {
        const { grid, width, height } = data;
        patternCanvas.width = width;
        patternCanvas.height = height;

        const imageData = ctx.createImageData(width, height);
        for (let i = 0; i < grid.length; i++) {
            const idx = i * 4;
            imageData.data[idx] = grid[i][0];     // R
            imageData.data[idx + 1] = grid[i][1]; // G
            imageData.data[idx + 2] = grid[i][2]; // B
            imageData.data[idx + 3] = 255;        // A
        }
        ctx.putImageData(imageData, 0, 0);
    }

    function renderRepeat(data) {
        if (!data.repeat) return;
        const { grid, width, height } = data.repeat;
        repeatCanvas.width = width;
        repeatCanvas.height = height;

        const imageData = rctx.createImageData(width, height);
        for (let i = 0; i < grid.length; i++) {
            const idx = i * 4;
            imageData.data[idx] = grid[i][0];
            imageData.data[idx + 1] = grid[i][1];
            imageData.data[idx + 2] = grid[i][2];
            imageData.data[idx + 3] = 255;
        }
        rctx.putImageData(imageData, 0, 0);

        repeatInfo.textContent = `${data.repeat.repeat_w}×${data.repeat.repeat_h} unit`;
        repeatSection.classList.remove('hidden');
    }

    // ── Pattern Generation ──────────────────────────────────
    async function generatePattern() {
        const seq = dnaInput.value.replace(/[^ATGCatgc]/g, '').toUpperCase();
        if (!seq) {
            setStatus('Please enter a DNA sequence');
            return;
        }

        showLoading(true);
        setStatus('Generating...');

        const params = new URLSearchParams({
            sequence: seq,
            pattern_type: patternType.value,
            community: community.value,
            grid_size: gridSize.value,
            stitch_ratio: stitchRatio.value,
            complexity: complexity.value,
        });

        if (seedInput.value) {
            params.set('seed', seedInput.value);
        }

        try {
            const resp = await fetch(`${API_BASE}/api/generate?${params}`);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const data = await resp.json();

            if (data.error) {
                setStatus(`Error: ${data.error}`);
                return;
            }

            currentData = data;
            renderPattern(data);
            renderRepeat(data);
            setStatus(`Generated ${data.width}×${data.height} — ${data.pattern_type}`);
        } catch (err) {
            setStatus(`Failed: ${err.message}`);
            console.error(err);
        } finally {
            showLoading(false);
        }
    }

    // ── Export Functions ────────────────────────────────────
    async function exportFile(format) {
        if (!currentData) {
            setStatus('Generate a pattern first');
            return;
        }

        const seq = dnaInput.value.replace(/[^ATGCatgc]/g, '').toUpperCase();
        const params = new URLSearchParams({
            sequence: seq,
            pattern_type: patternType.value,
            community: community.value,
            grid_size: gridSize.value,
            stitch_ratio: stitchRatio.value,
            complexity: complexity.value,
            format: format,
        });

        if (seedInput.value) params.set('seed', seedInput.value);

        try {
            setStatus(`Exporting ${format}...`);
            const resp = await fetch(`${API_BASE}/api/export?${params}`);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `dna_textile_${patternType.value}_${Date.now()}.${format === 'png' ? 'png' : format === 'jac' ? 'jac' : format === 'csv' ? 'csv' : 'png'}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            setStatus(`Exported ${format}`);
        } catch (err) {
            setStatus(`Export failed: ${err.message}`);
        }
    }

    // ── Preset Management ───────────────────────────────────
    function savePreset() {
        const name = prompt('Preset name:');
        if (!name) return;

        const preset = {
            pattern_type: patternType.value,
            community: community.value,
            grid_size: gridSize.value,
            stitch_ratio: stitchRatio.value,
            complexity: complexity.value,
            seed: seedInput.value,
        };

        const presets = JSON.parse(localStorage.getItem('dna_textile_presets') || '{}');
        presets[name] = preset;
        localStorage.setItem('dna_textile_presets', JSON.stringify(presets));
        loadPresets();
        setStatus(`Saved preset: ${name}`);
    }

    function loadPresets() {
        const presets = JSON.parse(localStorage.getItem('dna_textile_presets') || '{}');
        presetSelect.innerHTML = '<option value="">Load preset...</option>';
        for (const name of Object.keys(presets).sort()) {
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = name;
            presetSelect.appendChild(opt);
        }
    }

    function applyPreset(name) {
        const presets = JSON.parse(localStorage.getItem('dna_textile_presets') || '{}');
        const preset = presets[name];
        if (!preset) return;

        patternType.value = preset.pattern_type;
        community.value = preset.community;
        gridSize.value = preset.grid_size;
        gridSizeVal.textContent = preset.grid_size;
        stitchRatio.value = preset.stitch_ratio;
        stitchRatioVal.textContent = parseFloat(preset.stitch_ratio).toFixed(2);
        complexity.value = preset.complexity;
        seedInput.value = preset.seed || '';

        if (autoGenerate.checked) generatePattern();
    }

    function deletePreset() {
        const name = presetSelect.value;
        if (!name) return;
        if (!confirm(`Delete preset "${name}"?`)) return;

        const presets = JSON.parse(localStorage.getItem('dna_textile_presets') || '{}');
        delete presets[name];
        localStorage.setItem('dna_textile_presets', JSON.stringify(presets));
        loadPresets();
        setStatus(`Deleted preset: ${name}`);
    }

    // ── Random DNA ──────────────────────────────────────────
    function randomDNA() {
        const bases = 'ATGC';
        const len = 50 + Math.floor(Math.random() * 100);
        let seq = '';
        for (let i = 0; i < len; i++) {
            seq += bases[Math.floor(Math.random() * 4)];
        }
        dnaInput.value = seq;
        updateSeqLength();
        if (autoGenerate.checked) generatePattern();
    }

    function loadSample() {
        dnaInput.value = 'ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC';
        updateSeqLength();
        if (autoGenerate.checked) generatePattern();
    }

    // ── Event Listeners ─────────────────────────────────────
    function debouncedGenerate() {
        if (!autoGenerate.checked) return;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(generatePattern, 300);
    }

    // Controls
    document.getElementById('btn-generate').addEventListener('click', generatePattern);
    document.getElementById('btn-random').addEventListener('click', randomDNA);
    document.getElementById('btn-sample').addEventListener('click', loadSample);

    // Exports
    document.getElementById('btn-export-png').addEventListener('click', () => exportFile('png'));
    document.getElementById('btn-export-jac').addEventListener('click', () => exportFile('jac'));
    document.getElementById('btn-export-punch').addEventListener('click', () => exportFile('punch_card'));
    document.getElementById('btn-export-lace').addEventListener('click', () => exportFile('lace_chart'));
    document.getElementById('btn-export-csv').addEventListener('click', () => exportFile('punch_card_csv'));
    document.getElementById('btn-export-tiled').addEventListener('click', () => exportFile('tiled'));

    // Presets
    document.getElementById('btn-save-preset').addEventListener('click', savePreset);
    presetSelect.addEventListener('change', (e) => { if (e.target.value) applyPreset(e.target.value); });
    document.getElementById('btn-delete-preset').addEventListener('click', deletePreset);

    // Input changes
    dnaInput.addEventListener('input', () => { updateSeqLength(); debouncedGenerate(); });
    patternType.addEventListener('change', debouncedGenerate);
    community.addEventListener('change', debouncedGenerate);
    complexity.addEventListener('change', debouncedGenerate);

    gridSize.addEventListener('input', () => {
        gridSizeVal.textContent = gridSize.value;
        debouncedGenerate();
    });

    stitchRatio.addEventListener('input', () => {
        stitchRatioVal.textContent = parseFloat(stitchRatio.value).toFixed(2);
        debouncedGenerate();
    });

    seedInput.addEventListener('change', debouncedGenerate);

    // ── Initialize ──────────────────────────────────────────
    updateSeqLength();
    loadPresets();

    // Auto-generate on load if DNA is present
    if (dnaInput.value.trim()) {
        generatePattern();
    }

})();
