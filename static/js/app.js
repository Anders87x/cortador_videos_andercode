const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");
const themeLabel = document.getElementById("themeLabel");
const workflowLinks = [...document.querySelectorAll(".workflow-link")];

const presetSelect = document.getElementById("presetSelect");
const applyPresetButton = document.getElementById("applyPresetButton");
const savePresetButton = document.getElementById("savePresetButton");
const deletePresetButton = document.getElementById("deletePresetButton");
const recentProjectSelect = document.getElementById("recentProjectSelect");
const openProjectButton = document.getElementById("openProjectButton");
const deleteProjectButton = document.getElementById("deleteProjectButton");
const clearProjectsButton = document.getElementById("clearProjectsButton");

const videoInput = document.getElementById("videoInput");
const dropZone = document.getElementById("dropZone");
const uploadForm = document.getElementById("uploadForm");
const uploadButton = document.getElementById("uploadButton");
const analyzeButton = document.getElementById("analyzeButton");
const uploadStatus = document.getElementById("uploadStatus");

const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");

const previewPlaceholder = document.getElementById("previewPlaceholder");
const previewWorkspace = document.getElementById("previewWorkspace");
const videoPreview = document.getElementById("videoPreview");
const verticalPreviewCard = document.getElementById("verticalPreviewCard");
const verticalBackground = document.getElementById("verticalBackground");
const verticalForeground = document.getElementById("verticalForeground");

const introSeconds = document.getElementById("introSeconds");
const clipSeconds = document.getElementById("clipSeconds");
const videoDuration = document.getElementById("videoDuration");
const estimatedClips = document.getElementById("estimatedClips");

const segmentsPanel = document.getElementById("segmentsPanel");
const metadataGrid = document.getElementById("metadataGrid");
const analysisSummary = document.getElementById("analysisSummary");
const segmentsCount = document.getElementById("segmentsCount");
const segmentsList = document.getElementById("segmentsList");
const selectAllButton = document.getElementById("selectAllButton");
const deselectAllButton = document.getElementById("deselectAllButton");

const selectedCount = document.getElementById("selectedCount");
const generateButton = document.getElementById("generateButton");
const generationProgress = document.getElementById("generationProgress");
const progressTitle = document.getElementById("progressTitle");
const progressPercent = document.getElementById("progressPercent");
const progressBar = document.getElementById("progressBar");
const progressDetail = document.getElementById("progressDetail");
const generatedResults = document.getElementById("generatedResults");
const generatedList = document.getElementById("generatedList");
const outputFolder = document.getElementById("outputFolder");
const generationDescription = document.getElementById("generationDescription");
const outputFormatSummary = document.getElementById("outputFormatSummary");
const outputFormatInputs = [...document.querySelectorAll('input[name="outputFormat"]')];
const verticalSettings = document.getElementById("verticalSettings");
const contentScale = document.getElementById("contentScale");
const contentScaleValue = document.getElementById("contentScaleValue");
const blurStrength = document.getElementById("blurStrength");
const blurStrengthValue = document.getElementById("blurStrengthValue");
const verticalPositionInputs = [...document.querySelectorAll('input[name="verticalPosition"]')];
const brandingEnabled = document.getElementById("brandingEnabled");
const brandingSettings = document.getElementById("brandingSettings");
const brandingTitle = document.getElementById("brandingTitle");
const brandingHandle = document.getElementById("brandingHandle");
const showSafeZone = document.getElementById("showSafeZone");
const brandingPreview = document.getElementById("brandingPreview");
const brandingTitlePreview = document.getElementById("brandingTitlePreview");
const brandingHandlePreview = document.getElementById("brandingHandlePreview");
const subtitleSafeZone = document.getElementById("subtitleSafeZone");

let selectedFile = null;
let objectUrl = null;
let uploadedFilename = null;
let activePreviewEnd = null;
let currentSegments = [];
let generationInProgress = false;
let ffmpegReady = false;
let outputFormat = "original";
let recentProjects = [];

const THEME_STORAGE_KEY = "andercode-video-theme";
const PRESETS_STORAGE_KEY = "andercode-video-presets";

const BUILTIN_PRESETS = {
    "Reel AnderCode": {
        intro_seconds: 5,
        clip_seconds: 30,
        output_format: "vertical",
        vertical_scale: 88,
        vertical_position: "center",
        blur_strength: 25,
        branding_enabled: true,
        branding_title: "",
        branding_handle: "anderson-bastidas.com",
        show_safe_zone: true,
    },
    "Reel limpio": {
        intro_seconds: 5,
        clip_seconds: 30,
        output_format: "vertical",
        vertical_scale: 100,
        vertical_position: "center",
        blur_strength: 25,
        branding_enabled: false,
        branding_title: "",
        branding_handle: "@AnderCode",
        show_safe_zone: true,
    },
    "Formato original": {
        intro_seconds: 5,
        clip_seconds: 30,
        output_format: "original",
        vertical_scale: 100,
        vertical_position: "center",
        blur_strength: 25,
        branding_enabled: false,
        branding_title: "",
        branding_handle: "@AnderCode",
        show_safe_zone: true,
    },
};

function getCustomPresets() {
    try {
        const stored = JSON.parse(localStorage.getItem(PRESETS_STORAGE_KEY) || "{}");
        return stored && typeof stored === "object" && !Array.isArray(stored)
            ? stored
            : {};
    } catch (_error) {
        return {};
    }
}

function saveCustomPresets(presets) {
    try {
        localStorage.setItem(PRESETS_STORAGE_KEY, JSON.stringify(presets));
        return true;
    } catch (_error) {
        setStatus("No se pudieron guardar los presets en el navegador.", "error");
        return false;
    }
}

function captureCurrentSettings() {
    return {
        intro_seconds: Number(introSeconds.value) || 0,
        clip_seconds: Number(clipSeconds.value) || 30,
        output_format: getOutputFormat(),
        vertical_scale: Number(contentScale.value) || 100,
        vertical_position: getVerticalPosition(),
        blur_strength: Number(blurStrength.value) || 25,
        branding_enabled: brandingEnabled.checked,
        branding_title: brandingTitle.value.trim(),
        branding_handle: brandingHandle.value.trim(),
        show_safe_zone: showSafeZone.checked,
    };
}

function deriveTitleFromName(name = "") {
    return name
        .replace(/\.[^/.]+$/, "")
        .replace(/[_-]+/g, " ")
        .replace(/\s+/g, " ")
        .trim();
}

function applySettings(settings = {}) {
    introSeconds.value = settings.intro_seconds ?? 5;
    clipSeconds.value = settings.clip_seconds ?? 30;
    contentScale.value = settings.vertical_scale ?? 100;
    blurStrength.value = settings.blur_strength ?? 25;

    const desiredFormat = settings.output_format || "original";
    const formatInput = outputFormatInputs.find(
        (input) => input.value === desiredFormat
    );

    if (formatInput) {
        formatInput.checked = true;
    }

    const desiredPosition = settings.vertical_position || "center";
    const positionInput = verticalPositionInputs.find(
        (input) => input.value === desiredPosition
    );

    if (positionInput) {
        positionInput.checked = true;
    }

    brandingEnabled.checked = Boolean(settings.branding_enabled);
    brandingHandle.value = settings.branding_handle ?? "@AnderCode";
    showSafeZone.checked = settings.show_safe_zone !== false;

    if (typeof settings.branding_title === "string" && settings.branding_title.trim()) {
        brandingTitle.value = settings.branding_title;
    } else if (fileName.textContent && fileName.textContent !== "—") {
        brandingTitle.value = deriveTitleFromName(fileName.textContent);
    } else {
        brandingTitle.value = "";
    }

    recalculateClips();
    updateVerticalPreviewStyle();
    updateBrandingPreview();
    updateOutputFormat();

    if (uploadedFilename) {
        segmentsPanel.classList.add("hidden");
        analyzeButton.classList.remove("hidden");
        currentSegments = [];
        resetGeneration();
    }
}

function renderPresetOptions(selectedValue = "") {
    const customPresets = getCustomPresets();
    const options = [
        '<optgroup label="Incluidos">',
        ...Object.keys(BUILTIN_PRESETS).map(
            (name) => `<option value="builtin:${name}">${name}</option>`
        ),
        "</optgroup>",
    ];

    const customNames = Object.keys(customPresets);

    if (customNames.length) {
        options.push('<optgroup label="Mis presets">');
        options.push(
            ...customNames.map(
                (name) => `<option value="custom:${name}">${name}</option>`
            )
        );
        options.push("</optgroup>");
    }

    presetSelect.innerHTML = options.join("");

    if (selectedValue && [...presetSelect.options].some((option) => option.value === selectedValue)) {
        presetSelect.value = selectedValue;
    }

    updatePresetButtons();
}

function getSelectedPreset() {
    const [type, ...parts] = presetSelect.value.split(":");
    const name = parts.join(":");

    if (type === "builtin") {
        return {
            type,
            name,
            settings: BUILTIN_PRESETS[name],
        };
    }

    const custom = getCustomPresets();

    return {
        type: "custom",
        name,
        settings: custom[name],
    };
}

function updatePresetButtons() {
    const selected = getSelectedPreset();
    deletePresetButton.disabled = selected.type !== "custom";
}

async function loadRecentProjects(selectedId = "") {
    try {
        const response = await fetch("/projects");
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "No se pudieron cargar los proyectos recientes.");
        }

        recentProjects = data.projects || [];

        if (!recentProjects.length) {
            recentProjectSelect.innerHTML = '<option value="">Sin proyectos recientes</option>';
            openProjectButton.disabled = true;
            deleteProjectButton.disabled = true;
            clearProjectsButton.disabled = true;
            return;
        }

        recentProjectSelect.innerHTML = recentProjects.map((project) => {
            const unavailable = project.available ? "" : " · no disponible";
            const name = project.original_name || project.filename || project.id;
            return `<option value="${project.id}">${name}${unavailable}</option>`;
        }).join("");

        if (selectedId && recentProjects.some((project) => project.id === selectedId)) {
            recentProjectSelect.value = selectedId;
        }

        updateProjectButtons();
    } catch (error) {
        recentProjectSelect.innerHTML = '<option value="">No se pudieron cargar</option>';
        openProjectButton.disabled = true;
        deleteProjectButton.disabled = true;
        clearProjectsButton.disabled = true;
    }
}

function updateProjectButtons() {
    const project = recentProjects.find(
        (item) => item.id === recentProjectSelect.value
    );

    openProjectButton.disabled = !project?.available;
    deleteProjectButton.disabled = !project;
    clearProjectsButton.disabled = recentProjects.length === 0;
}

function loadPreviewUrl(url) {
    if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
        objectUrl = null;
    }

    videoPreview.src = url;
    verticalBackground.src = url;
    verticalForeground.src = url;

    previewPlaceholder.classList.add("hidden");
    previewWorkspace.classList.remove("hidden");

    videoPreview.load();
    verticalBackground.load();
    verticalForeground.load();

    updateVerticalPreviewStyle();
    updateBrandingPreview();
    updateOutputFormat();
}

async function openRecentProject() {
    const projectId = recentProjectSelect.value;

    if (!projectId) {
        return;
    }

    try {
        const response = await fetch(`/projects/${encodeURIComponent(projectId)}`);
        const project = await response.json();

        if (!response.ok) {
            throw new Error(project.message || "No se pudo abrir el proyecto.");
        }

        if (!project.available || !project.url) {
            throw new Error("El archivo original de este proyecto ya no está disponible.");
        }

        resetAnalysis();
        selectedFile = null;
        uploadedFilename = project.filename;

        fileName.textContent = project.original_name || project.filename;
        fileSize.textContent = formatBytes(Number(project.size) || 0);
        fileInfo.classList.remove("hidden");

        uploadButton.disabled = true;
        uploadButton.textContent = "Video ya cargado en el proyecto";
        analyzeButton.classList.remove("hidden");

        applySettings(project);
        loadPreviewUrl(project.url);

        setStatus(
            "Proyecto reciente cargado. Puedes analizarlo y continuar trabajando.",
            "success"
        );
        setActiveWorkflow("uploadSection");
        document.getElementById("uploadSection").scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    } catch (error) {
        setStatus(error.message || "No se pudo abrir el proyecto.", "error");
    }
}

function updateThemeControl() {
    const theme = document.documentElement.dataset.theme || "dark";
    const isDark = theme === "dark";

    themeIcon.textContent = isDark ? "☾" : "☀";
    themeLabel.textContent = isDark ? "Oscuro" : "Claro";
    themeToggle.setAttribute(
        "aria-label",
        isDark ? "Cambiar a modo claro" : "Cambiar a modo oscuro"
    );
    themeToggle.title =
        isDark ? "Cambiar a modo claro" : "Cambiar a modo oscuro";
}

function setTheme(theme, persist = true) {
    document.documentElement.dataset.theme = theme;
    updateThemeControl();

    if (persist) {
        try {
            localStorage.setItem(THEME_STORAGE_KEY, theme);
        } catch (_error) {
            // El navegador puede bloquear el almacenamiento local.
        }
    }
}

function setActiveWorkflow(targetId) {
    workflowLinks.forEach((link) => {
        const active = link.dataset.workflowTarget === targetId;
        link.classList.toggle("active", active);

        if (active) {
            link.setAttribute("aria-current", "step");
        } else {
            link.removeAttribute("aria-current");
        }
    });
}

function setupWorkflowObserver() {
    if (!("IntersectionObserver" in window)) {
        return;
    }

    const sections = workflowLinks
        .map((link) => document.getElementById(link.dataset.workflowTarget))
        .filter(Boolean);

    const observer = new IntersectionObserver(
        (entries) => {
            const visible = entries
                .filter((entry) => entry.isIntersecting)
                .sort((a, b) => b.intersectionRatio - a.intersectionRatio);

            if (visible[0]) {
                setActiveWorkflow(visible[0].target.id);
            }
        },
        {
            rootMargin: "-22% 0px -58% 0px",
            threshold: [0.05, 0.2, 0.45],
        }
    );

    sections.forEach((section) => observer.observe(section));
}


function getOutputFormat() {
    return outputFormatInputs.find((input) => input.checked)?.value || "original";
}

function syncVerticalPreview(force = false) {
    if (!Number.isFinite(videoPreview.currentTime)) {
        return;
    }

    [verticalBackground, verticalForeground].forEach((video) => {
        if (force || Math.abs(video.currentTime - videoPreview.currentTime) > 0.2) {
            try {
                video.currentTime = videoPreview.currentTime;
            } catch (_error) {
                // El navegador puede ignorar el seek hasta tener metadatos.
            }
        }
    });
}

async function playVerticalPreview() {
    if (outputFormat !== "vertical") {
        return;
    }

    syncVerticalPreview(true);

    await Promise.allSettled([
        verticalBackground.play(),
        verticalForeground.play(),
    ]);
}

function pauseVerticalPreview() {
    verticalBackground.pause();
    verticalForeground.pause();
}

function getVerticalPosition() {
    return verticalPositionInputs.find((input) => input.checked)?.value || "center";
}

function updateVerticalPreviewStyle() {
    const scale = Number(contentScale.value) || 100;
    const blur = Number(blurStrength.value) || 25;
    const position = getVerticalPosition();

    contentScaleValue.textContent = `${scale}%`;
    blurStrengthValue.textContent = String(blur);

    const stage = verticalForeground.parentElement;
    const stageWidth = stage?.clientWidth || 0;
    const stageHeight = stage?.clientHeight || 0;
    const sourceWidth = videoPreview.videoWidth || verticalForeground.videoWidth || 0;
    const sourceHeight = videoPreview.videoHeight || verticalForeground.videoHeight || 0;

    if (stageWidth > 0 && stageHeight > 0 && sourceWidth > 0 && sourceHeight > 0) {
        const scaleRatio = scale / 100;
        const targetWidth = stageWidth * scaleRatio;
        const targetHeight = stageHeight * scaleRatio;
        const sourceRatio = sourceWidth / sourceHeight;
        const targetRatio = targetWidth / targetHeight;

        let renderedWidth;
        let renderedHeight;

        if (sourceRatio >= targetRatio) {
            renderedWidth = targetWidth;
            renderedHeight = renderedWidth / sourceRatio;
        } else {
            renderedHeight = targetHeight;
            renderedWidth = renderedHeight * sourceRatio;
        }

        let top = 0;

        if (position === "center") {
            top = (stageHeight - renderedHeight) / 2;
        } else if (position === "bottom") {
            top = stageHeight - renderedHeight;
        }

        verticalForeground.style.width = `${renderedWidth}px`;
        verticalForeground.style.height = `${renderedHeight}px`;
        verticalForeground.style.left = "50%";
        verticalForeground.style.top = `${Math.max(0, top)}px`;
        verticalForeground.style.right = "auto";
        verticalForeground.style.bottom = "auto";
        verticalForeground.style.transform = "translateX(-50%)";
    }

    const previewBlur = Math.max(4, Math.round(blur * 0.72));
    verticalBackground.style.filter =
        `blur(${previewBlur}px) brightness(0.62)`;
}

function updateBrandingPreview() {
    const enabled = brandingEnabled.checked && outputFormat === "vertical";
    const title = brandingTitle.value.trim();
    const handle = brandingHandle.value.trim();

    brandingSettings.classList.toggle("hidden", !brandingEnabled.checked);
    brandingPreview.classList.toggle("hidden", !enabled);

    brandingTitlePreview.textContent = title;
    brandingTitlePreview.classList.toggle("hidden", !title);

    brandingHandlePreview.textContent = handle;
    brandingHandlePreview.classList.toggle("hidden", !handle);

    const handleLength = handle.length;
    const handleFontSize =
        handleLength <= 16 ? "0.76rem" :
        handleLength <= 24 ? "0.66rem" :
        handleLength <= 32 ? "0.58rem" :
        "0.52rem";

    brandingHandlePreview.style.fontSize = handleFontSize;

    subtitleSafeZone.classList.toggle("hidden", !showSafeZone.checked);
}

function updateOutputFormat() {
    outputFormat = getOutputFormat();
    const isVertical = outputFormat === "vertical";

    verticalPreviewCard.classList.toggle("hidden", !isVertical);
    verticalSettings.classList.toggle("hidden", !isVertical);

    outputFormatSummary.textContent = isVertical
        ? "Salida: Reel 9:16 · 1080×1920"
        : "Salida: Original";

    generationDescription.innerHTML = isVertical
        ? 'Los clips se exportarán en <strong>1080×1920</strong>, respetando el tamaño, posición y desenfoque configurados en el preview. Se guardarán dentro de <code>outputs/</code>.'
        : 'Los clips se exportarán en MP4 manteniendo la resolución original. Se guardarán dentro de <code>outputs/</code>.';

    if (isVertical) {
        updateVerticalPreviewStyle();
        updateBrandingPreview();
        syncVerticalPreview(true);

        if (!videoPreview.paused) {
            playVerticalPreview();
        }
    } else {
        brandingPreview.classList.add("hidden");
        pauseVerticalPreview();
    }

    if (currentSegments.length && !generationInProgress) {
        resetGeneration();
    }
}

function formatBytes(bytes) {
    if (!Number.isFinite(bytes) || bytes <= 0) {
        return "0 MB";
    }

    const units = ["B", "KB", "MB", "GB"];
    const index = Math.min(
        Math.floor(Math.log(bytes) / Math.log(1024)),
        units.length - 1
    );

    const value = bytes / Math.pow(1024, index);
    return `${value.toFixed(index >= 2 ? 2 : 0)} ${units[index]}`;
}

function formatDuration(seconds) {
    if (!Number.isFinite(Number(seconds))) {
        return "—";
    }

    const total = Math.max(0, Math.floor(Number(seconds)));
    const hours = Math.floor(total / 3600);
    const minutes = Math.floor((total % 3600) / 60);
    const secs = total % 60;

    if (hours > 0) {
        return [hours, minutes, secs]
            .map((value) => String(value).padStart(2, "0"))
            .join(":");
    }

    return [minutes, secs]
        .map((value) => String(value).padStart(2, "0"))
        .join(":");
}

function recalculateClips() {
    const duration = videoPreview.duration;
    const intro = Math.max(0, Number(introSeconds.value) || 0);
    const clip = Math.max(1, Number(clipSeconds.value) || 30);

    if (!Number.isFinite(duration)) {
        videoDuration.textContent = "—";
        estimatedClips.textContent = "—";
        return;
    }

    const usableDuration = Math.max(0, duration - intro);
    const clips = usableDuration > 0 ? Math.ceil(usableDuration / clip) : 0;

    videoDuration.textContent = formatDuration(duration);
    estimatedClips.textContent = String(clips);
}

function setStatus(message = "", type = "") {
    uploadStatus.textContent = message;
    uploadStatus.className = "upload-status";

    if (!message) {
        uploadStatus.classList.add("hidden");
        return;
    }

    uploadStatus.classList.add("visible");

    if (type) {
        uploadStatus.classList.add(type);
    }
}

function isSupportedVideo(file) {
    const allowedExtensions = ["mp4", "mov", "mkv", "webm", "avi"];
    const extension = file.name.split(".").pop()?.toLowerCase();

    return file.type.startsWith("video/") || allowedExtensions.includes(extension);
}

function resetGeneration() {
    generationProgress.classList.add("hidden");
    generatedResults.classList.add("hidden");
    generatedList.innerHTML = "";
    outputFolder.textContent = "";
    progressBar.style.width = "0%";
    progressPercent.textContent = "0%";
    progressTitle.textContent = "Preparando...";
    progressDetail.textContent = "Esperando generación.";
}

function resetAnalysis() {
    uploadedFilename = null;
    currentSegments = [];
    ffmpegReady = false;
    analyzeButton.classList.add("hidden");
    segmentsPanel.classList.add("hidden");
    metadataGrid.innerHTML = "";
    segmentsList.innerHTML = "";
    analysisSummary.textContent = "Esperando análisis";
    activePreviewEnd = null;
    selectedCount.textContent = "0 clips seleccionados";
    generateButton.disabled = true;
    resetGeneration();
}

function selectFile(file) {
    if (!file) {
        return;
    }

    if (!isSupportedVideo(file)) {
        setStatus("El archivo seleccionado no parece ser un video compatible.", "error");
        return;
    }

    resetAnalysis();
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatBytes(file.size);

    if (!brandingTitle.value.trim()) {
        brandingTitle.value = file.name.replace(/\.[^/.]+$/, "").replace(/[_-]+/g, " ");
    }
    fileInfo.classList.remove("hidden");
    uploadButton.disabled = false;
    uploadButton.textContent = "Cargar video al proyecto";
    setStatus("");

    if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
    }

    objectUrl = URL.createObjectURL(file);
    videoPreview.src = objectUrl;
    verticalBackground.src = objectUrl;
    verticalForeground.src = objectUrl;

    previewPlaceholder.classList.add("hidden");
    previewWorkspace.classList.remove("hidden");

    videoPreview.load();
    verticalBackground.load();
    verticalForeground.load();
    updateVerticalPreviewStyle();
    updateBrandingPreview();
    updateOutputFormat();
}

function renderMetadata(metadata) {
    const items = [
        ["Duración", formatDuration(metadata.duration)],
        ["Resolución", metadata.width && metadata.height ? `${metadata.width} × ${metadata.height}` : "—"],
        ["Video", metadata.video_codec ? metadata.video_codec.toUpperCase() : "—"],
        ["FPS", metadata.fps || "—"],
        ["Audio", metadata.has_audio ? (metadata.audio_codec || "Sí").toUpperCase() : "Sin audio"],
    ];

    metadataGrid.innerHTML = items.map(([label, value]) => `
        <div class="metadata-item">
            <span>${label}</span>
            <strong>${value}</strong>
        </div>
    `).join("");
}

function updateSelectedCount() {
    const checkboxes = [...document.querySelectorAll(".segment-checkbox")];
    const checked = checkboxes.filter((checkbox) => checkbox.checked);

    selectedCount.textContent = `${checked.length} ${checked.length === 1 ? "clip seleccionado" : "clips seleccionados"}`;
    generateButton.disabled = generationInProgress || !ffmpegReady || checked.length === 0;

    selectAllButton.disabled = generationInProgress || checkboxes.length === 0;
    deselectAllButton.disabled = generationInProgress || checked.length === 0;
}

function renderSegments(segments) {
    currentSegments = segments;
    segmentsCount.textContent = `${segments.length} ${segments.length === 1 ? "clip" : "clips"}`;

    if (!segments.length) {
        segmentsList.innerHTML = `
            <div class="empty-segments">
                No hay duración útil después de eliminar la intro.
            </div>
        `;
        updateSelectedCount();
        return;
    }

    segmentsList.innerHTML = segments.map((segment) => `
        <article class="segment-card" data-segment-index="${segment.index}">
            <label class="segment-check">
                <input type="checkbox" class="segment-checkbox" data-index="${segment.index}" checked>
                <span>Clip ${String(segment.index).padStart(2, "0")}</span>
            </label>

            <div class="segment-time">
                <strong>${formatDuration(segment.start)}</strong>
                <span>→</span>
                <strong>${formatDuration(segment.end)}</strong>
            </div>

            <span class="segment-duration">${formatDuration(segment.duration)}</span>

            <button
                class="preview-segment-button"
                type="button"
                data-start="${segment.start}"
                data-end="${segment.end}"
            >
                ▶ Ver
            </button>
        </article>
    `).join("");

    document.querySelectorAll(".segment-checkbox").forEach((checkbox) => {
        checkbox.addEventListener("change", updateSelectedCount);
    });

    document.querySelectorAll(".preview-segment-button").forEach((button) => {
        button.addEventListener("click", async () => {
            const start = Number(button.dataset.start);
            const end = Number(button.dataset.end);

            activePreviewEnd = end;
            videoPreview.currentTime = start;
            videoPreview.scrollIntoView({ behavior: "smooth", block: "center" });

            try {
                await videoPreview.play();
            } catch (_error) {
                setStatus("Pulsa Play en el reproductor para iniciar la vista previa.", "error");
            }
        });
    });

    updateSelectedCount();
}

function setGenerationControlsDisabled(disabled) {
    generationInProgress = disabled;

    document.querySelectorAll(".segment-checkbox").forEach((checkbox) => {
        checkbox.disabled = disabled;
    });

    document.querySelectorAll(".preview-segment-button").forEach((button) => {
        button.disabled = disabled;
    });

    selectAllButton.disabled = disabled;
    deselectAllButton.disabled = disabled;
    introSeconds.disabled = disabled;
    clipSeconds.disabled = disabled;
    videoInput.disabled = disabled;
    uploadButton.disabled = disabled;
    analyzeButton.disabled = disabled;
    outputFormatInputs.forEach((input) => {
        input.disabled = disabled;
    });
    verticalPositionInputs.forEach((input) => {
        input.disabled = disabled;
    });
    contentScale.disabled = disabled;
    blurStrength.disabled = disabled;
    brandingEnabled.disabled = disabled;
    brandingTitle.disabled = disabled;
    brandingHandle.disabled = disabled;
    showSafeZone.disabled = disabled;

    updateSelectedCount();
}

function renderGeneratedClip(data) {
    const item = document.createElement("div");
    item.className = "generated-item";

    const info = document.createElement("div");
    const name = document.createElement("strong");
    const meta = document.createElement("span");

    name.textContent = data.filename;
    const formatLabel = data.output_format === "vertical" ? "Reel 9:16" : "Original";
    meta.textContent = `${formatDuration(data.duration)} · ${formatBytes(data.size)} · ${formatLabel} · ${data.resolution || "—"}`;

    info.append(name, meta);

    const link = document.createElement("a");
    link.href = data.url;
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = "▶ Abrir clip";

    item.append(info, link);
    generatedList.appendChild(item);
}

presetSelect.addEventListener("change", updatePresetButtons);

applyPresetButton.addEventListener("click", () => {
    const preset = getSelectedPreset();

    if (!preset.settings) {
        setStatus("El preset seleccionado ya no existe.", "error");
        renderPresetOptions();
        return;
    }

    applySettings(preset.settings);
    setStatus(`Preset "${preset.name}" aplicado correctamente.`, "success");
});

savePresetButton.addEventListener("click", () => {
    const suggestedName = "Mi preset";
    const name = window.prompt("Nombre del preset:", suggestedName)?.trim();

    if (!name) {
        return;
    }

    if (Object.prototype.hasOwnProperty.call(BUILTIN_PRESETS, name)) {
        setStatus("Ese nombre está reservado para un preset incluido.", "error");
        return;
    }

    const customPresets = getCustomPresets();
    customPresets[name] = captureCurrentSettings();

    if (saveCustomPresets(customPresets)) {
        const value = `custom:${name}`;
        renderPresetOptions(value);
        setStatus(`Preset "${name}" guardado.`, "success");
    }
});

deletePresetButton.addEventListener("click", () => {
    const preset = getSelectedPreset();

    if (preset.type !== "custom" || !preset.name) {
        return;
    }

    if (!window.confirm(`¿Eliminar el preset "${preset.name}"?`)) {
        return;
    }

    const customPresets = getCustomPresets();
    delete customPresets[preset.name];

    if (saveCustomPresets(customPresets)) {
        renderPresetOptions("builtin:Reel AnderCode");
        setStatus(`Preset "${preset.name}" eliminado.`, "success");
    }
});

recentProjectSelect.addEventListener("change", updateProjectButtons);

openProjectButton.addEventListener("click", openRecentProject);

deleteProjectButton.addEventListener("click", async () => {
    const projectId = recentProjectSelect.value;
    const project = recentProjects.find((item) => item.id === projectId);

    if (!project) {
        return;
    }

    const name = project.original_name || project.filename || project.id;

    if (!window.confirm(`¿Eliminar "${name}" y sus clips generados?`)) {
        return;
    }

    try {
        const response = await fetch(
            `/projects/${encodeURIComponent(projectId)}`,
            { method: "DELETE" }
        );
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "No se pudo eliminar el proyecto.");
        }

        if (uploadedFilename === project.filename) {
            resetAnalysis();
            selectedFile = null;
            fileInfo.classList.add("hidden");
            previewWorkspace.classList.add("hidden");
            previewPlaceholder.classList.remove("hidden");
            videoPreview.removeAttribute("src");
            verticalBackground.removeAttribute("src");
            verticalForeground.removeAttribute("src");
            videoPreview.load();
            uploadButton.textContent = "Cargar video al proyecto";
        }

        await loadRecentProjects();
        setStatus(data.message, "success");
    } catch (error) {
        setStatus(error.message || "No se pudo eliminar el proyecto.", "error");
    }
});

clearProjectsButton.addEventListener("click", async () => {
    if (!recentProjects.length) {
        return;
    }

    if (!window.confirm(
        "¿Eliminar TODOS los proyectos recientes, videos cargados y clips generados? Esta acción no se puede deshacer."
    )) {
        return;
    }

    try {
        const response = await fetch("/projects", { method: "DELETE" });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "No se pudieron limpiar los proyectos.");
        }

        resetAnalysis();
        selectedFile = null;
        fileInfo.classList.add("hidden");
        previewWorkspace.classList.add("hidden");
        previewPlaceholder.classList.remove("hidden");
        videoPreview.removeAttribute("src");
        verticalBackground.removeAttribute("src");
        verticalForeground.removeAttribute("src");
        videoPreview.load();
        uploadButton.textContent = "Cargar video al proyecto";

        await loadRecentProjects();
        setStatus(data.message, "success");
    } catch (error) {
        setStatus(error.message || "No se pudieron limpiar los proyectos.", "error");
    }
});

themeToggle.addEventListener("click", () => {
    const currentTheme = document.documentElement.dataset.theme || "dark";
    setTheme(currentTheme === "dark" ? "light" : "dark");
});

workflowLinks.forEach((link) => {
    link.addEventListener("click", () => {
        setActiveWorkflow(link.dataset.workflowTarget);
    });
});

videoInput.addEventListener("change", () => {
    selectFile(videoInput.files[0]);
});

["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.add("dragging");
    });
});

["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.remove("dragging");
    });
});

dropZone.addEventListener("drop", (event) => {
    const file = event.dataTransfer.files[0];

    if (file) {
        const transfer = new DataTransfer();
        transfer.items.add(file);
        videoInput.files = transfer.files;
        selectFile(file);
    }
});

videoPreview.addEventListener("loadedmetadata", () => {
    recalculateClips();
    updateVerticalPreviewStyle();
    syncVerticalPreview(true);
});

verticalForeground.addEventListener("loadedmetadata", () => {
    updateVerticalPreviewStyle();
});

window.addEventListener("resize", () => {
    if (outputFormat === "vertical") {
        updateVerticalPreviewStyle();
    }
});

videoPreview.addEventListener("play", () => {
    playVerticalPreview();
});

videoPreview.addEventListener("pause", () => {
    pauseVerticalPreview();
});

videoPreview.addEventListener("seeking", () => {
    syncVerticalPreview(true);
});

videoPreview.addEventListener("timeupdate", () => {
    if (outputFormat === "vertical") {
        syncVerticalPreview();
    }

    if (activePreviewEnd !== null && videoPreview.currentTime >= activePreviewEnd) {
        videoPreview.pause();
        activePreviewEnd = null;
    }
});

outputFormatInputs.forEach((input) => {
    input.addEventListener("change", updateOutputFormat);
});

contentScale.addEventListener("input", () => {
    updateVerticalPreviewStyle();

    if (currentSegments.length && !generationInProgress) {
        resetGeneration();
    }
});

blurStrength.addEventListener("input", () => {
    updateVerticalPreviewStyle();

    if (currentSegments.length && !generationInProgress) {
        resetGeneration();
    }
});

verticalPositionInputs.forEach((input) => {
    input.addEventListener("change", () => {
        updateVerticalPreviewStyle();

        if (currentSegments.length && !generationInProgress) {
            resetGeneration();
        }
    });
});

brandingEnabled.addEventListener("change", () => {
    updateBrandingPreview();

    if (currentSegments.length && !generationInProgress) {
        resetGeneration();
    }
});

[brandingTitle, brandingHandle].forEach((input) => {
    input.addEventListener("input", () => {
        updateBrandingPreview();

        if (currentSegments.length && !generationInProgress) {
            resetGeneration();
        }
    });
});

showSafeZone.addEventListener("change", updateBrandingPreview);

introSeconds.addEventListener("input", () => {
    recalculateClips();

    if (uploadedFilename) {
        segmentsPanel.classList.add("hidden");
        analyzeButton.classList.remove("hidden");
        analysisSummary.textContent = "La configuración cambió. Vuelve a analizar.";
        currentSegments = [];
        resetGeneration();
    }
});

clipSeconds.addEventListener("input", () => {
    recalculateClips();

    if (uploadedFilename) {
        segmentsPanel.classList.add("hidden");
        analyzeButton.classList.remove("hidden");
        analysisSummary.textContent = "La configuración cambió. Vuelve a analizar.";
        currentSegments = [];
        resetGeneration();
    }
});

selectAllButton.addEventListener("click", () => {
    document.querySelectorAll(".segment-checkbox").forEach((checkbox) => {
        checkbox.checked = true;
    });

    updateSelectedCount();
});

deselectAllButton.addEventListener("click", () => {
    document.querySelectorAll(".segment-checkbox").forEach((checkbox) => {
        checkbox.checked = false;
    });

    updateSelectedCount();
});

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!selectedFile) {
        setStatus("Selecciona un video antes de continuar.", "error");
        return;
    }

    uploadButton.disabled = true;
    uploadButton.textContent = "Cargando video...";
    setStatus("Copiando el video a la carpeta local del proyecto...");

    const formData = new FormData();
    formData.append("video", selectedFile);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "No se pudo cargar el video.");
        }

        uploadedFilename = data.filename;
        analyzeButton.classList.remove("hidden");
        await loadRecentProjects(data.project_id);

        const toolsReady = data.ffprobe_available && data.ffmpeg_available;
        const toolText = toolsReady
            ? " FFprobe y FFmpeg están disponibles."
            : " FFmpeg/FFprobe no están completamente disponibles en el PATH.";

        setStatus(
            `Video cargado correctamente como ${data.filename}.${toolText}`,
            toolsReady ? "success" : "error"
        );
    } catch (error) {
        setStatus(error.message || "Ocurrió un error al cargar el video.", "error");
    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = "Cargar video al proyecto";
    }
});

analyzeButton.addEventListener("click", async () => {
    if (!uploadedFilename) {
        setStatus("Primero carga el video al proyecto.", "error");
        return;
    }

    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analizando con FFprobe...";
    setStatus("Leyendo metadatos y preparando el plan de cortes...");
    resetGeneration();

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                filename: uploadedFilename,
                intro_seconds: Number(introSeconds.value) || 0,
                clip_seconds: Number(clipSeconds.value) || 30,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "No se pudo analizar el video.");
        }

        renderMetadata(data.metadata);
        renderSegments(data.segments);

        videoDuration.textContent = formatDuration(data.metadata.duration);
        estimatedClips.textContent = String(data.total_segments);
        analysisSummary.textContent = `${data.total_segments} cortes calculados con FFprobe`;
        segmentsPanel.classList.remove("hidden");
        loadRecentProjects();

        ffmpegReady = Boolean(data.ffmpeg_available);
        updateSelectedCount();

        if (!ffmpegReady) {
            generateButton.disabled = true;
            setStatus(
                "Análisis completado, pero FFmpeg no está disponible para generar clips.",
                "error"
            );
        } else {
            setStatus("Análisis completado. Revisa y selecciona los clips que quieras generar.", "success");
        }

        segmentsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
        setStatus(error.message || "Ocurrió un error al analizar el video.", "error");
    } finally {
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analizar cortes con FFprobe";
    }
});

generateButton.addEventListener("click", async () => {
    if (!uploadedFilename || !currentSegments.length || generationInProgress) {
        return;
    }

    const selectedIndexes = [...document.querySelectorAll(".segment-checkbox:checked")]
        .map((checkbox) => Number(checkbox.dataset.index));

    const selectedSegments = currentSegments.filter((segment) =>
        selectedIndexes.includes(segment.index)
    );

    if (!selectedSegments.length) {
        setStatus("Selecciona al menos un clip para generar.", "error");
        return;
    }

    resetGeneration();
    generationProgress.classList.remove("hidden");
    generatedResults.classList.remove("hidden");
    setGenerationControlsDisabled(true);

    generateButton.textContent = "Generando clips...";
    const formatLabel = outputFormat === "vertical"
        ? `Reel 9:16 · ${contentScale.value}% · ${getVerticalPosition()}${brandingEnabled.checked ? " · branding" : ""}`
        : "formato original";

    setStatus(
        `Generando ${selectedSegments.length} ${selectedSegments.length === 1 ? "clip" : "clips"} en ${formatLabel} con FFmpeg...`
    );

    let completed = 0;
    let failed = 0;

    for (let position = 0; position < selectedSegments.length; position += 1) {
        const segment = selectedSegments[position];
        const card = document.querySelector(`[data-segment-index="${segment.index}"]`);

        progressTitle.textContent = outputFormat === "vertical"
            ? `Generando Reel ${String(segment.index).padStart(2, "0")}`
            : `Generando clip ${String(segment.index).padStart(2, "0")}`;
        progressDetail.textContent =
            `${formatDuration(segment.start)} → ${formatDuration(segment.end)}`;

        if (card) {
            card.classList.remove("generated", "failed");
            card.classList.add("generating");
        }

        try {
            const response = await fetch("/generate-clip", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    filename: uploadedFilename,
                    index: segment.index,
                    start: segment.start,
                    end: segment.end,
                    output_format: outputFormat,
                    vertical_scale: Number(contentScale.value) || 100,
                    vertical_position: getVerticalPosition(),
                    blur_strength: Number(blurStrength.value) || 25,
                    branding_enabled: brandingEnabled.checked,
                    branding_title: brandingTitle.value.trim(),
                    branding_handle: brandingHandle.value.trim(),
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `No se pudo generar el clip ${segment.index}.`);
            }

            completed += 1;

            if (card) {
                card.classList.remove("generating");
                card.classList.add("generated");
            }

            renderGeneratedClip(data);

            if (!outputFolder.textContent) {
                outputFolder.textContent = data.output_folder;
            }
        } catch (error) {
            failed += 1;

            if (card) {
                card.classList.remove("generating");
                card.classList.add("failed");
            }

            const errorItem = document.createElement("div");
            errorItem.className = "generated-item generated-error";
            errorItem.textContent =
                `Clip ${String(segment.index).padStart(2, "0")}: ${error.message}`;
            generatedList.appendChild(errorItem);
        }

        const processed = position + 1;
        const percent = Math.round((processed / selectedSegments.length) * 100);

        progressBar.style.width = `${percent}%`;
        progressPercent.textContent = `${percent}%`;
        progressDetail.textContent =
            `${processed} de ${selectedSegments.length} clips procesados`;
    }

    progressTitle.textContent = failed
        ? "Generación finalizada con observaciones"
        : "Generación completada";
    progressDetail.textContent =
        `${completed} correctos · ${failed} con error`;

    generateButton.textContent = "Generar clips seleccionados";
    setGenerationControlsDisabled(false);

    setStatus(
        failed
            ? `Proceso terminado: ${completed} clips generados y ${failed} con error.`
            : `Listo. Se generaron ${completed} clips en ${formatLabel} dentro de outputs/.`,
        failed ? "error" : "success"
    );

    generatedResults.scrollIntoView({ behavior: "smooth", block: "start" });
});


renderPresetOptions("builtin:Reel AnderCode");
loadRecentProjects();
updateThemeControl();
setupWorkflowObserver();
updateVerticalPreviewStyle();
updateBrandingPreview();
updateOutputFormat();
