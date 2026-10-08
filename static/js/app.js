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
const cancelGenerationButton = document.getElementById("cancelGenerationButton");
const renderEngineSelect = document.getElementById("renderEngineSelect");
const renderEngineHint = document.getElementById("renderEngineHint");
const generationProgress = document.getElementById("generationProgress");
const progressTitle = document.getElementById("progressTitle");
const progressPercent = document.getElementById("progressPercent");
const progressBar = document.getElementById("progressBar");
const progressDetail = document.getElementById("progressDetail");
const progressTiming = document.getElementById("progressTiming");
const generatedResults = document.getElementById("generatedResults");
const generatedList = document.getElementById("generatedList");
const outputFolder = document.getElementById("outputFolder");
const openOutputFolderButton = document.getElementById("openOutputFolderButton");
const generationDescription = document.getElementById("generationDescription");
const outputFormatSummary = document.getElementById("outputFormatSummary");
const outputFormatInputs = [...document.querySelectorAll('input[name="outputFormat"]')];
const verticalSettings = document.getElementById("verticalSettings");
const contentScale = document.getElementById("contentScale");
const contentScaleValue = document.getElementById("contentScaleValue");
const blurStrength = document.getElementById("blurStrength");
const blurStrengthValue = document.getElementById("blurStrengthValue");
const verticalPositionInputs = [...document.querySelectorAll('input[name="verticalPosition"]')];
const basicAccordionSummary = document.getElementById("basicAccordionSummary");
const frameAccordionSummary = document.getElementById("frameAccordionSummary");
const brandingAccordion = document.getElementById("brandingAccordion");
const brandingAccordionSummary = document.getElementById("brandingAccordionSummary");
const hookAccordionSummary = document.getElementById("hookAccordionSummary");
const outroAccordionSummary = document.getElementById("outroAccordionSummary");
const brandingEnabled = document.getElementById("brandingEnabled");
const brandingSettings = document.getElementById("brandingSettings");
const brandingTitle = document.getElementById("brandingTitle");
const brandingHandle = document.getElementById("brandingHandle");
const showSafeZone = document.getElementById("showSafeZone");
const brandingPreview = document.getElementById("brandingPreview");
const brandingTitlePreview = document.getElementById("brandingTitlePreview");
const brandingHandlePreview = document.getElementById("brandingHandlePreview");
const subtitleSafeZone = document.getElementById("subtitleSafeZone");

const hookEnabled = document.getElementById("hookEnabled");
const hookImageInput = document.getElementById("hookImageInput");
const selectHookImageButton = document.getElementById("selectHookImageButton");
const deleteHookImageButton = document.getElementById("deleteHookImageButton");
const hookEmptyState = document.getElementById("hookEmptyState");
const hookProjectHint = document.getElementById("hookProjectHint");
const hookPreviewBox = document.getElementById("hookPreviewBox");
const hookImagePreview = document.getElementById("hookImagePreview");
const hookImageName = document.getElementById("hookImageName");
const hookImageSize = document.getElementById("hookImageSize");
const hookDuration = document.getElementById("hookDuration");
const hookFade = document.getElementById("hookFade");
const hookStatus = document.getElementById("hookStatus");

const outroEnabled = document.getElementById("outroEnabled");
const outroImageInput = document.getElementById("outroImageInput");
const selectOutroImageButton = document.getElementById("selectOutroImageButton");
const deleteOutroImageButton = document.getElementById("deleteOutroImageButton");
const outroEmptyState = document.getElementById("outroEmptyState");
const outroProjectHint = document.getElementById("outroProjectHint");
const outroPreviewBox = document.getElementById("outroPreviewBox");
const outroImagePreview = document.getElementById("outroImagePreview");
const outroImageName = document.getElementById("outroImageName");
const outroImageSize = document.getElementById("outroImageSize");
const outroDuration = document.getElementById("outroDuration");
const outroFade = document.getElementById("outroFade");
const outroStatus = document.getElementById("outroStatus");

let selectedFile = null;
let objectUrl = null;
let uploadedFilename = null;
let activePreviewEnd = null;
let currentSegments = [];
let generationInProgress = false;
let ffmpegReady = false;
let outputFormat = "vertical";
let recentProjects = [];
let activeProjectId = null;
let hookHasImage = false;
let outroHasImage = false;
let activeRenderJobId = null;
let cancelRequested = false;
let renderStartedAt = 0;
let renderTimerId = null;
let processedRenderClips = 0;
let totalRenderClips = 0;

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

    const desiredFormat = settings.output_format || "vertical";
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

    brandingEnabled.checked = settings.branding_enabled !== false;
    brandingHandle.value = settings.branding_handle ?? "anderson-bastidas.com";
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
        activeProjectId = project.id;

        fileName.textContent = project.original_name || project.filename;
        fileSize.textContent = formatBytes(Number(project.size) || 0);
        fileInfo.classList.remove("hidden");

        uploadButton.disabled = true;
        uploadButton.textContent = "Video ya cargado en el proyecto";
        analyzeButton.classList.remove("hidden");

        applySettings(project);
        applyHookProject(project);
        applyOutroProject(project);
        openOutputFolderButton.disabled = !project.output_available;
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

function setHookStatus(message, type = "") {
    hookStatus.textContent = message;
    hookStatus.className = "outro-status";

    if (type) {
        hookStatus.classList.add(type);
    }
}

function refreshHookControlsDisabled(forceDisabled = false) {
    const hasProject = Boolean(activeProjectId);
    const disabled = forceDisabled || !hasProject;

    selectHookImageButton.disabled = disabled;
    hookDuration.disabled = disabled;
    hookFade.disabled = disabled;
    deleteHookImageButton.disabled = disabled || !hookHasImage;
    hookEnabled.disabled = disabled || !hookHasImage;
}

function resetHookProject() {
    hookHasImage = false;
    hookEnabled.checked = false;
    hookDuration.value = 0.5;
    hookFade.checked = true;
    hookImageInput.value = "";
    hookImagePreview.removeAttribute("src");
    hookPreviewBox.classList.add("hidden");
    hookEmptyState.classList.remove("hidden");
    hookProjectHint.textContent = "Carga primero el video al proyecto.";
    hookImageName.textContent = "Imagen de gancho";
    hookImageSize.textContent = "—";
    hookAccordionSummary.textContent = "Sin imagen · 0.5 s";
    refreshHookControlsDisabled();
    setHookStatus("PNG, JPG, JPEG o WEBP · máximo 10 MB.");
}

function applyHookProject(project = {}) {
    activeProjectId = project.id || activeProjectId;
    hookHasImage = Boolean(project.hook_image);

    hookEnabled.checked = Boolean(project.hook_enabled && hookHasImage);
    hookDuration.value = project.hook_duration ?? 0.5;
    hookFade.checked = project.hook_fade !== false;

    if (hookHasImage && project.hook_image_url) {
        hookImagePreview.src =
            `${project.hook_image_url}?v=${encodeURIComponent(project.updated_at || Date.now())}`;
        hookImageName.textContent =
            project.hook_image_original_name || project.hook_image;
        hookImageSize.textContent = formatBytes(
            Number(project.hook_image_size) || 0
        );
        hookPreviewBox.classList.remove("hidden");
        hookEmptyState.classList.add("hidden");
    } else {
        hookImagePreview.removeAttribute("src");
        hookImageName.textContent = "Imagen de gancho";
        hookImageSize.textContent = "—";
        hookPreviewBox.classList.add("hidden");
        hookEmptyState.classList.remove("hidden");
        hookProjectHint.textContent = activeProjectId
            ? "Selecciona una imagen de gancho para este proyecto."
            : "Carga primero el video al proyecto.";
    }

    hookAccordionSummary.textContent = hookHasImage
        ? `${hookEnabled.checked ? "Activo" : "Pausado"} · ${hookDuration.value} s`
        : `Sin imagen · ${hookDuration.value} s`;

    refreshHookControlsDisabled();
    setHookStatus(
        hookHasImage
            ? "El gancho se aplicará al inicio de todos los clips cuando integremos el render final."
            : "PNG, JPG, JPEG o WEBP · máximo 10 MB."
    );
}

async function saveHookSettings() {
    if (!activeProjectId) {
        return false;
    }

    try {
        const response = await fetch(
            `/projects/${encodeURIComponent(activeProjectId)}/hook`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    hook_enabled: hookEnabled.checked,
                    hook_duration: Number(hookDuration.value) || 0.5,
                    hook_fade: hookFade.checked,
                }),
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.message || "No se pudo guardar la configuración del hook."
            );
        }

        applyHookProject(data);
        await loadRecentProjects(activeProjectId);
        setHookStatus("Configuración del hook guardada.", "success");
        return true;
    } catch (error) {
        setHookStatus(
            error.message || "No se pudo guardar la configuración del hook.",
            "error"
        );

        if (!hookHasImage) {
            hookEnabled.checked = false;
        }

        return false;
    }
}

async function uploadHookImage(file) {
    if (!activeProjectId || !file) {
        return;
    }

    const allowedExtensions = ["png", "jpg", "jpeg", "webp"];
    const extension = file.name.split(".").pop()?.toLowerCase();

    if (!allowedExtensions.includes(extension)) {
        setHookStatus("Usa una imagen PNG, JPG, JPEG o WEBP.", "error");
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        setHookStatus("La imagen supera el límite de 10 MB.", "error");
        return;
    }

    selectHookImageButton.disabled = true;
    deleteHookImageButton.disabled = true;
    setHookStatus("Guardando imagen de gancho...");

    const formData = new FormData();
    formData.append("image", file);

    try {
        const response = await fetch(
            `/projects/${encodeURIComponent(activeProjectId)}/hook-image`,
            {
                method: "POST",
                body: formData,
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "No se pudo guardar la imagen.");
        }

        hookImageInput.value = "";
        applyHookProject(data);
        await loadRecentProjects(activeProjectId);
        setHookStatus(
            "Imagen guardada. El hook quedó activado para este proyecto.",
            "success"
        );
    } catch (error) {
        setHookStatus(
            error.message || "No se pudo guardar la imagen de gancho.",
            "error"
        );
        refreshHookControlsDisabled();
    }
}

async function removeHookImage() {
    if (!activeProjectId || !hookHasImage) {
        return;
    }

    if (!window.confirm("¿Eliminar la imagen de gancho de este proyecto?")) {
        return;
    }

    refreshHookControlsDisabled(true);
    setHookStatus("Eliminando imagen de gancho...");

    try {
        const response = await fetch(
            `/projects/${encodeURIComponent(activeProjectId)}/hook-image`,
            { method: "DELETE" }
        );
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "No se pudo eliminar la imagen.");
        }

        applyHookProject(data);
        await loadRecentProjects(activeProjectId);
        setHookStatus(data.message, "success");
    } catch (error) {
        setHookStatus(
            error.message || "No se pudo eliminar la imagen de gancho.",
            "error"
        );
        refreshHookControlsDisabled();
    }
}

function setOutroStatus(message, type = "") {
    outroStatus.textContent = message;
    outroStatus.className = "outro-status";

    if (type) {
        outroStatus.classList.add(type);
    }
}

function refreshOutroControlsDisabled(forceDisabled = false) {
    const hasProject = Boolean(activeProjectId);
    const disabled = forceDisabled || !hasProject;

    selectOutroImageButton.disabled = disabled;
    outroDuration.disabled = disabled;
    outroFade.disabled = disabled;
    deleteOutroImageButton.disabled = disabled || !outroHasImage;
    outroEnabled.disabled = disabled || !outroHasImage;
}

function resetOutroProject() {
    outroHasImage = false;
    outroEnabled.checked = false;
    outroDuration.value = 5;
    outroFade.checked = true;
    outroImageInput.value = "";
    outroImagePreview.removeAttribute("src");
    outroPreviewBox.classList.add("hidden");
    outroEmptyState.classList.remove("hidden");
    outroProjectHint.textContent = "Carga primero el video al proyecto.";
    outroImageName.textContent = "Imagen promocional";
    outroImageSize.textContent = "—";
    outroAccordionSummary.textContent = "Sin imagen · 5 s";
    outroAccordionSummary.textContent = outroHasImage
        ? `${outroEnabled.checked ? "Activo" : "Pausado"} · ${outroDuration.value} s`
        : `Sin imagen · ${outroDuration.value} s`;

    refreshOutroControlsDisabled();
    setOutroStatus(
        "La imagen será silenciosa y específica para este proyecto."
    );
}

function applyOutroProject(project = {}) {
    activeProjectId = project.id || activeProjectId;
    outroHasImage = Boolean(project.outro_image);

    outroEnabled.checked = Boolean(project.outro_enabled && outroHasImage);
    outroDuration.value = project.outro_duration ?? 5;
    outroFade.checked = project.outro_fade !== false;

    if (outroHasImage && project.outro_image_url) {
        outroImagePreview.src =
            `${project.outro_image_url}?v=${encodeURIComponent(project.updated_at || Date.now())}`;
        outroImageName.textContent =
            project.outro_image_original_name || project.outro_image;
        outroImageSize.textContent = formatBytes(
            Number(project.outro_image_size) || 0
        );
        outroPreviewBox.classList.remove("hidden");
        outroEmptyState.classList.add("hidden");
    } else {
        outroImagePreview.removeAttribute("src");
        outroImageName.textContent = "Imagen promocional";
        outroImageSize.textContent = "—";
        outroPreviewBox.classList.add("hidden");
        outroEmptyState.classList.remove("hidden");
        outroProjectHint.textContent = activeProjectId
            ? "Selecciona una imagen específica para este proyecto."
            : "Carga primero el video al proyecto.";
    }

    refreshOutroControlsDisabled();
    setOutroStatus(
        outroHasImage
            ? "La imagen se aplicará a todos los clips cuando integremos el render del outro."
            : "PNG, JPG, JPEG o WEBP · máximo 10 MB."
    );
}

async function saveOutroSettings() {
    if (!activeProjectId) {
        return false;
    }

    try {
        const response = await fetch(
            `/projects/${encodeURIComponent(activeProjectId)}/outro`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    outro_enabled: outroEnabled.checked,
                    outro_duration: Number(outroDuration.value) || 5,
                    outro_fade: outroFade.checked,
                }),
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.message || "No se pudo guardar la configuración del outro."
            );
        }

        applyOutroProject(data);
        await loadRecentProjects(activeProjectId);
        setOutroStatus("Configuración del outro guardada.", "success");
        return true;
    } catch (error) {
        setOutroStatus(
            error.message || "No se pudo guardar la configuración del outro.",
            "error"
        );

        if (!outroHasImage) {
            outroEnabled.checked = false;
        }

        return false;
    }
}

async function uploadOutroImage(file) {
    if (!activeProjectId || !file) {
        return;
    }

    const allowedExtensions = ["png", "jpg", "jpeg", "webp"];
    const extension = file.name.split(".").pop()?.toLowerCase();

    if (!allowedExtensions.includes(extension)) {
        setOutroStatus("Usa una imagen PNG, JPG, JPEG o WEBP.", "error");
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        setOutroStatus("La imagen supera el límite de 10 MB.", "error");
        return;
    }

    selectOutroImageButton.disabled = true;
    deleteOutroImageButton.disabled = true;
    setOutroStatus("Guardando imagen promocional...");

    const formData = new FormData();
    formData.append("image", file);

    try {
        const response = await fetch(
            `/projects/${encodeURIComponent(activeProjectId)}/outro-image`,
            {
                method: "POST",
                body: formData,
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "No se pudo guardar la imagen.");
        }

        outroImageInput.value = "";
        applyOutroProject(data);
        await loadRecentProjects(activeProjectId);
        setOutroStatus(
            "Imagen guardada. El outro quedó activado para este proyecto.",
            "success"
        );
    } catch (error) {
        setOutroStatus(
            error.message || "No se pudo guardar la imagen promocional.",
            "error"
        );
        refreshOutroControlsDisabled();
    }
}

async function removeOutroImage() {
    if (!activeProjectId || !outroHasImage) {
        return;
    }

    if (!window.confirm(
        "¿Eliminar la imagen promocional de este proyecto?"
    )) {
        return;
    }

    refreshOutroControlsDisabled(true);
    setOutroStatus("Eliminando imagen promocional...");

    try {
        const response = await fetch(
            `/projects/${encodeURIComponent(activeProjectId)}/outro-image`,
            { method: "DELETE" }
        );
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "No se pudo eliminar la imagen.");
        }

        applyOutroProject(data);
        await loadRecentProjects(activeProjectId);
        setOutroStatus(data.message, "success");
    } catch (error) {
        setOutroStatus(
            error.message || "No se pudo eliminar la imagen promocional.",
            "error"
        );
        refreshOutroControlsDisabled();
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
    return outputFormatInputs.find((input) => input.checked)?.value || "vertical";
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

    const positionLabel = {
        top: "Arriba",
        center: "Centro",
        bottom: "Abajo",
    }[position] || "Centro";

    frameAccordionSummary.textContent =
        `${scale}% · ${positionLabel} · Blur ${blur}`;

    const previewBlur = Math.max(4, Math.round(blur * 0.72));
    verticalBackground.style.filter =
        `blur(${previewBlur}px) brightness(0.62)`;
}

function balanceBrandingTitle(text, maxChars = 24, maxLines = 3) {
    const cleanText = String(text || "").trim().replace(/\s+/g, " ");

    if (!cleanText) {
        return [];
    }

    const words = cleanText.split(" ");
    const totalChars = cleanText.length;
    const lineCount = Math.max(
        1,
        Math.min(
            maxLines,
            words.length,
            Math.ceil(totalChars / maxChars)
        )
    );

    if (lineCount === 1) {
        return [cleanText];
    }

    const target = totalChars / lineCount;
    let bestLines = null;
    let bestScore = null;

    const evaluate = (lines) => {
        const lengths = lines.map((line) => line.length);
        const overflow = lengths.reduce(
            (total, length) =>
                total + (Math.max(0, length - maxChars) ** 2 * 100),
            0
        );
        const balance = lengths.reduce(
            (total, length) =>
                total + ((length - target) ** 2),
            0
        );
        const spread = (
            Math.max(...lengths) - Math.min(...lengths)
        ) ** 2;
        const score = overflow + balance + spread;

        if (bestScore === null || score < bestScore) {
            bestScore = score;
            bestLines = lines;
        }
    };

    const search = (startIndex, remainingLines, currentLines) => {
        if (remainingLines === 1) {
            const finalLine = words.slice(startIndex).join(" ");

            if (finalLine) {
                evaluate([...currentLines, finalLine]);
            }

            return;
        }

        const maxEnd = words.length - remainingLines + 1;

        for (
            let endIndex = startIndex + 1;
            endIndex <= maxEnd;
            endIndex += 1
        ) {
            const line = words.slice(startIndex, endIndex).join(" ");
            search(
                endIndex,
                remainingLines - 1,
                [...currentLines, line]
            );
        }
    };

    search(0, lineCount, []);

    return bestLines || [cleanText];
}

function updateBrandingPreview() {
    const enabled = brandingEnabled.checked && outputFormat === "vertical";
    const title = brandingTitle.value.trim();
    const handle = brandingHandle.value.trim();

    brandingSettings.classList.toggle("hidden", !brandingEnabled.checked);
    brandingPreview.classList.toggle("hidden", !enabled);

    brandingTitlePreview.textContent = balanceBrandingTitle(title).join("\n");
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

    brandingAccordionSummary.textContent = brandingEnabled.checked
        ? `Activo · ${handle || "Sin firma"}`
        : "Desactivado";

    subtitleSafeZone.classList.toggle("hidden", !showSafeZone.checked);
}

function updateOutputFormat() {
    outputFormat = getOutputFormat();
    const isVertical = outputFormat === "vertical";

    basicAccordionSummary.textContent =
        `${Number(introSeconds.value) || 0} s intro · ${Number(clipSeconds.value) || 30} s clips · ${isVertical ? "Reel 9:16" : "Original"}`;

    verticalPreviewCard.classList.toggle("hidden", !isVertical);
    verticalSettings.classList.toggle("hidden", !isVertical);
    brandingAccordion.classList.toggle("hidden", !isVertical);

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

    basicAccordionSummary.textContent =
        `${intro} s intro · ${clip} s clips · ${getOutputFormat() === "vertical" ? "Reel 9:16" : "Original"}`;

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

function createRenderJobId() {
    if (window.crypto?.randomUUID) {
        return window.crypto.randomUUID();
    }

    return `render-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function formatRenderClock(totalSeconds) {
    const total = Math.max(0, Math.round(totalSeconds));
    const hours = Math.floor(total / 3600);
    const minutes = Math.floor((total % 3600) / 60);
    const seconds = total % 60;

    if (hours > 0) {
        return [
            String(hours),
            String(minutes).padStart(2, "0"),
            String(seconds).padStart(2, "0"),
        ].join(":");
    }

    return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function updateRenderTiming() {
    if (!renderStartedAt) {
        progressTiming.textContent = "";
        return;
    }

    const elapsedSeconds = (performance.now() - renderStartedAt) / 1000;
    let label = `Transcurrido ${formatRenderClock(elapsedSeconds)}`;

    if (processedRenderClips > 0 && totalRenderClips > processedRenderClips) {
        const average = elapsedSeconds / processedRenderClips;
        const remaining = average * (totalRenderClips - processedRenderClips);
        label += ` · Restante aprox. ${formatRenderClock(remaining)}`;
    }

    progressTiming.textContent = label;
}

function startRenderTimer(totalClips) {
    totalRenderClips = totalClips;
    processedRenderClips = 0;
    renderStartedAt = performance.now();
    updateRenderTiming();

    if (renderTimerId) {
        clearInterval(renderTimerId);
    }

    renderTimerId = window.setInterval(updateRenderTiming, 1000);
}

function stopRenderTimer() {
    if (renderTimerId) {
        clearInterval(renderTimerId);
        renderTimerId = null;
    }

    updateRenderTiming();
}

async function loadRenderCapabilities() {
    try {
        const response = await fetch("/render-capabilities");
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "No se pudieron detectar los motores de render.");
        }

        const gpuOption = renderEngineSelect.querySelector('option[value="gpu"]');

        if (gpuOption) {
            gpuOption.disabled = !data.nvenc_available;
            gpuOption.textContent = data.nvenc_available
                ? "NVIDIA NVENC · GPU"
                : "NVIDIA NVENC · no disponible";
        }

        renderEngineHint.textContent = data.nvenc_available
            ? "Auto usará NVIDIA NVENC y hará fallback a CPU si es necesario."
            : "NVENC no está disponible; Auto utilizará CPU.";
    } catch (_error) {
        renderEngineSelect.value = "cpu";
        const gpuOption = renderEngineSelect.querySelector('option[value="gpu"]');

        if (gpuOption) {
            gpuOption.disabled = true;
        }

        renderEngineHint.textContent = "No se pudo detectar NVENC. Se usará CPU.";
    }
}

async function finishRenderJob(jobId) {
    if (!jobId) {
        return;
    }

    try {
        await fetch(`/render-jobs/${encodeURIComponent(jobId)}/finish`, {
            method: "POST",
        });
    } catch (_error) {
        // La limpieza del job no debe bloquear la experiencia del usuario.
    }
}

async function cancelActiveRender() {
    if (!activeRenderJobId || !generationInProgress || cancelRequested) {
        return;
    }

    cancelRequested = true;
    cancelGenerationButton.disabled = true;
    cancelGenerationButton.textContent = "Cancelando...";
    progressTitle.textContent = "Cancelando procesamiento...";
    setStatus("Cancelando el proceso FFmpeg actual...");

    try {
        await fetch(
            `/render-jobs/${encodeURIComponent(activeRenderJobId)}/cancel`,
            { method: "POST" }
        );
    } catch (_error) {
        setStatus(
            "Se solicitó detener la cola. El proceso actual puede tardar unos segundos en finalizar.",
            "error"
        );
    }
}

async function openCurrentOutputFolder() {
    if (!activeProjectId) {
        setStatus("No hay un proyecto activo para abrir.", "error");
        return;
    }

    try {
        const response = await fetch(
            `/projects/${encodeURIComponent(activeProjectId)}/open-output`,
            { method: "POST" }
        );
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "No se pudo abrir la carpeta de resultados.");
        }

        setStatus(data.message, "success");
    } catch (error) {
        setStatus(error.message || "No se pudo abrir la carpeta de resultados.", "error");
    }
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
    progressTiming.textContent = "";
    openOutputFolderButton.disabled = true;
}

function resetAnalysis() {
    uploadedFilename = null;
    activeProjectId = null;
    resetHookProject();
    resetOutroProject();
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
    renderEngineSelect.disabled = disabled;
    refreshHookControlsDisabled(disabled);
    refreshOutroControlsDisabled(disabled);

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
    const durationValue = Number(data.duration);
    const durationLabel = Number.isFinite(durationValue)
        ? `${durationValue.toFixed(Number.isInteger(durationValue) ? 0 : 1)} s`
        : "—";
    const promoLabels = [];

    if (data.hook_enabled) {
        promoLabels.push(`Hook ${data.hook_duration} s`);
    }

    if (data.outro_enabled) {
        promoLabels.push(`Outro ${data.outro_duration} s`);
    }

    meta.textContent = [
        durationLabel,
        formatBytes(data.size),
        formatLabel,
        data.resolution || "—",
        data.encoder_used || "",
        ...promoLabels,
    ].filter(Boolean).join(" · ");

    info.append(name, meta);

    const link = document.createElement("a");
    link.href = `${data.url}?v=${Date.now()}`;
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

selectHookImageButton.addEventListener("click", () => {
    if (!activeProjectId) {
        setHookStatus("Carga primero el video al proyecto.", "error");
        return;
    }

    hookImageInput.click();
});

hookImageInput.addEventListener("change", () => {
    const file = hookImageInput.files[0];

    if (file) {
        uploadHookImage(file);
    }
});

deleteHookImageButton.addEventListener("click", removeHookImage);

hookEnabled.addEventListener("change", saveHookSettings);

hookDuration.addEventListener("change", () => {
    const duration = Number(hookDuration.value);

    if (!Number.isFinite(duration) || duration < 0.2 || duration > 3) {
        setHookStatus(
            "La duración debe estar entre 0.2 y 3 segundos.",
            "error"
        );
        hookDuration.value = 0.5;
        return;
    }

    hookDuration.value = Math.round(duration * 10) / 10;
    saveHookSettings();
});

hookFade.addEventListener("change", saveHookSettings);

selectOutroImageButton.addEventListener("click", () => {
    if (!activeProjectId) {
        setOutroStatus("Carga primero el video al proyecto.", "error");
        return;
    }

    outroImageInput.click();
});

outroImageInput.addEventListener("change", () => {
    const file = outroImageInput.files[0];

    if (file) {
        uploadOutroImage(file);
    }
});

deleteOutroImageButton.addEventListener("click", removeOutroImage);

outroEnabled.addEventListener("change", saveOutroSettings);

outroDuration.addEventListener("change", () => {
    const duration = Number(outroDuration.value);

    if (!Number.isInteger(duration) || duration < 2 || duration > 10) {
        setOutroStatus(
            "La duración debe estar entre 2 y 10 segundos.",
            "error"
        );
        outroDuration.value = Math.min(10, Math.max(2, Math.round(duration || 5)));
        return;
    }

    saveOutroSettings();
});

outroFade.addEventListener("change", saveOutroSettings);

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
        activeProjectId = data.project_id;
        analyzeButton.classList.remove("hidden");
        applyHookProject({
            id: data.project_id,
            hook_enabled: false,
            hook_image: null,
            hook_duration: 0.5,
            hook_fade: true,
        });
        applyOutroProject({
            id: data.project_id,
            outro_enabled: false,
            outro_image: null,
            outro_duration: 5,
            outro_fade: true,
        });
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

cancelGenerationButton.addEventListener("click", cancelActiveRender);
openOutputFolderButton.addEventListener("click", openCurrentOutputFolder);

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

    activeRenderJobId = createRenderJobId();
    cancelRequested = false;
    cancelGenerationButton.classList.remove("hidden");
    cancelGenerationButton.disabled = false;
    cancelGenerationButton.textContent = "Cancelar procesamiento";
    startRenderTimer(selectedSegments.length);

    generateButton.textContent = "Generando clips...";

    const promoSummary = [
        hookEnabled.checked ? `hook ${hookDuration.value}s` : "",
        outroEnabled.checked ? `outro ${outroDuration.value}s` : "",
    ].filter(Boolean).join(" · ");

    const engineLabel = renderEngineSelect.options[
        renderEngineSelect.selectedIndex
    ]?.textContent || "Auto";

    const formatLabel = outputFormat === "vertical"
        ? `Reel 9:16 · ${contentScale.value}% · ${getVerticalPosition()}${brandingEnabled.checked ? " · branding" : ""}${promoSummary ? ` · ${promoSummary}` : ""}`
        : `formato original${promoSummary ? ` · ${promoSummary}` : ""}`;

    setStatus(
        `Generando ${selectedSegments.length} ${selectedSegments.length === 1 ? "clip" : "clips"} en ${formatLabel} · ${engineLabel}...`
    );

    let completed = 0;
    let failed = 0;
    let attempted = 0;

    try {
        for (let position = 0; position < selectedSegments.length; position += 1) {
            if (cancelRequested) {
                break;
            }

            const segment = selectedSegments[position];
            const card = document.querySelector(
                `[data-segment-index="${segment.index}"]`
            );

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
                        encoder_mode: renderEngineSelect.value,
                        job_id: activeRenderJobId,
                    }),
                });

                const data = await response.json();

                if (!response.ok) {
                    const error = new Error(
                        data.message || `No se pudo generar el clip ${segment.index}.`
                    );
                    error.detail = data.detail || "";
                    error.status = response.status;
                    throw error;
                }

                completed += 1;
                attempted += 1;
                processedRenderClips = attempted;

                if (card) {
                    card.classList.remove("generating");
                    card.classList.add("generated");
                }

                renderGeneratedClip(data);
                openOutputFolderButton.disabled = false;

                if (!outputFolder.textContent) {
                    outputFolder.textContent = data.output_folder;
                }
            } catch (error) {
                const wasCancelled =
                    cancelRequested ||
                    error.status === 409 ||
                    /cancelado/i.test(error.message || "");

                if (card) {
                    card.classList.remove("generating");

                    if (!wasCancelled) {
                        card.classList.add("failed");
                    }
                }

                if (wasCancelled) {
                    cancelRequested = true;
                    break;
                }

                failed += 1;
                attempted += 1;
                processedRenderClips = attempted;

                const errorItem = document.createElement("div");
                errorItem.className = "generated-item generated-error";

                const errorTitle = document.createElement("div");
                errorTitle.textContent =
                    `Clip ${String(segment.index).padStart(2, "0")}: ${error.message}`;
                errorItem.appendChild(errorTitle);

                if (error.detail) {
                    const details = document.createElement("details");
                    details.className = "ffmpeg-error-detail";

                    const summary = document.createElement("summary");
                    summary.textContent = "Ver detalle técnico de FFmpeg";

                    const pre = document.createElement("pre");
                    pre.textContent = error.detail;

                    details.append(summary, pre);
                    errorItem.appendChild(details);
                }

                generatedList.appendChild(errorItem);
            }

            const processed = completed + failed;
            const percent = Math.round(
                (processed / selectedSegments.length) * 100
            );

            progressBar.style.width = `${percent}%`;
            progressPercent.textContent = `${percent}%`;
            progressDetail.textContent =
                `${processed} de ${selectedSegments.length} clips procesados`;
            updateRenderTiming();
        }
    } finally {
        stopRenderTimer();
        await finishRenderJob(activeRenderJobId);
    }

    const wasCancelled = cancelRequested;

    if (wasCancelled) {
        progressTitle.textContent = "Generación cancelada";
        progressDetail.textContent =
            `${completed} generados · ${failed} con error · cola detenida`;
    } else {
        progressTitle.textContent = failed
            ? "Generación finalizada con observaciones"
            : "Generación completada";
        progressDetail.textContent =
            `${completed} correctos · ${failed} con error`;
        progressBar.style.width = "100%";
        progressPercent.textContent = "100%";
    }

    generateButton.textContent = "Generar clips seleccionados";
    cancelGenerationButton.classList.add("hidden");
    cancelGenerationButton.disabled = false;
    cancelGenerationButton.textContent = "Cancelar procesamiento";
    activeRenderJobId = null;
    setGenerationControlsDisabled(false);

    if (wasCancelled) {
        setStatus(
            `Proceso cancelado. Se alcanzaron a generar ${completed} clips.`
        );
    } else {
        setStatus(
            failed
                ? `Proceso terminado: ${completed} clips generados y ${failed} con error.`
                : `Listo. Se generaron ${completed} clips en ${formatLabel} dentro de outputs/.`,
            failed ? "error" : "success"
        );
    }

    generatedResults.scrollIntoView({ behavior: "smooth", block: "start" });
});


renderPresetOptions("builtin:Reel AnderCode");
resetHookProject();
resetOutroProject();
loadRecentProjects();
loadRenderCapabilities();
updateThemeControl();
setupWorkflowObserver();
updateVerticalPreviewStyle();
updateBrandingPreview();
updateOutputFormat();
