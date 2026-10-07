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
const videoPreview = document.getElementById("videoPreview");

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

let selectedFile = null;
let objectUrl = null;
let uploadedFilename = null;
let activePreviewEnd = null;

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

function formatDuration(seconds, includeMillis = false) {
    if (!Number.isFinite(Number(seconds))) {
        return "—";
    }

    const numeric = Math.max(0, Number(seconds));
    const total = Math.floor(numeric);
    const hours = Math.floor(total / 3600);
    const minutes = Math.floor((total % 3600) / 60);
    const secs = total % 60;

    const base = hours > 0
        ? [hours, minutes, secs].map((value) => String(value).padStart(2, "0")).join(":")
        : [minutes, secs].map((value) => String(value).padStart(2, "0")).join(":");

    if (!includeMillis) {
        return base;
    }

    const millis = Math.round((numeric - total) * 1000);
    return millis > 0 ? `${base}.${String(millis).padStart(3, "0")}` : base;
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

    if (type) {
        uploadStatus.classList.add(type);
    }
}

function isSupportedVideo(file) {
    const allowedExtensions = ["mp4", "mov", "mkv", "webm", "avi"];
    const extension = file.name.split(".").pop()?.toLowerCase();

    return file.type.startsWith("video/") || allowedExtensions.includes(extension);
}

function resetAnalysis() {
    uploadedFilename = null;
    analyzeButton.classList.add("hidden");
    segmentsPanel.classList.add("hidden");
    metadataGrid.innerHTML = "";
    segmentsList.innerHTML = "";
    analysisSummary.textContent = "Esperando análisis";
    activePreviewEnd = null;
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
    fileInfo.classList.remove("hidden");
    uploadButton.disabled = false;
    setStatus("");

    if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
    }

    objectUrl = URL.createObjectURL(file);
    videoPreview.src = objectUrl;
    videoPreview.classList.remove("hidden");
    previewPlaceholder.classList.add("hidden");
    videoPreview.load();
}

function renderMetadata(metadata) {
    const items = [
        ["Duración", formatDuration(metadata.duration, true)],
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

function renderSegments(segments) {
    segmentsCount.textContent = `${segments.length} ${segments.length === 1 ? "clip" : "clips"}`;

    if (!segments.length) {
        segmentsList.innerHTML = `
            <div class="empty-segments">
                No hay duración útil después de eliminar la intro.
            </div>
        `;
        return;
    }

    segmentsList.innerHTML = segments.map((segment) => `
        <article class="segment-card">
            <label class="segment-check">
                <input type="checkbox" class="segment-checkbox" data-index="${segment.index}" checked>
                <span>Clip ${String(segment.index).padStart(2, "0")}</span>
            </label>

            <div class="segment-time">
                <strong>${formatDuration(segment.start, true)}</strong>
                <span>→</span>
                <strong>${formatDuration(segment.end, true)}</strong>
            </div>

            <span class="segment-duration">${formatDuration(segment.duration, true)}</span>

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
}

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

videoPreview.addEventListener("loadedmetadata", recalculateClips);
videoPreview.addEventListener("timeupdate", () => {
    if (activePreviewEnd !== null && videoPreview.currentTime >= activePreviewEnd) {
        videoPreview.pause();
        activePreviewEnd = null;
    }
});

introSeconds.addEventListener("input", () => {
    recalculateClips();

    if (uploadedFilename) {
        segmentsPanel.classList.add("hidden");
        analyzeButton.classList.remove("hidden");
        analysisSummary.textContent = "La configuración cambió. Vuelve a analizar.";
    }
});

clipSeconds.addEventListener("input", () => {
    recalculateClips();

    if (uploadedFilename) {
        segmentsPanel.classList.add("hidden");
        analyzeButton.classList.remove("hidden");
        analysisSummary.textContent = "La configuración cambió. Vuelve a analizar.";
    }
});

selectAllButton.addEventListener("click", () => {
    document.querySelectorAll(".segment-checkbox").forEach((checkbox) => {
        checkbox.checked = true;
    });
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

        const ffprobeText = data.ffprobe_available
            ? " FFprobe está disponible."
            : " FFprobe aún no está disponible en el PATH.";

        setStatus(
            `Video cargado correctamente como ${data.filename}.${ffprobeText}`,
            data.ffprobe_available ? "success" : "error"
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

        setStatus("Análisis completado. Revisa los fragmentos antes de cortar.", "success");
        segmentsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
        setStatus(error.message || "Ocurrió un error al analizar el video.", "error");
    } finally {
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analizar cortes con FFprobe";
    }
});
