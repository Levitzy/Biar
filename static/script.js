// User Management & Initial Setup
let currentUser = localStorage.getItem('username');
const usernameModal = document.getElementById('username-modal');
const leaderboardData = JSON.parse(localStorage.getItem('leaderboard')) || [];
const decryptHistory = JSON.parse(localStorage.getItem('decryptHistory')) || {};

// Initialize user's history if not exists
if (!decryptHistory[currentUser]) {
    decryptHistory[currentUser] = [];
}

if (currentUser) {
    updateUserDisplay();
    hideUsernameModal();
    updateHistory();
    updateLeaderboard();
} else {
    showUsernameModal();
}

// Username handling functions
function showUsernameModal() {
    usernameModal.classList.remove('hidden');
}

function hideUsernameModal() {
    usernameModal.classList.add('hidden');
}

function updateUserDisplay() {
    const userDisplay = document.getElementById('current-user');
    userDisplay.textContent = `Current User: ${currentUser}`;
}

function saveUsername(username) {
    currentUser = username;
    localStorage.setItem('username', username);
    if (!decryptHistory[username]) {
        decryptHistory[username] = [];
    }
    updateUserDisplay();
    updateLeaderboard();
    hideUsernameModal();
}

// Leaderboard functions
function updateLeaderboard() {
    const leaderboardBody = document.getElementById('leaderboard-body');
    const userStats = {};

    // Calculate stats for each user
    Object.entries(decryptHistory).forEach(([user, history]) => {
        const stats = history.reduce((acc, entry) => {
            acc.total++;
            acc.extensions[entry.type] = (acc.extensions[entry.type] || 0) + 1;
            return acc;
        }, { total: 0, extensions: {} });

        userStats[user] = {
            decryptions: stats.total,
            topExtension: Object.entries(stats.extensions)
                .sort((a, b) => b[1] - a[1])[0]?.[0] || 'None'
        };
    });

    // Sort users by decryption count
    const sortedUsers = Object.entries(userStats)
        .sort((a, b) => b[1].decryptions - a[1].decryptions);

    // Update leaderboard HTML
    leaderboardBody.innerHTML = sortedUsers
        .map(([user, stats], index) => `
            <tr class="border-b hover:bg-gray-50">
                <td class="py-3">${index + 1}</td>
                <td class="py-3">${user}</td>
                <td class="py-3">${stats.decryptions}</td>
                <td class="py-3">${stats.topExtension}</td>
            </tr>
        `).join('');
}

// History functions
function addToHistory(type, content, result) {
    const historyEntry = {
        type,
        content,
        result,
        timestamp: new Date().toISOString()
    };
    
    decryptHistory[currentUser].unshift(historyEntry);
    if (decryptHistory[currentUser].length > 10) {
        decryptHistory[currentUser].pop();
    }
    
    localStorage.setItem('decryptHistory', JSON.stringify(decryptHistory));
    updateHistory();
    updateLeaderboard();
}

function updateHistory() {
    const historyContainer = document.getElementById('history-container');
    const userHistory = decryptHistory[currentUser] || [];
    
    historyContainer.innerHTML = userHistory
        .map(entry => `
            <div class="bg-gray-50 p-4 rounded-lg">
                <div class="flex justify-between items-center mb-2">
                    <span class="font-medium">${entry.type}</span>
                    <span class="text-sm text-gray-500">
                        ${new Date(entry.timestamp).toLocaleString()}
                    </span>
                </div>
                <div class="text-sm text-gray-600 truncate">${entry.result}</div>
            </div>
        `).join('');
}

// Event Listeners
document.getElementById('save-username').addEventListener('click', () => {
    const usernameInput = document.getElementById('username-input');
    if (usernameInput.value.trim()) {
        saveUsername(usernameInput.value.trim());
        hideUsernameModal();
    }
});

document.getElementById('change-username').addEventListener('click', showUsernameModal);

document.getElementById('options').addEventListener('change', function() {
    const decryptSection = document.getElementById('decrypt-section');
    const fileSection = document.getElementById('file-section');
    const resultContainer = document.getElementById('result-container');
    const copyPayloadButton = document.getElementById('copy-payload-button');
    
    decryptSection.classList.add('hidden');
    fileSection.classList.add('hidden');
    resultContainer.classList.add('hidden');
    copyPayloadButton.classList.add('hidden');
    resultContainer.classList.remove('visible');
    
    if (['armod-vpn', 'netmod-syna', 'sockshttp', 'opentunnel'].includes(this.value)) {
        copyPayloadButton.classList.remove('hidden');
    }
    
    if (this.value === 'armod-vpn') {
        decryptSection.classList.remove('hidden');
    } else if (['netmod-syna', 'sockshttp', 'opentunnel'].includes(this.value)) {
        fileSection.classList.remove('hidden');
    }
});

document.getElementById('decrypt-button').addEventListener('click', function() {
    const encryptedContent = document.getElementById('encrypted-content').value;
    fetch('/decrypt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ encryptedContent })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').textContent = data.result;
        const resultContainer = document.getElementById('result-container');
        resultContainer.classList.remove('hidden');
        resultContainer.classList.add('visible');
        addToHistory('armod-vpn', encryptedContent, data.result);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.getElementById('file-input').addEventListener('change', function() {
    const file = this.files[0];
    const option = document.getElementById('options').value;
    
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const content = e.target.result;
            let endpoint;
            
            if (option === 'sockshttp') {
                endpoint = '/file_sockshttp';
            } else if (option === 'opentunnel') {
                endpoint = '/file_opentunnel';
            } else if (option === 'netmod-syna') {
                endpoint = '/decrypt-file';
            } else {
                endpoint = '/decrypt-file';
            }
            
            fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ fileContent: content })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').textContent = data.result;
                const resultContainer = document.getElementById('result-container');
                resultContainer.classList.remove('hidden');
                resultContainer.classList.add('visible');
                addToHistory(option, file.name, data.result);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        };
        reader.readAsText(file);
    }
});

document.getElementById('copy-payload-button').addEventListener('click', function() {
    const resultText = document.getElementById('result').textContent;
    let payloadMatch;
    
    switch (document.getElementById('options').value) {
        case 'armod-vpn':
            payloadMatch = resultText.match(/payload=(.*?)(\n|$)/);
            break;
        case 'netmod-syna':
            payloadMatch = resultText.match(/\[<\/>\] \[Value\]: (.*?)(\n|$)/);
            break;
        case 'sockshttp':
            payloadMatch = resultText.match(/\[<\/>\] \[Proxy Payload\] (.*?)(\n|$)/) ||
                           resultText.match(/\[<\/>\] \[SSH Direct Payload\] (.*?)(\n|$)/) ||
                           resultText.match(/\[<\/>\] \[SSL Payload\] (.*?)(\n|$)/);
            break;
        case 'opentunnel':
            payloadMatch = resultText.match(/\[<\/>\] \[proxyPayload\]= (.*?)(\n|$)/);
            break;
    }
    
    if (payloadMatch) {
        const payload = payloadMatch[1];
        navigator.clipboard.writeText(payload).then(() => {
            alert('Payload copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy payload: ', err);
        });
    } else {
        alert('Payload not found!');
    }
});

