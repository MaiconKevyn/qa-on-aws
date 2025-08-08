document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const fileSelected = document.getElementById('fileSelected');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFile = document.getElementById('removeFile');
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');
    const uploadBtnText = document.querySelector('.upload-btn-text');
    const uploadBtnLoading = document.querySelector('.upload-btn-loading');

    let selectedFile = null;

    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    removeFile.addEventListener('click', () => {
        clearFileSelection();
    });

    uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (selectedFile) {
            uploadFile();
        }
    });

    function handleFileSelection(file) {
        if (!validateFile(file)) {
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        
        dropZone.style.display = 'none';
        fileSelected.style.display = 'block';
        uploadBtn.disabled = false;
        
        clearMessages();
    }

    function validateFile(file) {
        if (file.type !== 'application/pdf') {
            showError('Por favor, selecione apenas arquivos PDF.');
            return false;
        }

        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            showError('Arquivo muito grande. Tamanho máximo permitido: 10MB.');
            return false;
        }

        if (file.size === 0) {
            showError('Arquivo está vazio.');
            return false;
        }

        return true;
    }

    function clearFileSelection() {
        selectedFile = null;
        fileInput.value = '';
        dropZone.style.display = 'block';
        fileSelected.style.display = 'none';
        uploadBtn.disabled = true;
        progressContainer.style.display = 'none';
        clearMessages();
        resetUploadButton();
    }

    function uploadFile() {
        if (!selectedFile) return;

        const formData = new FormData();
        formData.append('file', selectedFile);

        uploadBtn.disabled = true;
        uploadBtnText.style.display = 'none';
        uploadBtnLoading.style.display = 'flex';
        progressContainer.style.display = 'block';
        clearMessages();

        simulateProgress();

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            progressFill.style.width = '100%';
            progressText.textContent = '100%';
            
            setTimeout(() => {
                if (data.success) {
                    showSuccess(`Arquivo "${data.data.original_filename}" enviado com sucesso para o S3!`);
                    setTimeout(() => {
                        clearFileSelection();
                    }, 3000);
                } else {
                    showError(data.message || 'Erro ao enviar arquivo.');
                    resetUploadButton();
                }
            }, 500);
        })
        .catch(error => {
            console.error('Erro no upload:', error);
            showError('Erro de conexão. Tente novamente.');
            resetUploadButton();
            progressContainer.style.display = 'none';
        });
    }

    function simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) {
                progress = 90;
                clearInterval(interval);
            }
            progressFill.style.width = progress + '%';
            progressText.textContent = Math.round(progress) + '%';
        }, 200);
    }

    function resetUploadButton() {
        uploadBtn.disabled = false;
        uploadBtnText.style.display = 'block';
        uploadBtnLoading.style.display = 'none';
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function showSuccess(message) {
        clearMessages();
        successMessage.textContent = message;
        successMessage.style.display = 'block';
    }

    function showError(message) {
        clearMessages();
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    function clearMessages() {
        successMessage.style.display = 'none';
        errorMessage.style.display = 'none';
    }
});