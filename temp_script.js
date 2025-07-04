        // Global state
        let currentCharacter = null;
        let characterId = null;
        let refinementCount = 0;
        let verboseMode = true;
        let stepCounter = 1;
        const API_BASE = 'http://localhost:8000';

        // Enhanced logging functions for ultra-verbose mode
        function logVerbose(title, content, type = 'info') {
            if (!verboseMode) return;
            
            const verboseLog = document.getElementById('verboseLog');
            const timestamp = new Date().toLocaleTimeString();
            
            const logDiv = document.createElement('div');
            logDiv.className = `log-entry ${type}`;
            
            // Create detailed log entry based on type
            switch(type) {
                case 'creation-start':
                    logDiv.innerHTML = createCreationStartLog(title, content, timestamp);
                    break;
                case 'creation-step':
                    logDiv.innerHTML = createCreationStepLog(title, content, timestamp);
                    break;
                case 'llm-request':
                    logDiv.innerHTML = createLLMRequestLog(title, content, timestamp);
                    break;
                case 'llm-response':
                    logDiv.innerHTML = createLLMResponseLog(title, content, timestamp);
                    break;
                case 'llm-error':
                    logDiv.innerHTML = createLLMErrorLog(title, content, timestamp);
                    break;
                case 'creation-complete':
                    logDiv.innerHTML = createCreationCompleteLog(title, content, timestamp);
                    break;
                case 'creation-error':
                    logDiv.innerHTML = createCreationErrorLog(title, content, timestamp);
                    break;
                default:
                    logDiv.innerHTML = createGenericLog(title, content, timestamp, type);
            }
            
            verboseLog.appendChild(logDiv);
            verboseLog.scrollTop = verboseLog.scrollHeight;
        }

        function createCreationStartLog(title, content, timestamp) {
            return `
                <div class="log-header">
                    <span>🚀 ${title}</span>
                    <span class="log-timestamp">${timestamp}</span>
                </div>
                <div class="log-content">
                    <div class="step-summary">
                        Starting character creation process with user input
                    </div>
                    <div class="log-meta">
                        <strong>Prompt:</strong> "${content.prompt || content}"<br>
                        <strong>User Preferences:</strong> ${JSON.stringify(content.user_preferences || {}, null, 2)}
                    </div>
                </div>
            `;
        }

        function createCreationStepLog(title, content, timestamp) {
            return `
                <div class="log-header">
                    <span>⚙️ ${title}</span>
                    <span class="log-timestamp">${timestamp}</span>
                </div>
                <div class="log-content">
                    <div class="step-summary">
                        ${content.description || content}
                    </div>
                    ${content.step ? `<div class="log-meta"><strong>Step:</strong> ${content.step}</div>` : ''}
                    ${content.data ? `
                        <button class="collapsible-verbose" onclick="toggleVerboseCollapsible(this)">
                            Show Generated Data
                        </button>
                        <div class="collapsible-verbose-content">
                            <div class="json-display">${JSON.stringify(content.data, null, 2)}</div>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        function createLLMRequestLog(title, content, timestamp) {
            const promptText = content.prompt || content;
            const promptLength = typeof promptText === 'string' ? promptText.length : JSON.stringify(promptText).length;
            
            return `
                <div class="log-header">
                    <span>📤 LLM Request: ${title}</span>
                    <span class="log-timestamp">${timestamp}</span>
                </div>
                <div class="log-content">
                    <div class="llm-stats">
                        <div class="stat-item"><strong>Type:</strong> ${content.content_type || 'Unknown'}</div>
                        <div class="stat-item"><strong>Attempt:</strong> ${content.attempt || 1}</div>
                        <div class="stat-item"><strong>Length:</strong> ${promptLength} chars</div>
                    </div>
                    <button class="collapsible-verbose" onclick="toggleVerboseCollapsible(this)">
                        Show Prompt Details
                    </button>
                    <div class="collapsible-verbose-content">
                        <div class="prompt-display">${typeof promptText === 'string' ? promptText : JSON.stringify(promptText, null, 2)}</div>
                    </div>
                </div>
            `;
        }

        function createLLMResponseLog(title, content, timestamp) {
            const responseText = content.raw_response || content.response || content;
            const responseLength = typeof responseText === 'string' ? responseText.length : JSON.stringify(responseText).length;
            
            return `
                <div class="log-header">
                    <span>📥 LLM Response: ${title}</span>
                    <span class="log-timestamp">${timestamp}</span>
                </div>
                <div class="log-content">
                    <div class="performance-info">
                        ⚡ Generation Time: ${content.generation_time ? content.generation_time.toFixed(2) + 's' : 'Unknown'} | 
                        📊 Response Size: ${responseLength} characters
                    </div>
                    <div class="llm-stats">
                        <div class="stat-item"><strong>Type:</strong> ${content.content_type || 'Unknown'}</div>
                        <div class="stat-item"><strong>Attempt:</strong> ${content.attempt || 1}</div>
                        <div class="stat-item"><strong>Success:</strong> ${content.success ? '✅' : '❌'}</div>
                    </div>
                    <button class="collapsible-verbose" onclick="toggleVerboseCollapsible(this)">
                        Show Raw Response
                    </button>
                    <div class="collapsible-verbose-content">
                        <div class="response-display">${typeof responseText === 'string' ? responseText : JSON.stringify(responseText, null, 2)}</div>
                    </div>
                    ${content.parsed_data ? `
                        <button class="collapsible-verbose" onclick="toggleVerboseCollapsible(this)">
                            Show Parsed Data
                        </button>
                        <div class="collapsible-verbose-content">
                            <div class="json-display">${JSON.stringify(content.parsed_data, null, 2)}</div>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        function createLLMErrorLog(title, content, timestamp) {
            return `
                <div class="log-header">
                    <span>❌ LLM Error: ${title}</span>
                    <span class="log-timestamp">${timestamp}</span>
                </div>
                <div class="log-content">
                    <div class="performance-info">
                        ⏱️ Failed after: ${content.generation_time ? content.generation_time.toFixed(2) + 's' : 'Unknown'}
                    </div>
                    <div class="log-meta">
                        <strong>Content Type:</strong> ${content.content_type || 'Unknown'}<br>
                        <strong>Attempt:</strong> ${content.attempt || 1}<br>
                        <strong>Error:</strong> ${content.error || content}
                    </div>
                </div>
            `;
        }

        function createCreationCompleteLog(title, content, timestamp) {
            return `
                <div class="log-header">
                    <span>✅ ${title}</span>
                    <span class="log-timestamp">${timestamp}</span>
                </div>
                <div class="log-content">
                    <div class="performance-info">
                        🎉 Total Creation Time: ${content.total_time ? content.total_time.toFixed(2) + 's' : 'Unknown'}
                    </div>
                    <div class="step-summary">
                        Successfully created character: <strong>${content.character_name || 'Unknown'}</strong>
                        ${content.final_level ? ` (Level ${content.final_level})` : ''}
                    </div>
                </div>
            `;
        }

        function createCreationErrorLog(title, content, timestamp) {
            return `
                <div class="log-header">
                    <span>💥 ${title}</span>
                    <span class="log-timestamp">${timestamp}</span>
                </div>
                <div class="log-content">
                    <div class="performance-info">
                        ⏱️ Failed after: ${content.total_time ? content.total_time.toFixed(2) + 's' : 'Unknown'}
                    </div>
                    <div class="log-meta">
                        <strong>Error:</strong> ${content.error || content}
                    </div>
                </div>
            `;
        }

        function createGenericLog(title, content, timestamp, type) {
            return `
                <div class="log-header">
                    <span>📝 ${title}</span>
                    <span class="log-timestamp">${timestamp}</span>
                </div>
                <div class="log-content">
                    <div class="log-meta">
                        ${typeof content === 'string' ? content : JSON.stringify(content, null, 2)}
                    </div>
                </div>
            `;
        }

        function toggleVerboseCollapsible(button) {
            const content = button.nextElementSibling;
            const isActive = content.classList.contains('active');
            
            if (isActive) {
                content.classList.remove('active');
                button.classList.remove('active');
                button.textContent = button.textContent.replace('Hide', 'Show');
            } else {
                content.classList.add('active');
                button.classList.add('active');
                button.textContent = button.textContent.replace('Show', 'Hide');
            }
        }

        function toggleCollapsible(button) {
            const content = button.nextElementSibling;
            const isActive = content.classList.contains('active');
            
            if (isActive) {
                content.classList.remove('active');
                button.classList.remove('active');
                button.textContent = button.textContent.replace('Hide', 'Show');
            } else {
                content.classList.add('active');
                button.classList.add('active');
                button.textContent = button.textContent.replace('Show', 'Hide');
            }
        }

        // Utility functions
        function showElement(id) {
            document.getElementById(id).classList.remove('hidden');
        }

        function hideElement(id) {
            document.getElementById(id).classList.add('hidden');
        }

        function showError(message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.textContent = message;
            document.getElementById('generationLog').appendChild(errorDiv);
        }

        function showSuccess(message) {
            const successDiv = document.createElement('div');
            successDiv.className = 'success';
            successDiv.textContent = message;
            document.getElementById('generationLog').appendChild(successDiv);
        }

        function updateProgress(percentage, status) {
            document.getElementById('progressFill').style.width = percentage + '%';
            document.getElementById('generationStatus').textContent = status;
        }

        function logMessage(message) {
            const logDiv = document.createElement('div');
            logDiv.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
            logDiv.style.margin = '5px 0';
            logDiv.style.padding = '5px';
            logDiv.style.background = '#f8f9fa';
            logDiv.style.borderRadius = '4px';
            document.getElementById('generationLog').appendChild(logDiv);
        }

        // Enhanced API call wrapper with verbose logging
        async function apiCall(endpoint, method = 'GET', data = null, stepDescription = '') {
            const startTime = Date.now();
            
            if (stepDescription) {
                logVerbose(stepDescription, `Preparing ${method} request to ${endpoint}`, 'step');
            }

            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                }
            };

            let finalEndpoint = endpoint;
            if (data) {
                if (method === 'GET') {
                    // Convert data to query parameters
                    const params = new URLSearchParams(data);
                    finalEndpoint += '?' + params.toString();
                    logVerbose(`${method} ${endpoint}`, `Query parameters: ${params.toString()}`, 'request');
                } else {
                    options.body = JSON.stringify(data);
                    logVerbose(`${method} ${endpoint}`, {
                        url: API_BASE + endpoint,
                        method: method,
                        headers: options.headers,
                        body: data
                    }, 'request');
                }
            } else {
                logVerbose(`${method} ${endpoint}`, {
                    url: API_BASE + finalEndpoint,
                    method: method,
                    headers: options.headers
                }, 'request');
            }

            try {
                // Create AbortController for timeout
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 minutes timeout
                
                const response = await fetch(API_BASE + finalEndpoint, {
                    ...options,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                const responseTime = Date.now() - startTime;
                
                if (!response.ok) {
                    const errorText = await response.text();
                    logVerbose(`API Error ${response.status}`, {
                        status: response.status,
                        statusText: response.statusText,
                        responseTime: `${responseTime}ms`,
                        errorBody: errorText
                    }, 'error');
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const result = await response.json();
                
                logVerbose(`Response from ${endpoint}`, {
                    status: response.status,
                    responseTime: `${responseTime}ms`,
                    dataSize: `${JSON.stringify(result).length} characters`,
                    response: result
                }, 'response');

                return result;
            } catch (error) {
                const responseTime = Date.now() - startTime;
                
                // Handle different error types
                let errorMessage = error.message;
                if (error.name === 'AbortError') {
                    errorMessage = 'Request timed out after 10 minutes';
                }
                
                logVerbose(`Request Failed`, {
                    endpoint: endpoint,
                    method: method,
                    responseTime: `${responseTime}ms`,
                    error: errorMessage,
                    errorType: error.name
                }, 'error');
                
                throw new Error(errorMessage);
            }
        }

        // Enhanced character creation flow with detailed logging
        async function startCreation() {
            console.log('🚀 startCreation function called!');
            
            const concept = document.getElementById('characterConcept').value.trim();
            console.log('Character concept:', concept);
            
            if (!concept) {
                alert('Please enter a character concept first!');
                console.log('❌ No concept provided');
                return;
            }

            console.log('✅ Concept provided, starting creation process...');

            // Test basic functionality first
            try {
                console.log('📝 Resetting verbose log...');
                // Reset verbose log
                document.getElementById('verboseLog').innerHTML = '<h4>🔍 Ultra-Detailed AI Process Log</h4><p style="color: #6c757d; font-size: 12px; margin-bottom: 20px;">This log shows every single step, LLM request, and response in the character creation process.</p>';
                stepCounter = 1;

                console.log('🎯 Showing step 2...');
                // Hide step 1, show step 2
                hideElement('step1');
                showElement('step2');
                document.getElementById('loadingIndicator').classList.add('show');

                console.log('📊 Logging user input...');
                // Log the user's initial concept
                logVerbose('User Input Received', {
                    prompt: concept,
                    timestamp: new Date().toISOString(),
                    user_action: 'character_creation_start'
                }, 'creation-start');

                console.log('🔍 Testing API connection...');
                // Test health check first
                updateProgress(5, 'Testing API connection...');
                await apiCall('/health', 'GET', null, 'Health Check');
                logMessage('✅ API connection successful');
                console.log('✅ Health check passed');

                console.log('🏭 Preparing character creation request...');
                // Generate initial character using factory
                updateProgress(15, 'Generating base character with AI...');
                logVerbose('Preparing Factory Request', {
                    description: 'About to call the AI factory with verbose generation enabled',
                    step: 'factory_preparation'
                }, 'creation-step');

                const characterCreationData = {
                    creation_type: 'character',
                    prompt: concept,
                    save_to_database: true,
                    user_preferences: {
                        level: 3,
                        detail_level: 'high',
                        verbose_generation: true
                    }
                };

                console.log('📡 Calling character creation API...');
                const characterData = await apiCall('/api/v2/factory/create', 'POST', characterCreationData, 'AI Character Generation');
                console.log('📦 Character data received:', characterData);

                // Process verbose logs from backend if available
                if (characterData.verbose_logs && characterData.verbose_logs.length > 0) {
                    logVerbose('Backend Logs Received', {
                        description: `Received ${characterData.verbose_logs.length} detailed log entries from backend`,
                        log_count: characterData.verbose_logs.length
                    }, 'creation-step');
                    
                    // Process each backend log entry
                    processBackendVerboseLogs(characterData.verbose_logs);
                }

                if (characterData.object_id) {
                    characterId = characterData.object_id;
                    currentCharacter = characterData;
                    
                    logVerbose('Character Successfully Created', {
                        character_name: characterData.data?.core?.name || 'Unknown',
                        character_id: characterId,
                        total_time: characterData.processing_time,
                        warnings: characterData.warnings
                    }, 'creation-complete');
                    
                    logMessage(`✅ Character created with ID: ${characterId}`);
                    console.log(`🎉 Character created successfully with ID: ${characterId}`);
                    
                    // Show processing time
                    if (characterData.processing_time) {
                        logVerbose('Performance Summary', {
                            description: 'Final performance metrics for character creation',
                            total_time: characterData.processing_time,
                            character_name: characterData.data?.core?.name || 'Unknown'
                        }, 'creation-complete');
                    }
                } else {
                    console.log('❌ No character ID received');
                    throw new Error('No character ID received from backend');
                }

                console.log('🚀 Starting additional content generation...');
                updateProgress(35, 'Generating enhanced backstory...');
                await generateEnhancedContent(concept);

                updateProgress(55, 'Creating custom equipment...');
                await generateCustomEquipment(concept);

                updateProgress(75, 'Adding personality details...');
                await generatePersonalityDetails(concept);

                updateProgress(90, 'Loading complete character sheet...');
                await loadCompleteCharacterData();

                updateProgress(100, 'Character generation complete!');
                logVerbose('All Generation Complete', {
                    description: 'All AI generation steps finished successfully',
                    final_character: currentCharacter?.data?.core?.name || 'Unknown'
                }, 'creation-complete');
                showSuccess('🎉 Your AI-generated character is ready for review!');

                console.log('🎯 Showing step 3...');
                // Show step 3
                document.getElementById('loadingIndicator').classList.remove('show');
                setTimeout(() => {
                    hideElement('step2');
                    showElement('step3');
                    displayCharacterForReview();
                }, 1000);

            } catch (error) {
                console.error('❌ Error during character generation:', error);
                showError(`❌ Error during character generation: ${error.message}`);
                document.getElementById('loadingIndicator').classList.remove('show');
                logVerbose('Character Creation Failed', {
                    error: error.message,
                    stack: error.stack
                }, 'creation-error');
            }
        }

        function processBackendVerboseLogs(logs) {
            logs.forEach((log, index) => {
                const logType = log.type;
                const timestamp = new Date(log.timestamp * 1000).toLocaleTimeString();
                
                switch(logType) {
                    case 'creation_start':
                        logVerbose('Backend: Creation Started', log, 'creation-start');
                        break;
                    case 'creation_step':
                        logVerbose(`Backend: ${log.step || 'Processing Step'}`, log, 'creation-step');
                        break;
                    case 'llm_request':
                        logVerbose(`Backend: LLM Request (${log.content_type})`, log, 'llm-request');
                        break;
                    case 'llm_response':
                        logVerbose(`Backend: LLM Response (${log.content_type})`, log, 'llm-response');
                        break;
                    case 'llm_error':
                        logVerbose(`Backend: LLM Error (${log.content_type})`, log, 'llm-error');
                        break;
                    case 'creation_complete':
                        logVerbose('Backend: Creation Complete', log, 'creation-complete');
                        break;
                    case 'creation_error':
                        logVerbose('Backend: Creation Error', log, 'creation-error');
                        break;
                    default:
                        logVerbose(`Backend: ${logType}`, log, 'info');
                }
            });
        }

        async function generateEnhancedContent(concept) {
            logVerbose('Enhanced Content Generation', {
                description: 'Generating detailed custom items and spells',
                step: 'enhanced_content'
            }, 'creation-step');
            
            try {
                // Generate unique spell for casters
                logVerbose('Spell Generation Start', {
                    description: 'Generating unique signature spell',
                    prompt: `A unique signature spell for: ${concept}`
                }, 'creation-step');

                const spellData = {
                    creation_type: 'spell',
                    prompt: `A unique signature spell for: ${concept}`,
                    save_to_database: false
                };

                const spellResult = await apiCall('/api/v2/factory/create', 'POST', spellData, 'Custom Spell Generation');
                
                logVerbose('Enhanced Content Complete', {
                    description: 'Successfully generated enhanced content',
                    spell_created: spellResult ? 'Yes' : 'No'
                }, 'creation-complete');
                
            } catch (error) {
                logVerbose('Enhanced Content Failed', {
                    error: error.message,
                    description: 'Failed to generate enhanced content'
                }, 'creation-error');
                logMessage(`⚠️ Enhanced content generation failed: ${error.message}`);
            }
        }

        async function generateCustomEquipment(concept) {
            logVerbose('Custom Equipment Generation', {
                description: 'Creating unique weapons and items',
                step: 'custom_equipment'
            }, 'creation-step');
            
            try {
                // Generate a unique weapon
                logVerbose('Weapon Generation Start', {
                    description: 'Generating unique signature weapon',
                    prompt: `A unique signature weapon for: ${concept}`
                }, 'creation-step');

                const weaponData = {
                    creation_type: 'weapon',
                    prompt: `A unique signature weapon for: ${concept}`,
                    save_to_database: false
                };

                const weaponResult = await apiCall('/api/v2/factory/create', 'POST', weaponData, 'Custom Weapon Generation');
                
                // Generate unique armor
                logVerbose('Armor Generation Start', {
                    description: 'Generating custom armor',
                    prompt: `Custom armor that fits the theme: ${concept}`
                }, 'creation-step');

                const armorData = {
                    creation_type: 'armor',
                    prompt: `Custom armor that fits the theme: ${concept}`,
                    save_to_database: false
                };

                const armorResult = await apiCall('/api/v2/factory/create', 'POST', armorData, 'Custom Armor Generation');
                
                // Generate unique item
                logVerbose('Item Generation Start', {
                    description: 'Generating custom magical item',
                    prompt: `A unique magical item for: ${concept}`
                }, 'creation-step');

                const itemData = {
                    creation_type: 'other_item',
                    prompt: `A unique magical item for: ${concept}`,
                    save_to_database: false
                };

                const itemResult = await apiCall('/api/v2/factory/create', 'POST', itemData, 'Custom Item Generation');
                
                logVerbose('Equipment Generation Complete', {
                    description: 'Successfully created custom equipment set',
                    weapon_created: weaponResult ? 'Yes' : 'No',
                    armor_created: armorResult ? 'Yes' : 'No',
                    item_created: itemResult ? 'Yes' : 'No'
                }, 'creation-complete');
                
            } catch (error) {
                logVerbose('Equipment Generation Failed', {
                    error: error.message,
                    description: 'Failed to generate custom equipment'
                }, 'creation-error');
                logMessage(`⚠️ Custom equipment generation failed: ${error.message}`);
            }
        }

        async function generatePersonalityDetails(concept) {
            logVerbose('Personality Enhancement', {
                description: 'Developing detailed personality traits and motivations',
                step: 'personality_details'
            }, 'creation-step');
            
            try {
                // Generate an NPC companion or rival to add depth
                const npcData = {
                    creation_type: 'npc',
                    prompt: `Create a significant NPC from the backstory of: ${concept} - this could be a mentor, rival, ally, or family member`,
                    save_to_database: false
                };

                const npcResult = await apiCall('/api/v2/factory/create', 'POST', npcData, 'Related NPC Generation');
                
                logVerbose('Personality Complete', {
                    description: 'Successfully enhanced character personality with related NPC',
                    npc_created: npcResult ? 'Generated' : 'Failed'
                }, 'creation-complete');
                
            } catch (error) {
                logVerbose('Personality Generation Failed', {
                    error: error.message,
                    description: 'Failed to generate personality details'
                }, 'creation-error');
                logMessage(`⚠️ Personality enhancement failed: ${error.message}`);
            }
        }

        async function loadCompleteCharacterData() {
            if (!characterId) {
                logVerbose('Character Loading Skipped', {
                    description: 'No character ID available',
                    error: 'Missing character ID'
                }, 'creation-error');
                return;
            }

            logVerbose('Complete Character Loading', {
                description: 'Loading full character sheet and state data',
                character_id: characterId,
                step: 'data_loading'
            }, 'creation-step');
            
            try {
                // Load basic character data
                const basicCharacter = await apiCall(`/api/v2/characters/${characterId}`, 'GET', null, 'Basic Character Data');
                
                // Load complete character sheet
                const characterSheet = await apiCall(`/api/v2/characters/${characterId}/sheet`, 'GET', null, 'Complete Character Sheet');
                
                // Load character state
                const characterState = await apiCall(`/api/v2/characters/${characterId}/state`, 'GET', null, 'Character State');
                
                // Validate character using v2 validation (validate existing character)
                const validation = await apiCall(`/api/v2/characters/${characterId}/validate`, 'GET', null, 'Character Validation');
                
                currentCharacter = {
                    ...basicCharacter,
                    sheet: characterSheet,
                    state: characterState,
                    validation: validation
                };
                
                logVerbose('Character Loading Complete', 'All character data successfully loaded and validated', 'creation-complete');
                logMessage('✅ Complete character sheet loaded and validated');
                
            } catch (error) {
                logVerbose('Character Loading Failed', error.message, 'creation-error');
                logMessage(`⚠️ Character loading failed: ${error.message}`);
                
                // Fallback to basic character data if sheet/state loading fails
                try {
                    const basicCharacter = await apiCall(`/api/v2/characters/${characterId}`, 'GET', null, 'Fallback Character Data');
                    currentCharacter = basicCharacter;
                    logMessage('✅ Basic character data loaded as fallback');
                } catch (fallbackError) {
                    logMessage(`❌ Complete character loading failed: ${fallbackError.message}`);
                }
            }
        }

        function displayCharacterForReview() {
            const container = document.getElementById('initialCharacterDisplay');
            
            if (!currentCharacter) {
                container.innerHTML = '<div class="error">No character data available</div>';
                return;
            }

            // Handle both factory response format and character response format
            const characterData = currentCharacter.data || currentCharacter;
            const coreData = characterData.core || characterData;
            const rawData = characterData.raw_data || {};

            const name = coreData.name || rawData.name || 'Generated Character';
            const species = coreData.species || rawData.species || 'Custom Species';
            const background = coreData.background || rawData.background || 'Unique Background';
            const level = coreData.level || rawData.level || 1;
            const classes = coreData.character_classes || rawData.classes || rawData.character_classes || {'Adventurer': 1};
            const abilities = coreData.ability_scores || rawData.ability_scores || rawData.attributes || {};
            const backstory = (coreData.personality && coreData.personality.backstory) || rawData.backstory || 'A mysterious past awaits discovery...';

            container.innerHTML = `
                <div class="character-sheet">
                    <h3>🎭 Your AI-Generated Character</h3>
                    <div class="character-grid">
                        <div class="character-section">
                            <h4>Basic Information</h4>
                            <p><strong>Name:</strong> ${name}</p>
                            <p><strong>Species:</strong> ${species}</p>
                            <p><strong>Background:</strong> ${background}</p>
                            <p><strong>Level:</strong> ${level}</p>
                        </div>
                        
                        <div class="character-section">
                            <h4>Classes</h4>
                            ${formatClasses(classes)}
                        </div>
                        
                        <div class="character-section">
                            <h4>Ability Scores</h4>
                            <div class="ability-scores">
                                ${formatAbilityScores(abilities)}
                            </div>
                        </div>
                        
                        <div class="character-section">
                            <h4>Backstory</h4>
                            <p style="font-style: italic; max-height: 150px; overflow-y: auto;">${backstory}</p>
                        </div>
                    </div>
                    
                    <button class="collapsible" onclick="toggleCollapsible(this)">
                        Show Full Character Data
                    </button>
                    <div class="collapsible-content">
                        <div class="json-display">${JSON.stringify(characterData, null, 2)}</div>
                    </div>
                </div>
            `;
        }

        function formatClasses(classes) {
            if (!classes || Object.keys(classes).length === 0) {
                return '<p>Adventurer Level 1</p>';
            }
            
            return Object.entries(classes)
                .map(([className, level]) => `<p>${className} ${level}</p>`)
                .join('');
        }

        function formatAbilityScores(abilities) {
            const defaultAbilities = {
                strength: 10, dexterity: 10, constitution: 10,
                intelligence: 10, wisdom: 10, charisma: 10
            };
            
            const finalAbilities = { ...defaultAbilities, ...abilities };
            
            return Object.entries(finalAbilities)
                .map(([ability, score]) => {
                    const modifier = Math.floor((score - 10) / 2);
                    const modStr = modifier >= 0 ? `+${modifier}` : `${modifier}`;
                    return `
                        <div class="ability-score">
                            <div class="name">${ability.toUpperCase().slice(0, 3)}</div>
                            <div class="score">${score}</div>
                            <div class="modifier">${modStr}</div>
                        </div>
                    `;
                })
                .join('');
        }

        async function refineCharacter() {
            const refinementPrompt = document.getElementById('refinementPrompt').value.trim();
            
            if (!refinementPrompt) {
                alert('Please describe what you\'d like to change about your character.');
                return;
            }

            if (!characterId) {
                alert('No character available to refine.');
                return;
            }

            try {
                refinementCount++;
                const historyContainer = document.getElementById('refinementHistory');
                
                // Add refinement to history
                const refinementDiv = document.createElement('div');
                refinementDiv.className = 'iteration-container';
                refinementDiv.innerHTML = `
                    <div class="iteration-header">🔄 Refinement ${refinementCount}</div>
                    <p><strong>Your Request:</strong> ${refinementPrompt}</p>
                    <div class="loading show">
                        <div class="spinner"></div>
                        <p>AI is refining your character...</p>
                    </div>
                `;
                historyContainer.appendChild(refinementDiv);

                // Use evolution endpoint to refine character
                const evolutionData = await apiCall('/api/v2/factory/evolve', 'POST', {
                    creation_type: 'character',
                    character_id: characterId,
                    evolution_prompt: `Based on user feedback: "${refinementPrompt}" - Please refine the character accordingly while maintaining the core concept.`,
                    preserve_backstory: true,
                    user_preferences: {
                        refinement_type: 'user_feedback',
                        iteration: refinementCount
                    }
                });

                // Update character data from evolution response
                if (evolutionData.success && evolutionData.data) {
                    currentCharacter.data = evolutionData.data;
                }

                // Try to get updated character from database
                try {
                    const updatedCharacter = await apiCall(`/api/v2/characters/${characterId}`);
                    currentCharacter = { ...currentCharacter, ...updatedCharacter };
                } catch (error) {
                    console.log('Could not load updated character from database, using evolution data');
                }

                // Update the refinement display
                refinementDiv.querySelector('.loading').classList.remove('show');
                
                // Extract character data for display
                const updatedData = currentCharacter.data || currentCharacter;
                const coreData = updatedData.core || updatedData;
                const name = coreData.name || 'Generated Character';
                const backstory = (coreData.personality && coreData.personality.backstory) || updatedData.raw_data?.backstory || 'A mysterious past awaits discovery...';
                
                refinementDiv.innerHTML += `
                    <div class="success">✅ Character refined successfully!</div>
                    <div style="margin-top: 10px;">
                        <strong>Updated Character:</strong>
                        <div style="margin-left: 15px; margin-top: 5px;">
                            <p><strong>Name:</strong> ${name}</p>
                            <p><strong>Backstory:</strong> ${backstory.substring(0, 200)}${backstory.length > 200 ? '...' : ''}</p>
                        </div>
                    </div>
                `;

                // Refresh the character display
                displayCharacterForReview();

                // Clear the refinement input
                document.getElementById('refinementPrompt').value = '';

                showSuccess(`Refinement ${refinementCount} complete! Review the updated character above.`);

            } catch (error) {
                showError(`❌ Error refining character: ${error.message}`);
            }
        }

        async function finalizeCharacter() {
            if (!characterId) {
                alert('No character to finalize.');
                return;
            }

            try {
                // Load complete character sheet
                const characterSheet = await apiCall(`/api/v2/characters/${characterId}/sheet`);
                const characterState = await apiCall(`/api/v2/characters/${characterId}/state`);
                
                currentCharacter.sheet = characterSheet;
                currentCharacter.state = characterState;

                // Hide step 3, show step 4
                hideElement('step3');
                showElement('step4');
                
                displayFinalCharacterSheet();
                
            } catch (error) {
                showError(`❌ Error finalizing character: ${error.message}`);
                
                // Fallback to current character data if detailed loading fails
                hideElement('step3');
                showElement('step4');
                displayFinalCharacterSheet();
            }
        }

        function displayFinalCharacterSheet() {
            const container = document.getElementById('finalCharacterSheet');
            
            // Handle both v2 factory response format and direct character data
            const characterData = currentCharacter.data || currentCharacter;
            const sheet = currentCharacter.sheet || {};
            const coreData = characterData.core || sheet.core || characterData;
            const rawData = characterData.raw_data || {};
            const stats = sheet.stats || {};
            const state = currentCharacter.state || sheet.state || {};

            // Extract data with fallbacks
            const name = coreData.name || rawData.name || 'Generated Character';
            const species = coreData.species || rawData.species || 'Custom Species';
            const background = coreData.background || rawData.background || 'Unique Background';
            const level = coreData.level || rawData.level || 1;
            const classes = coreData.character_classes || rawData.classes || rawData.character_classes || {'Adventurer': 1};
            const abilities = coreData.ability_scores || rawData.ability_scores || rawData.attributes || {};
            const backstory = (coreData.personality && coreData.personality.backstory) || rawData.backstory || 'A mysterious past awaits discovery...';

            container.innerHTML = `
                <div class="character-sheet">
                    <h3>📋 Complete Character Sheet</h3>
                    
                    <div class="character-grid">
                        <div class="character-section">
                            <h4>Core Information</h4>
                            <p><strong>Name:</strong> ${name}</p>
                            <p><strong>Species:</strong> ${species}</p>
                            <p><strong>Level:</strong> ${level}</p>
                            <p><strong>Background:</strong> ${background}</p>
                            <p><strong>Character ID:</strong> ${characterId || 'Unknown'}</p>
                        </div>

                        <div class="character-section">
                            <h4>Classes</h4>
                            ${formatClasses(classes)}
                        </div>

                        <div class="character-section">
                            <h4>Combat Stats</h4>
                            <p><strong>Armor Class:</strong> ${stats.armor_class || 10}</p>
                            <p><strong>Hit Points:</strong> ${state.current_hit_points || stats.max_hit_points || 10}</p>
                            <p><strong>Proficiency Bonus:</strong> +${stats.proficiency_bonus || 2}</p>
                        </div>

                        <div class="character-section">
                            <h4>Ability Scores</h4>
                            <div class="ability-scores">
                                ${formatAbilityScores(abilities)}
                            </div>
                        </div>

                        <div class="character-section">
                            <h4>Skills & Proficiencies</h4>
                            ${formatSkills(rawData.skill_proficiencies || coreData.proficiencies?.skills || {})}
                        </div>

                        <div class="character-section">
                            <h4>Equipment</h4>
                            ${formatCompleteEquipment(rawData, characterData)}
                        </div>

                        <div class="character-section">
                            <h4>Backstory</h4>
                            <p style="font-style: italic; max-height: 200px; overflow-y: auto;">${backstory}</p>
                        </div>

                        <div class="character-section">
                            <h4>Full Character Data</h4>
                            <button class="collapsible" onclick="toggleCollapsible(this)">
                                Show Complete JSON Data
                            </button>
                            <div class="collapsible-content">
                                <div class="json-display">${JSON.stringify(currentCharacter, null, 2)}</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        function formatSkills(skills) {
            if (!skills || Object.keys(skills).length === 0) {
                return '<p>No special skill proficiencies</p>';
            }
            
            return Object.entries(skills)
                .filter(([_, bonus]) => bonus > 0)
                .map(([skill, bonus]) => `<p>${skill}: +${bonus}</p>`)
                .join('') || '<p>No skill bonuses</p>';
        }

        function formatCompleteEquipment(rawData, characterData) {
            const parts = [];
            
            // Handle armor from raw_data
            if (rawData.armor) {
                parts.push(`<p><strong>Armor:</strong> ${rawData.armor}</p>`);
            }
            
            // Handle weapons from raw_data
            if (rawData.weapons && rawData.weapons.length > 0) {
                const weaponNames = rawData.weapons.map(weapon => 
                    typeof weapon === 'string' ? weapon : weapon.name || 'Unknown Weapon'
                );
                parts.push(`<p><strong>Weapons:</strong> ${weaponNames.join(', ')}</p>`);
            }
            
            // Handle equipment items
            if (rawData.equipment || characterData.equipment) {
                const equipment = rawData.equipment || characterData.equipment;
                parts.push(formatEquipmentItems(equipment));
            }
            
            return parts.join('') || '<p>Basic adventuring gear</p>';
        }

        function formatEquipmentItems(equipment) {
            if (!equipment || Object.keys(equipment).length === 0) {
                return '<p>Basic adventuring gear</p>';
            }
            
            const parts = [];
            
            // Handle object-style equipment (like from the backend response)
            if (typeof equipment === 'object' && !Array.isArray(equipment)) {
                const equipmentList = Object.entries(equipment)
                    .filter(([item, quantity]) => quantity > 0)
                    .map(([item, quantity]) => quantity > 1 ? `${item} (${quantity})` : item)
                    .join(', ');
                
                if (equipmentList) {
                    parts.push(`<p><strong>Equipment:</strong> ${equipmentList}</p>`);
                }
            }
            
            // Handle array-style equipment
            if (Array.isArray(equipment)) {
                parts.push('<p><strong>Items:</strong> ' + equipment.join(', ') + '</p>');
            }
            
            return parts.join('') || '<p>Basic adventuring gear</p>';
        }

        function formatSavingThrows(saves) {
            if (!saves || Object.keys(saves).length === 0) {
                return '<p>Standard saving throws</p>';
            }
            
            return Object.entries(saves)
                .map(([save, bonus]) => {
                    const sign = bonus >= 0 ? '+' : '';
                    return '<p>' + save.charAt(0).toUpperCase() + save.slice(1) + ': ' + sign + bonus + '</p>';
                })
                .join('');
        }

        function formatPersonality(core) {
            const parts = [];
            
            if (core.personality_traits && core.personality_traits.length > 0) {
                parts.push('<p><strong>Traits:</strong> ' + core.personality_traits.join(', ') + '</p>');
            }
            
            if (core.ideals && core.ideals.length > 0) {
                parts.push('<p><strong>Ideals:</strong> ' + core.ideals.join(', ') + '</p>');
            }
            
            if (core.bonds && core.bonds.length > 0) {
                parts.push('<p><strong>Bonds:</strong> ' + core.bonds.join(', ') + '</p>');
            }
            
            if (core.flaws && core.flaws.length > 0) {
                parts.push('<p><strong>Flaws:</strong> ' + core.flaws.join(', ') + '</p>');
            }
            
            return parts.join('') || '<p>Unique personality awaiting discovery</p>';
        }

        function formatEquipment(state) {
            const parts = [];
            
            if (state.weapons && state.weapons.length > 0) {
                parts.push('<p><strong>Weapons:</strong> ' + state.weapons.join(', ') + '</p>');
            }
            
            if (state.armor) {
                parts.push('<p><strong>Armor:</strong> ' + state.armor + '</p>');
            }
            
            if (state.equipment && state.equipment.length > 0) {
                parts.push('<p><strong>Equipment:</strong> ' + state.equipment.join(', ') + '</p>');
            }
            
            return parts.join('') || '<p>Basic adventuring gear</p>';
        }

        function formatSpellcasting(spellcasting) {
            if (!spellcasting.is_spellcaster) {
                return '<p>Not a spellcaster</p>';
            }
            
            const parts = [];
            
            if (spellcasting.spellcasting_classes && spellcasting.spellcasting_classes.length > 0) {
                const spellClass = spellcasting.spellcasting_classes[0];
                parts.push(`<p><strong>Spellcasting Class:</strong> ${spellClass.class}</p>`);
                
                if (spellClass.info && spellClass.info.spellcasting_ability) {
                    parts.push(`<p><strong>Spellcasting Ability:</strong> ${spellClass.info.spellcasting_ability}</p>`);
                }
                
                if (spellClass.info && spellClass.info.spell_slots) {
                    const slots = Object.entries(spellClass.info.spell_slots)
                        .map(([level, count]) => `Level ${level}: ${count}`)
                        .join(', ');
                    parts.push(`<p><strong>Spell Slots:</strong> ${slots}</p>`);
                }
            }
            
            return parts.join('') || '<p>Spellcaster - details being calculated</p>';
        }

        async function saveCharacter() {
            if (!characterId) {
                alert('No character to save.');
                return;
            }

            try {
                // Character is already saved in the database, just confirm
                showSuccess('✅ Character is already saved in the database!');
                
                // Optionally, you could add character to a user's collection here
                
            } catch (error) {
                showError(`❌ Error saving character: ${error.message}`);
            }
        }

        function exportCharacter() {
            if (!currentCharacter) {
                alert('No character to export.');
                return;
            }

            const dataStr = JSON.stringify(currentCharacter, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = `${currentCharacter.name || 'character'}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            showSuccess('📤 Character exported successfully!');
        }

        function startOver() {
            if (confirm('Are you sure you want to start over? This will clear your current character.')) {
                // Reset state
                currentCharacter = null;
                characterId = null;
                refinementCount = 0;
                
                // Clear forms
                document.getElementById('characterConcept').value = '';
                document.getElementById('refinementPrompt').value = '';
                
                // Clear displays
                document.getElementById('generationLog').innerHTML = '';
                document.getElementById('refinementHistory').innerHTML = '';
                
                // Reset progress
                updateProgress(0, 'Ready to start...');
                
                // Show only step 1
                hideElement('step2');
                hideElement('step3');
                hideElement('step4');
                showElement('step1');
            }
        }

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            // Any initialization code here
            console.log('AI Character Creator initialized');
        });

        // Test function to check if JavaScript is working
        function testFunction() {
            alert('JavaScript is working! The startCreation function exists: ' + (typeof startCreation === 'function'));
            console.log('Test function called');
            console.log('startCreation function type:', typeof startCreation);
        }
