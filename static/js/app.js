const videoInput = document.getElementById("videoInput");
const dropZone = document.getElementById("dropZone");
const uploadForm = document.getElementById("uploadForm");
const uploadButton = document.getElementById("uploadButton");
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

let selectedFile = null;
let objectUrl = null;

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
    if (!Number.isFinite(seconds)) {
        return "—";
    }

    const total = Math.max(0, Math.floor(seconds));
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

    if (type) {
        uploadStatus.classList.add(type);
    }
}

function isSupportedVideo(file) {
    const allowedExtensions = ["mp4", "mov", "mkv", "webm", "avi"];
    const extension = file.name.split(".").pop()?.toLowerCase();

    return file.type.startsWith("video/") || allowedExtensions.includes(extension);
}

function selectFile(file) {
    if (!file) {
        return;
    }

    if (!isSupportedVideo(file)) {
        setStatus("El archivo seleccionado no parece ser un video compatible.", "error");
        return;
    }

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
introSeconds.addEventListener("input", recalculateClips);
clipSeconds.addEventListener("input", recalculateClips);

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

        setStatus(
            `Video cargado correctamente como ${data.filename}.`,
            "success"
        );
    } catch (error) {
        setStatus(error.message || "Ocurrió un error al cargar el video.", "error");
    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = "Cargar video al proyecto";
    }
});
