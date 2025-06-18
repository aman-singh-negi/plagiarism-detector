function renderHeatmap(data) {
    const container = document.getElementById('heatmap');
    container.innerHTML = '';
    
    if (!data || data.length === 0) {
        container.innerHTML = '<p class="no-data">No heatmap data available</p>';
        return;
    }
    
    // Create a grid of cells based on the similarity data
    data.forEach((row, i) => {
        row.forEach((value, j) => {
            const cell = document.createElement('div');
            cell.className = 'heatmap-cell';
            cell.style.backgroundColor = `rgba(67, 97, 238, ${value})`;
            cell.title = `Similarity: ${(value * 100).toFixed(1)}%`;
            
            // Add animation
            cell.style.opacity = '0';
            cell.style.transform = 'scale(0.8)';
            
            setTimeout(() => {
                cell.style.opacity = '1';
                cell.style.transform = 'scale(1)';
                cell.style.transition = 'all 0.3s ease';
            }, (i + j) * 50);
            
            container.appendChild(cell);
        });
    });
}

// Add hover effect for heatmap cells
document.addEventListener('mouseover', (e) => {
    if (e.target.classList.contains('heatmap-cell')) {
        e.target.style.transform = 'scale(1.1)';
        e.target.style.zIndex = '1';
        e.target.style.boxShadow = '0 0 10px rgba(0,0,0,0.2)';
    }
});

document.addEventListener('mouseout', (e) => {
    if (e.target.classList.contains('heatmap-cell')) {
        e.target.style.transform = 'scale(1)';
        e.target.style.zIndex = '0';
        e.target.style.boxShadow = 'none';
    }
});