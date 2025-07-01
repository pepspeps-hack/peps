document.addEventListener('DOMContentLoaded', () => {
    const menuImageUpload = document.getElementById('menu-image-upload');
    const targetLanguageSelect = document.getElementById('target-language');
    const processMenuButton = document.getElementById('process-menu-button');
    const loadingIndicator = document.getElementById('loading-indicator'); // Dit is nu de .loading-overlay
    const errorMessageElement = document.getElementById('error-message'); // Dit is nu .error-display
    const errorMessageTextElement = errorMessageElement.querySelector('span'); // Het span binnen de error-display
    const menuItemsContainer = document.getElementById('menu-items-container');
    const fileNameDisplay = document.getElementById('file-name-display');

    // Placeholder for OpenRouter API Key - !!! VUL HIER JE EIGEN KEY IN !!!
    // LET OP: Het is veiliger om de API key via een backend proxy te laten lopen voor een productie applicatie.
    // Voor dit prototype wordt het direct gebruikt, wat een veiligheidsrisico kan zijn.
    const OPENROUTER_API_KEY = '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'; // Nieuwe API Key
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
            // Stap 1: OCR (nog niet geïmplementeerd, placeholder)
            // In een echte implementatie zou hier de call naar Gemini of Tesseract.js komen.
            const ocrText = await performOcr(imageFile);
            console.log("OCR Result (placeholder):", ocrText);

            if (!ocrText || ocrText.trim() === "") {
                showError("Kon geen tekst uit de afbeelding extraheren. Probeer een duidelijkere foto.");
                showLoading(false);
                return;
            }

            // Stap 2: Parse menu items (simpele placeholder, moet verfijnd worden)
            const menuItems = parseMenuItems(ocrText);
            if (menuItems.length === 0) {
                showError("Kon geen individuele menu-items vinden in de tekst.");
                showLoading(false);
                return;
            }
            console.log("Parsed Menu Items (placeholder):", menuItems);


            // Stap 3 & 4: Verwerk elk menu item (tekstverwerking & beeldgeneratie)
            // Nu eerst alleen tekstverwerking, beeldgeneratie komt in de volgende stap.
            for (const itemText of menuItems) {
                const processedTextData = await processSingleMenuItemWithGemini(itemText, targetLanguage); // Hernoemde functie

                let imageUrl = `https://via.placeholder.com/300x200.png?text=Beeld+voor+${(processedTextData.vertaald_naam || itemText).replace(/\s+/g, '+')}`; // Default placeholder
                if (processedTextData && !processedTextData.uitleg.startsWith("Fout bij verwerken")) { // Alleen proberen als tekstverwerking succesvol was
                    try {
                        imageUrl = await generateImageWithLlama(processedTextData);
                    } catch (imgError) {
                        console.error("Kon afbeelding niet genereren voor:", processedTextData.vertaald_naam, imgError);
                        // imageUrl blijft de placeholder als generateImageWithLlama een error gooit of een fallback URL teruggeeft.
                    }
                }

                displayMenuItem({
                    ...processedTextData,
                    image_url: imageUrl
                });
            }

        } catch (error) {
            console.error("Fout tijdens verwerken:", error);
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
        // Client-side API key check verwijderd zoals gevraagd. Validatie gebeurt door OpenRouter.

        const base64Image = await imageToBase64(imageFile);

        const payload = {
            model: "google/gemini-2.0-flash-exp:free", // Gecorrigeerd OCR Model
            messages: [
                {
                    role: "user",
                    content: [
                        {
                            type: "text",
                            text: "Extraheer alle tekst van deze afbeelding van een menukaart. Geef alleen de herkende tekst terug, zonder extra opmerkingen of uitleg."
                        },
                        {
                            type: "image_url",
                            image_url: {
                                url: base64Image
                            }
                        }
                    ]
                }
            ],
            max_tokens: 2000 // Ruimte voor potentieel veel tekst
        };

        try {
            const response = await fetch(OPENROUTER_API_URL, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
                    'Content-Type': 'application/json',
                    // Optioneel: Voeg site URL en naam toe voor OpenRouter leaderboards
                    // 'HTTP-Referer': 'YOUR_SITE_URL',
                    // 'X-Title': 'YOUR_SITE_NAME'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null); // Probeer error details te parsen
                console.error("API Error Data:", errorData);
                throw new Error(`API request failed with status ${response.status}: ${response.statusText}. Details: ${errorData ? JSON.stringify(errorData.error) : 'Geen details'}`);
            }

            const data = await response.json();
            console.log("Gemini API Response (OCR):", data);

            if (data.choices && data.choices.length > 0 && data.choices[0].message && data.choices[0].message.content) {
                return data.choices[0].message.content.trim();
            } else {
                throw new Error("Geen geldige tekst ontvangen van OCR API.");
            }
        } catch (error) {
            console.error("Fout tijdens OCR API call:", error);
            throw error; // Gooi de error verder zodat het in de UI getoond kan worden
        }
    }

    function parseMenuItems(ocrText) {
        // Simpele parser: split op nieuwe regels. Moet slimmer gemaakt worden.
        return ocrText.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    }

    async function processSingleMenuItemWithGemini(itemText, targetLanguage) { // Functie hernoemd
        console.log(`Processing item "${itemText}" with Gemini Flash for language: ${targetLanguage}`); // Log aangepast
        // Client-side API key check verwijderd zoals gevraagd. Validatie gebeurt door OpenRouter.

        const systemPrompt = `Je bent een gespecialiseerde AI-assistent voor het analyseren en uitleggen van restaurantmenu-items.
Antwoord ALTIJD in een valide JSON-object. De structuur van het JSON-object moet zijn:
{
  "original_name": "DE ORIGINELE TEKST VAN HET MENU ITEM",
  "vertaald_naam": "DE VERTALING VAN HET MENU ITEM NAAR DE DOELTAAL",
  "uitleg": "EEN KORTE, EENVOUDIGE UITLEG VAN HET GERECHT IN DE DOELTAAL",
  "ingredienten": ["HOOFDINGREDIËNT 1", "HOOFDINGREDIËNT 2", "..."],
  "keuken": "DE KEUKEN (BIJV. ITALIAANS, MEXICAANS, ETC.) INDIEN AFLEIDBAAR, ANDERS LEEG LATEN"
}
Extraheer de informatie uitsluitend uit de gegeven menu-item tekst. Speculeer niet over ingrediënten of keuken als deze niet duidelijk zijn.
Als een veld niet ingevuld kan worden op basis van de input, laat de string dan leeg of geef een lege array voor ingrediënten.`;

        const userPrompt = `Analyseer het volgende menu-item: "${itemText}".
Doeltaal voor vertaling en uitleg: ${targetLanguage}.
Retourneer het resultaat als een JSON-object zoals gespecificeerd in de system prompt.`;

        const payload = {
            model: "google/gemini-2.0-flash-exp:free", // Model gewijzigd naar Gemini
            response_format: { type: "json_object" }, // Vraag om JSON output (hopelijk ondersteund)
            messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: userPrompt }
            ],
            temperature: 0.5, // Iets creatiever voor uitleg, maar niet te veel
            max_tokens: 500,
            // stream: false // Zekerstellen dat we wachten op de volledige JSON
        };

        try {
            const response = await fetch(OPENROUTER_API_URL, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                console.error("Mistral API Error Data:", errorData);
                throw new Error(`Mistral API request failed with status ${response.status}: ${response.statusText}. Details: ${errorData ? JSON.stringify(errorData.error) : 'Geen details'}`);
            }

            const data = await response.json();
            console.log(`Gemini API Response for "${itemText}" (Text Processing):`, data); // Log aangepast

            if (data.choices && data.choices.length > 0 && data.choices[0].message && data.choices[0].message.content) {
                try {
                    // De content zou al JSON moeten zijn vanwege response_format, maar voor de zekerheid parsen.
                    // Sommige modellen stoppen de JSON in een ```json ... ``` block.
                    let contentStr = data.choices[0].message.content;
                    if (contentStr.startsWith("```json")) {
                        contentStr = contentStr.substring(7, contentStr.length - 3).trim();
                    } else if (contentStr.startsWith("```")) {
                         contentStr = contentStr.substring(3, contentStr.length - 3).trim();
                    }

                    const jsonResponse = JSON.parse(contentStr);
                    // Valideer of de verwachte velden aanwezig zijn
                    if (typeof jsonResponse.original_name === 'undefined' || typeof jsonResponse.vertaald_naam === 'undefined' ||
                        typeof jsonResponse.uitleg === 'undefined' || typeof jsonResponse.ingredienten === 'undefined') {
                        console.warn("Gemini response mist verwachte JSON velden:", jsonResponse);
                        // Probeer toch iets terug te geven met de originele tekst als fallback
                        return {
                            original_name: itemText,
                            vertaald_naam: `Kon niet verwerken met Gemini: ${itemText}`,
                            uitleg: "Fout bij parsen van Gemini AI antwoord (missende velden).",
                            ingredienten: [],
                            keuken: ""
                        };
                    }
                    return jsonResponse;
                } catch (e) {
                    console.error("Fout bij het parsen van Gemini JSON response:", e, data.choices[0].message.content);
                    throw new Error("Antwoord van Gemini kon niet als JSON worden verwerkt.");
                }
            } else {
                throw new Error("Geen geldige content ontvangen van Gemini API (Text Processing).");
            }
        } catch (error) {
            console.error(`Fout tijdens Gemini API call for "${itemText}" (Text Processing):`, error); // Log aangepast
            // Geef een foutobject terug zodat de loop door kan gaan met andere items
            return {
                original_name: itemText,
                vertaald_naam: `Fout bij verwerken: ${itemText}`,
                uitleg: error.message,
                ingredienten: [],
                keuken: ""
            };
        }
    }


    async function generateImageWithLlama(processedTextData) {
        const { vertaald_naam, original_name, keuken, ingredienten } = processedTextData;
        console.log(`Generating image for "${vertaald_naam}" with Llama 3.2 Vision...`);

        // Client-side API key check verwijderd zoals gevraagd. Validatie gebeurt door OpenRouter.

        // Probeer een generieke garnituur of laat het weg als het te complex wordt.
        const garnituur = "een passende garnering"; // Simpele placeholder
        const ingredientenString = ingredienten.join(', ');

        // De prompt zoals gespecificeerd, aangepast voor Llama text-to-image.
        // Het is mogelijk dat Llama een andere promptstructuur of parameters verwacht dan standaard text-to-image modellen.
        // Dit is een generieke text-to-image prompt.
        const imagePromptText = `Generate a high-quality food photography image of "${vertaald_naam}" (Original: "${original_name}"), a traditional ${keuken || 'dish'} made with ${ingredientenString}. The dish is served on a clean white plate, with ${garnituur}, in a well-lit restaurant setting. Professional food photography style, hyper-realistic, 4K resolution.`;

        // Aanname: Llama Vision op OpenRouter accepteert een text-to-image prompt via de chat completions endpoint.
        // De exacte modelnaam moet geverifieerd worden op OpenRouter. Ik gebruik een placeholder.
        // OpenRouter's documentatie over beeldgeneratie is hier cruciaal.
        // Veel beeldmodellen hebben specifieke parameters zoals "n" (aantal afbeeldingen), "size", etc.
        // Voor nu houden we het simpel.
        const payload = {
            model: "qwen/qwq-32b:free", // Exacte model ID zoals gespecificeerd door gebruiker.
                                   // VERIFIEER of dit model bestaat, gratis is, en text-to-image ondersteunt op OpenRouter.
            messages: [
                {
                    role: "user",
                    content: imagePromptText
                }
            ],
            // Mogelijke parameters specifiek voor beeldgeneratie (afhankelijk van model/OpenRouter implementatie):
            // "n": 1, // Aantal afbeeldingen
            // "size": "1024x1024", // Afbeeldingsgrootte
            // "response_format": "url", // of "b64_json"
            max_tokens: 250 // Ruimte voor een URL of base64 string (kan aangepast worden)
        };

        try {
            const response = await fetch(OPENROUTER_API_URL, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                console.error("Llama Vision API Error Data:", errorData);
                throw new Error(`Llama Vision API request failed with status ${response.status}: ${response.statusText}. Details: ${errorData ? JSON.stringify(errorData.error) : 'Geen details'}`);
            }

            const data = await response.json();
            console.log(`Llama Vision API Response for "${vertaald_naam}":`, data);

            // De structuur van het antwoord voor beeldgeneratie kan variëren.
            // - Sommige modellen geven een URL in `data.url` of `data.data[0].url`.
            // - Andere geven base64 data in `data.data[0].b64_json`.
            // - Als het via de chat completions endpoint gaat, kan de URL in `choices[0].message.content` staan.
            // Dit is een generieke poging om een URL te vinden.
            let imageUrl = null;
            if (data.choices && data.choices.length > 0 && data.choices[0].message && data.choices[0].message.content) {
                // Probeer te zien of de content een URL is. Dit is een zwakke check.
                // Een beter model zou expliciet een URL of base64 teruggeven in een gestructureerd veld.
                const content = data.choices[0].message.content;
                if (content.startsWith('http://') || content.startsWith('https://')) {
                    imageUrl = content;
                } else {
                    // Als het geen URL is, kan het een pad zijn of een base64 string.
                    // Voor nu loggen we het en gaan we ervan uit dat we een URL verwachten.
                    console.warn("Llama Vision response content is not an obvious URL:", content);
                     // Probeer of het een base64 string is (simpele check)
                    if (content.startsWith('data:image/')) {
                        imageUrl = content; // Direct bruikbaar als src
                    } else {
                        // Fallback als we de image URL niet kunnen vinden.
                        console.error("Kon geen image URL extraheren uit Llama Vision response.");
                        // imageUrl = `https://via.placeholder.com/300x200.png?text=Fout+bij+beeldgeneratie`;
                    }
                }
            } else if (data.data && data.data.length > 0 && data.data[0].url) {
                imageUrl = data.data[0].url; // Standaard OpenAI DALL-E formaat
            } else if (data.data && data.data.length > 0 && data.data[0].b64_json) {
                imageUrl = `data:image/png;base64,${data.data[0].b64_json}`; // Standaard OpenAI DALL-E formaat
            }


            if (!imageUrl) {
                 // Als na alle checks geen URL is gevonden, gebruik een duidelijke placeholder
                console.error("Kon geen bruikbare image URL of base64 data extraheren uit Llama Vision response.");
                return `https://via.placeholder.com/300x200.png?text=Beeld+generatie+mislukt+voor+${vertaald_naam.replace(/\s+/g, '+')}`;
            }

            return imageUrl;

        } catch (error) {
            console.error(`Fout tijdens Llama Vision API call for "${vertaald_naam}":`, error);
            return `https://via.placeholder.com/300x200.png?text=API+Fout+beeld+${vertaald_naam.replace(/\s+/g, '+')}`; // Fallback image URL
        }
    }


    // --- Hulpfuncties voor UI ---

    function showLoading(isLoading) {
        if (isLoading) {
            loadingIndicator.style.opacity = '0'; // Begin onzichtbaar voor fade-in
            loadingIndicator.style.display = 'flex';
            setTimeout(() => { // Wacht een fractie voor de display:flex om effect te hebben
                loadingIndicator.style.opacity = '1';
            }, 20);
        } else {
            loadingIndicator.style.opacity = '0';
            setTimeout(() => { // Wacht tot fade-out compleet is voor display:none
                loadingIndicator.style.display = 'none';
            }, 300); // Moet overeenkomen met CSS transitie tijd
        }
    }

    function showError(message) {
        errorMessageTextElement.textContent = message; // Zet tekst in de span
        errorMessageElement.style.display = 'flex'; // Gebruik flex voor de error card
        // Voeg eventueel een fade-in toe als gewenst, vergelijkbaar met showLoading
    }

    function clearResults() {
        menuItemsContainer.innerHTML = '';
        errorMessageElement.style.display = 'none';
        errorMessageTextElement.textContent = '';
    }

    function displayMenuItem(item) {
        const itemCard = document.createElement('article'); // Gebruik <article> voor semantiek
        itemCard.classList.add('menu-item'); // De .card stijl wordt al toegepast door .menu-item in CSS

        const imageContainer = document.createElement('div');
        imageContainer.classList.add('menu-item-image-container'); // Voor eventuele extra styling

        if (item.image_url && !item.image_url.includes('placeholder.com') && !item.image_url.includes('Beeld+generatie+mislukt') && !item.image_url.includes('API+Fout+beeld')) {
            const img = document.createElement('img');
            img.src = item.image_url;
            img.alt = `Afbeelding van ${item.vertaald_naam || item.original_name || 'gerecht'}`;
            img.onerror = function() {
                imageContainer.innerHTML = `<p class="placeholder-image-text">Afbeelding kon niet geladen worden.</p>`;
            };
            imageContainer.appendChild(img);
        } else {
            let placeholderText = '[Geen afbeelding gegenereerd]';
            if(item.image_url && (item.image_url.includes('Beeld+generatie+mislukt') || item.image_url.includes('API+Fout+beeld'))) {
                placeholderText = '[Beeldgeneratie voor dit item is mislukt]';
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
