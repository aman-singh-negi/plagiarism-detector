const dropArea = document.getElementById('drop-area');

// Prevent default drag behaviors
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
});

// Highlight drop area when item is dragged over it
['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false);
});

// Handle dropped files
dropArea.addEventListener('drop', handleDrop, false);

// Add event listeners for manual file selection
const file1 = document.getElementById('file1');
const file2 = document.getElementById('file2');

file1.addEventListener('change', () => updateFileLabel('file1'));
file2.addEventListener('change', () => updateFileLabel('file2'));

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    dropArea.classList.add('highlight');
}

function unhighlight() {
    dropArea.classList.remove('highlight');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length >= 2) {
        // Assign files to inputs
        const file1 = document.getElementById('file1');
        const file2 = document.getElementById('file2');
        
        // Create new DataTransfer object
        const dataTransfer1 = new DataTransfer();
        const dataTransfer2 = new DataTransfer();
        
        dataTransfer1.items.add(files[0]);
        dataTransfer2.items.add(files[1]);
        
        file1.files = dataTransfer1.files;
        file2.files = dataTransfer2.files;
        
        // Update UI
        document.querySelector('label[for="file1"] span').innerHTML = `${files[0].name} <i class='fas fa-check-circle' style='color: var(--success); margin-left: 6px;'></i>`;
        document.querySelector('label[for="file2"] span').innerHTML = `${files[1].name} <i class='fas fa-check-circle' style='color: var(--success); margin-left: 6px;'></i>`;
        
        // Add visual feedback
        const labels = document.querySelectorAll('.file-inputs label');
        labels.forEach(label => {
            label.classList.add('ripple');
            setTimeout(() => label.classList.remove('ripple'), 500);
        });
    } else {
        alert('Please drop exactly 2 files for comparison');
    }
}

function updateFileLabel(fileInputId) {
    const fileInput = document.getElementById(fileInputId);
    const label = document.querySelector(`label[for="${fileInputId}"] span`);
    if (fileInput.files.length > 0) {
        label.innerHTML = `${fileInput.files[0].name} <i class='fas fa-check-circle' style='color: var(--success); margin-left: 6px;'></i>`;
    } else {
        label.textContent = fileInputId === 'file1' ? 'Select File 1' : 'Select File 2';
    }
}