// Main JavaScript for DeepFake AI Detection application

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Media upload preview
    const mediaInput = document.getElementById('media');
    if (mediaInput) {
        mediaInput.addEventListener('change', previewFile);
        
        // Setup drag and drop for upload area
        const uploadArea = document.getElementById('upload-area');
        if (uploadArea) {
            uploadArea.addEventListener('click', function() {
                mediaInput.click();
            });
            
            // Drag and drop events
            uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                uploadArea.classList.add('upload-area-active');
            });
            
            uploadArea.addEventListener('dragleave', function() {
                uploadArea.classList.remove('upload-area-active');
            });
            
            uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                uploadArea.classList.remove('upload-area-active');
                
                if (e.dataTransfer.files.length) {
                    mediaInput.files = e.dataTransfer.files;
                    // Trigger change event to preview the file
                    const event = new Event('change');
                    mediaInput.dispatchEvent(event);
                }
            });
        }
    }
    
    // Initialize charts if they exist on the page
    initializeCharts();
});

// Preview uploaded file
function previewFile(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const previewContainer = document.getElementById('preview-container');
    const previewText = document.getElementById('preview-text');
    
    if (!previewContainer || !previewText) return;
    
    // Clear existing preview
    previewContainer.innerHTML = '';
    
    // Update preview text
    previewText.textContent = `Selected file: ${file.name} (${formatFileSize(file.size)})`;
    
    if (file.type.startsWith('image/')) {
        // Preview image
        const img = document.createElement('img');
        img.classList.add('img-fluid', 'upload-preview');
        previewContainer.appendChild(img);
        
        const reader = new FileReader();
        reader.onload = function(e) {
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    } else if (file.type.startsWith('video/')) {
        // Preview video
        const video = document.createElement('video');
        video.classList.add('img-fluid', 'upload-preview');
        video.controls = true;
        previewContainer.appendChild(video);
        
        const reader = new FileReader();
        reader.onload = function(e) {
            video.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Initialize charts
function initializeCharts() {
    // History page chart
    const historyChart = document.getElementById('historyChart');
    if (historyChart) {
        const realCount = parseInt(historyChart.getAttribute('data-real') || '0');
        const fakeCount = parseInt(historyChart.getAttribute('data-fake') || '0');
        
        new Chart(historyChart, {
            type: 'doughnut',
            data: {
                labels: ['Authentic Media', 'Deepfakes'],
                datasets: [{
                    data: [realCount, fakeCount],
                    backgroundColor: ['rgba(40, 167, 69, 0.7)', 'rgba(220, 53, 69, 0.7)'],
                    borderColor: ['rgba(40, 167, 69, 1)', 'rgba(220, 53, 69, 1)'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Authentic vs Deepfake Media'
                    }
                }
            }
        });
    }
}