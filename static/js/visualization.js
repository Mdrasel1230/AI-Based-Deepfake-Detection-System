// Visualization JavaScript for DeepFake AI Detection application

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize image comparison if available
    initializeImageComparison();
    
    // Initialize heatmap toggle if available
    initializeHeatmapToggle();
});

// Initialize image comparison slider
function initializeImageComparison() {
    const comparisonSlider = document.querySelector('.comparison-slider');
    if (!comparisonSlider) return;
    
    const before = comparisonSlider.querySelector('.comparison-before');
    const after = comparisonSlider.querySelector('.comparison-after');
    const handle = comparisonSlider.querySelector('.comparison-handle');
    
    let isDragging = false;
    
    // Set initial position
    updatePosition(50);
    
    // Handle mouse events
    handle.addEventListener('mousedown', startDrag);
    window.addEventListener('mouseup', stopDrag);
    window.addEventListener('mousemove', drag);
    
    // Handle touch events
    handle.addEventListener('touchstart', startDrag);
    window.addEventListener('touchend', stopDrag);
    window.addEventListener('touchmove', drag);
    
    function startDrag(e) {
        isDragging = true;
        e.preventDefault();
    }
    
    function stopDrag() {
        isDragging = false;
    }
    
    function drag(e) {
        if (!isDragging) return;
        
        let clientX;
        if (e.type === 'touchmove') {
            clientX = e.touches[0].clientX;
        } else {
            clientX = e.clientX;
        }
        
        const rect = comparisonSlider.getBoundingClientRect();
        const position = Math.max(0, Math.min(100, (clientX - rect.left) / rect.width * 100));
        
        updatePosition(position);
    }
    
    function updatePosition(position) {
        after.style.width = `${position}%`;
        handle.style.left = `${position}%`;
    }
}

// Initialize heatmap toggle
function initializeHeatmapToggle() {
    const toggleBtn = document.getElementById('heatmap-toggle');
    if (!toggleBtn) return;
    
    const originalImg = document.getElementById('original-image');
    const heatmapImg = document.getElementById('heatmap-image');
    
    toggleBtn.addEventListener('click', function() {
        if (originalImg.classList.contains('d-none')) {
            // Show original
            originalImg.classList.remove('d-none');
            heatmapImg.classList.add('d-none');
            toggleBtn.textContent = 'Show Heatmap';
            toggleBtn.classList.remove('btn-info');
            toggleBtn.classList.add('btn-outline-info');
        } else {
            // Show heatmap
            originalImg.classList.add('d-none');
            heatmapImg.classList.remove('d-none');
            toggleBtn.textContent = 'Show Original';
            toggleBtn.classList.remove('btn-outline-info');
            toggleBtn.classList.add('btn-info');
        }
    });
}

// Visualize detection results
function visualizeDetection(imageElement, result, confidence) {
    if (!imageElement) return;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = imageElement.width;
    canvas.height = imageElement.height;
    
    // Draw original image
    ctx.drawImage(imageElement, 0, 0, canvas.width, canvas.height);
    
    // Add overlay based on result
    ctx.fillStyle = result ? 'rgba(220, 53, 69, 0.3)' : 'rgba(40, 167, 69, 0.3)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Add text label
    ctx.font = '24px Arial';
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'center';
    ctx.fillText(result ? 'DEEPFAKE' : 'AUTHENTIC', canvas.width / 2, 40);
    
    // Add confidence percentage
    ctx.font = '20px Arial';
    ctx.fillText(`Confidence: ${(confidence * 100).toFixed(2)}%`, canvas.width / 2, 70);
    
    // Replace image with canvas
    const dataURL = canvas.toDataURL();
    imageElement.src = dataURL;
}