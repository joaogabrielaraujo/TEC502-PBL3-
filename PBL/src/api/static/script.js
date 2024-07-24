function fetchCurrentTime() {
    fetch('/get_clock')
        .then(response => response.json())
        .then(data => {
            document.getElementById('clock').innerText = data.time;
        })
        .catch(error => console.error('Error fetching time:', error));
}

function updateTime() {
    const newTime = document.getElementById('newTime').value;
    fetch('/update_time', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ time: newTime }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Time updated successfully');
        } else {
            alert('Invalid time format');
        }
    })
    .catch(error => console.error('Error updating time:', error));
}

function updateDrift() {
    const newDrift = document.getElementById('newDrift').value;
    fetch('/update_drift', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ drift: newDrift }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Drift updated successfully');
        } else {
            alert('Invalid drift value');
        }
    })
    .catch(error => console.error('Error updating drift:', error));
}

// Update the clock every second
setInterval(fetchCurrentTime, 100);
fetchCurrentTime();
