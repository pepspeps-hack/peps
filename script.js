document.addEventListener('DOMContentLoaded', () => {
    const menuImageUpload = document.getElementById('menu-image-upload');
    const targetLanguageSelect = document.getElementById('target-language');
    const processMenuButton = document.getElementById('process-menu-button');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessageElement = document.getElementById('error-message');
    const errorMessageTextElement = errorMessageElement.querySelector('span');
    const menuItemsContainer = document.getElementById('menu-items-container');
    const fileNameDisplay = document.getElementById('file-name-display');

    const OPENROUTER_API_KEY = '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'; // Jouw API Key
    const OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions';

    menuImageUpload.addEventListener('change', () => {
        if (menuImageUpload.files.length > 0) {
            fileNameDisplay.textContent = menuImageUpload.files[0].name;
        } else {
            fileNameDisplay.textContent = 'Geen bestand gekozen';
        }
    });

    processMenuButton.addEventListener('click', async () => {
        const files = menuImageUpload.files;
        if (files.length === 0) {
            showError("Selecteer alstublieft een afbeelding van het menu.");
            return;
        }

        const targetLanguage = targetLanguageSelect.value;
        const imageFile = files[0];

        clearResults();
        showLoading(true);

        try {
            // Stap 1: OCR
            console.log("Attempting OCR...");
            const ocrText = await performOcr(imageFile);
            console.log("OCR Result:", ocrText);

            if (!ocrText || ocrText.trim() === "") {
                showError("Kon geen tekst uit de afbeelding extraheren. Probeer een duidelijkere foto.");
                showLoading(false); // Stop loading als OCR faalt
                return;
            }

            // Stap 2: Parse menu items
            const menuItems = parseMenuItems(ocrText);
            if (menuItems.length === 0) {
                showError("Kon geen individuele menu-items vinden in de tekst.");
                showLoading(false); // Stop loading als parsen faalt
                return;
            }
            console.log("Parsed Menu Items:", menuItems);

            // Stap 3 & 4: Verwerk elk menu item (tekstverwerking & beeldgeneratie)
            for (const itemText of menuItems) {
                console.log(`Processing item: ${itemText}`);
                const processedTextData = await processSingleMenuItemWithGemini(itemText, targetLanguage);

                let imageUrl = `https://via.placeholder.com/300x200.png?text=Beeld+voor+${(processedTextData.vertaald_naam || itemText).replace(/\s+/g, '+')}`;

                if (processedTextData && processedTextData.uitleg && !processedTextData.uitleg.startsWith("Fout bij verwerken") && !processedTextData.uitleg.startsWith("Kon niet verwerken")) {
                    try {
                        console.log(`Attempting image generation for: ${processedTextData.vertaald_naam || itemText}`);
                        imageUrl = await generateImageWithQwen(processedTextData);
                    } catch (imgError) {
                        console.error("Kon afbeelding niet genereren voor:", processedTextData.vertaald_naam, imgError);
                    }
                } else {
                    console.log(`Skipping image generation for "${itemText}" due to previous processing error or placeholder data.`);
                }

                displayMenuItem({
                    ...processedTextData,
                    image_url: imageUrl
                });
            }

        } catch (error) {
            console.error("Fout tijdens hoofdverwerking:", error);
            showError(`Er is een fout opgetreden: ${error.message}`);
        } finally {
            showLoading(false);
        }
    });

    // --- Functies voor AI interactie ---

    function imageToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    }

    async function performOcr(imageFile) {
        console.log("Starting OCR with Gemini...");
        const base64Image = await imageToBase64(imageFile);
        const payload = {
            model: "google/gemini-2.0-flash-exp:free",
            messages: [
                {
                    role: "user",
                    content: [
                        { type: "text", text: "Extraheer alle tekst van deze afbeelding van een menukaart. Geef alleen de herkende tekst terug, zonder extra opmerkingen of uitleg." },
                        { type: "image_url", image_url: { url: base64Image } }
                    ]
                }
            ],
            max_tokens: 2000
        };

        try {
            console.log("performOcr: Fetch call starten...");
            const response = await fetch(OPENROUTER_API_URL, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${OPENROUTER_API_KEY}`, 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            console.log("performOcr: Fetch response status:", response.status);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: "Kon error JSON niet parsen" }));
                console.error("performOcr: API Error Data:", errorData);
                throw new Error(`OCR API request failed with status ${response.status}: ${response.statusText}. Details: ${errorData.error ? JSON.stringify(errorData.error) : 'Geen details'}`);
            }
            const data = await response.json();
            console.log("performOcr: API Response Data:", JSON.stringify(data, null, 2));
            if (data.choices && data.choices.length > 0 && data.choices[0].message && data.choices[0].message.content) {
                return data.choices[0].message.content.trim();
            } else {
                throw new Error("Geen geldige tekst ontvangen van OCR API.");
            }
        } catch (error) {
            console.error("performOcr: Fout in try-catch block:", error);
            throw error;
        }
    }

    function parseMenuItems(ocrText) {
        return ocrText.split('\n').map(line => line.trim()).filter(line => line.length > 2); // Iets langere regels om ruis te filteren
    }

    async function processSingleMenuItemWithGemini(itemText, targetLanguage) {
        console.log(`Processing item "${itemText}" with Gemini Flash for language: ${targetLanguage}`);
        const systemPrompt = `Je bent een gespecialiseerde AI-assistent voor het analyseren en uitleggen van restaurantmenu-items. Antwoord ALTIJD in een valide JSON-object. De structuur: {"original_name": "...", "vertaald_naam": "...", "uitleg": "...", "ingredienten": ["..."], "keuken": "..."}. Extraheer info alleen uit de item tekst. Als een veld niet ingevuld kan worden, laat de string leeg of geef een lege array.`;
        const userPrompt = `Analyseer het menu-item: "${itemText}". Doeltaal: ${targetLanguage}. Retourneer als JSON.`;
        const payload = {
            model: "google/gemini-2.0-flash-exp:free",
            response_format: { type: "json_object" },
            messages: [ { role: "system", content: systemPrompt }, { role: "user", content: userPrompt } ],
            temperature: 0.5, max_tokens: 500,
        };

        try {
            const response = await fetch(OPENROUTER_API_URL, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${OPENROUTER_API_KEY}`, 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                console.error("Gemini API Error Data (Text Processing):", errorData);
                throw new Error(`Gemini (Text Processing) API request failed: ${response.status}. Details: ${errorData ? JSON.stringify(errorData.error) : 'Geen details'}`);
            }
            const data = await response.json();
            console.log(`Gemini API Response for "${itemText}" (Text Processing):`, data);
            if (data.choices && data.choices.length > 0 && data.choices[0].message && data.choices[0].message.content) {
                let contentStr = data.choices[0].message.content;
                if (contentStr.startsWith("```json")) { contentStr = contentStr.substring(7, contentStr.length - 3).trim(); }
                else if (contentStr.startsWith("```")) { contentStr = contentStr.substring(3, contentStr.length - 3).trim(); }
                const jsonResponse = JSON.parse(contentStr);
                if (typeof jsonResponse.original_name === 'undefined' || typeof jsonResponse.vertaald_naam === 'undefined' ||
                    typeof jsonResponse.uitleg === 'undefined' || typeof jsonResponse.ingredienten === 'undefined') {
                    console.warn("Gemini response mist verwachte JSON velden:", jsonResponse);
                    return { original_name: itemText, vertaald_naam: `Kon niet verwerken: ${itemText}`, uitleg: "Fout bij parsen (missende velden).", ingredienten: [], keuken: "" };
                }
                return jsonResponse;
            } else {
                throw new Error("Geen geldige content van Gemini API (Text Processing).");
            }
        } catch (error) {
            console.error(`Fout tijdens Gemini API call for "${itemText}" (Text Processing):`, error);
            return { original_name: itemText, vertaald_naam: `Fout bij verwerken: ${itemText}`, uitleg: error.message, ingredienten: [], keuken: "" };
        }
    }

    async function generateImageWithQwen(processedTextData) {
        const { vertaald_naam, original_name, keuken, ingredienten } = processedTextData;
        console.log(`Generating image for "${vertaald_naam}" with Qwen...`);
        const garnituur = "een passende garnering";
        const ingredientenString = ingredienten ? ingredienten.join(', ') : 'onbekende ingrediënten';
        const imagePromptText = `Generate a high-quality food photography image of "${vertaald_naam}" (Original: "${original_name}"), a traditional ${keuken || 'dish'} made with ${ingredientenString}. The dish is served on a clean white plate, with ${garnituur}, in a well-lit restaurant setting. Professional food photography style, hyper-realistic, 4K resolution.`;
        const payload = {
            model: "qwen/qwq-32b:free",
            messages: [ { role: "user", content: imagePromptText } ],
            max_tokens: 250
        };

        try {
            const response = await fetch(OPENROUTER_API_URL, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${OPENROUTER_API_KEY}`, 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                console.error("Qwen Image Gen API Error Data:", errorData);
                throw new Error(`Qwen Image Gen API request failed: ${response.status}. Details: ${errorData ? JSON.stringify(errorData.error) : 'Geen details'}`);
            }
            const data = await response.json();
            console.log(`Qwen Image Gen API Response for "${vertaald_naam}":`, data);
            let imageUrl = null;
            if (data.choices && data.choices.length > 0 && data.choices[0].message && data.choices[0].message.content) {
                const content = data.choices[0].message.content;
                if (content.startsWith('http://') || content.startsWith('https://')) { imageUrl = content; }
                else if (content.startsWith('data:image/')) { imageUrl = content; }
                else { console.warn("Qwen Image Gen response content is not an obvious URL/Base64:", content); }
            } else if (data.data && data.data.length > 0 && data.data[0].url) { imageUrl = data.data[0].url;
            } else if (data.data && data.data.length > 0 && data.data[0].b64_json) { imageUrl = `data:image/png;base64,${data.data[0].b64_json}`; }

            if (!imageUrl) {
                console.error("Kon geen bruikbare image URL/Base64 uit Qwen Image Gen response halen.");
                return `https://via.placeholder.com/300x200.png?text=Beeld+Qwen+mislukt+${vertaald_naam.replace(/\s+/g, '+')}`;
            }
            return imageUrl;
        } catch (error) {
            console.error(`Fout tijdens Qwen Image Gen API call for "${vertaald_naam}":`, error);
            return `https://via.placeholder.com/300x200.png?text=API+Fout+Qwen+${vertaald_naam.replace(/\s+/g, '+')}`;
        }
    }

    // --- Hulpfuncties voor UI ---

    function showLoading(isLoading) {
        if (isLoading) {
            loadingIndicator.style.opacity = '0';
            loadingIndicator.style.display = 'flex';
            setTimeout(() => { loadingIndicator.style.opacity = '1'; }, 20);
        } else {
            loadingIndicator.style.opacity = '0';
            setTimeout(() => { loadingIndicator.style.display = 'none'; }, 300);
        }
    }

    function showError(message) {
        errorMessageTextElement.textContent = message;
        errorMessageElement.style.display = 'flex';
    }

    function clearResults() {
        menuItemsContainer.innerHTML = '';
        errorMessageElement.style.display = 'none';
        errorMessageTextElement.textContent = '';
    }

    function displayMenuItem(item) {
        const itemCard = document.createElement('article');
        itemCard.classList.add('menu-item');

        const imageContainer = document.createElement('div');
        imageContainer.classList.add('menu-item-image-container');

        if (item.image_url && !item.image_url.includes('placeholder.com') && !item.image_url.includes('Beeld+Qwen+mislukt') && !item.image_url.includes('API+Fout+Qwen')) {
            const img = document.createElement('img');
            img.src = item.image_url;
            img.alt = `Afbeelding van ${item.vertaald_naam || item.original_name || 'gerecht'}`;
            img.onerror = function() {
                imageContainer.innerHTML = `<p class="placeholder-image-text">Afbeelding kon niet geladen worden.</p>`;
            };
            imageContainer.appendChild(img);
        } else {
            let placeholderText = '[Geen afbeelding gegenereerd]';
            if(item.image_url && (item.image_url.includes('Beeld+Qwen+mislukt') || item.image_url.includes('API+Fout+Qwen'))) {
                placeholderText = '[Beeldgeneratie met Qwen voor dit item is mislukt]';
            }
            imageContainer.innerHTML = `<p class="placeholder-image-text">${placeholderText}</p>`;
        }
        itemCard.appendChild(imageContainer);

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('menu-item-content');

        contentDiv.innerHTML = `
            <h3>${item.vertaald_naam || item.original_name || 'Onbekend Item'}</h3>
            ${(item.original_name && item.vertaald_naam !== item.original_name) ? `<p class="original-name"><em>Origineel: ${item.original_name}</em></p>` : ''}
            <p><strong><i class="fas fa-info-circle"></i> Uitleg:</strong> ${item.uitleg || 'Niet beschikbaar'}</p>
            <p><strong><i class="fas fa-pepper-hot"></i> Ingrediënten:</strong> ${(item.ingredienten && item.ingredienten.length > 0) ? item.ingredienten.join(', ') : 'Niet gespecificeerd'}</p>
            <p><strong><i class="fas fa-flag"></i> Keuken:</strong> ${item.keuken || 'Niet gespecificeerd'}</p>
        `;
        itemCard.appendChild(contentDiv);
        menuItemsContainer.appendChild(itemCard);
    }
});
