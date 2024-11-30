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
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.getElementById('file-input').addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const content = e.target.result;
            const option = document.getElementById('options').value;
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
