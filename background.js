// Set your Gemini API key in the Extension Popup Settings (or configure here)
const DEFAULT_API_KEY = "";

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(['geminiApiKey'], (result) => {
    if (!result.geminiApiKey) {
      chrome.storage.local.set({ geminiApiKey: DEFAULT_API_KEY });
    }
  });
});

const MODELS = [
  "gemini-3.5-flash-lite",
  "gemini-3-flash-preview",
  "gemini-2.5-flash"
];

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "translate_incoming") {
    const prompt = `Translate the following chat message (which may be in English, Banglish/Latin script Bengali, or another language) into natural, fluent Bengali (বাংলা). Output ONLY the final Bengali translation in Bengali script. Do not output English or explanations or quotes:\n\n${request.text}`;
    
    callGeminiWaterfall({ contents: [{ parts: [{ text: prompt }] }] }, (geminiRes) => {
      if (geminiRes && geminiRes.success) {
        sendResponse(geminiRes);
      } else {
        fallbackGoogleTranslate(request.text, 'bn', sendResponse);
      }
    });
    return true;
  } 
  
  else if (request.action === "translate_outgoing") {
    let toneInstruction = "fluent, natural, grammatically correct, and professional English suitable for a workplace or client conversation";
    if (request.tone === "casual") {
      toneInstruction = "friendly, warm, natural, and polite conversational English";
    } else if (request.tone === "executive") {
      toneInstruction = "formal, polished, executive-level corporate English";
    }

    const prompt = `You are a professional business translator and editor. Translate the following Banglish (Bengali written in English letters or Latin script) or Bengali text into ${toneInstruction}. Output ONLY the translated English sentence(s). Do not add explanations, notes, or quotation marks:\n\n${request.text}`;
    
    callGeminiWaterfall({ contents: [{ parts: [{ text: prompt }] }] }, (geminiRes) => {
      if (geminiRes && geminiRes.success) {
        sendResponse(geminiRes);
      } else {
        fallbackGoogleTranslate(request.text, 'en', sendResponse);
      }
    });
    return true;
  }

  else if (request.action === "ai_chat") {
    const contents = request.messages || [{ role: 'user', parts: [{ text: request.text }] }];
    const developerPrompt = `You are a helpful, intelligent, polite, and professional AI assistant created by Md. Rifayet Hossen (commonly known as Refayet, Rifat, or Rifayet / রিফাত / রেফায়েত) for this Chat Translator AI extension.

DEVELOPER PROFILE & BIO:
- Name: Md. Rifayet Hossen (Rifat / Refayet / Rifayet)
- Profession: Professional Shopify Developer & E-commerce/Web Specialist.
- Expertise: Custom Shopify store development, Shopify theme customization, Liquid coding, bug fixing, responsive web design, performance optimization, and custom extension/software development.
- Phone / WhatsApp: 01952321390 (+8801952321390)
- Email: mdrifayethossen@gmail.com
- Facebook: https://www.facebook.com/Rifayet221/
- GitHub: https://github.com/rifat3790

BEHAVIOR GUIDELINES:
1. When any user mentions or asks about "Refayet", "Rifat", "Rifayet", "developer", "creator", "tumi k", "developer k", "who created you", or asks for information about the developer:
   - Speak proudly, warmly, and respectfully about Md. Rifayet Hossen (Rifat).
   - Explain that he is a talented professional Shopify Developer and the creator of this Chat Translator AI extension.
   - Highlight that he provides premium Shopify store development, theme customization, and e-commerce solutions.
2. If the user asks for his contact info, phone number, WhatsApp, email, or social media links (e.g. for freelance work, projects, or inquiries), provide all his official contact channels cleanly formatted:
   - 📱 WhatsApp / Phone: 01952321390 (+8801952321390)
   - ✉️ Email: mdrifayethossen@gmail.com
   - 🌐 Facebook: https://www.facebook.com/Rifayet221/
   - 💻 GitHub: https://github.com/rifat3790
3. Always match the user's language (Bengali বাংলা, Banglish, or English) in a natural, polite, and friendly professional tone.
4. For all other questions (client emails, code, translation, general knowledge), answer accurately, concisely, and helpfully.`;

    const payload = {
      contents: contents,
      systemInstruction: {
        parts: [{ text: developerPrompt }]
      }
    };

    callGeminiWaterfall(payload, (geminiRes) => {
      sendResponse(geminiRes);
    });
    return true;
  }
});

// Fallback to free Google Translate API
function fallbackGoogleTranslate(text, targetLang, sendResponse) {
  const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=${targetLang}&dt=t&q=${encodeURIComponent(text)}`;
  fetch(url)
    .then(r => r.json())
    .then(data => {
      if (data && data[0]) {
        const translatedText = data[0].map(item => item[0]).filter(Boolean).join('');
        sendResponse({ success: true, text: translatedText });
      } else {
        sendResponse({ success: false, error: "Translation failed" });
      }
    })
    .catch(err => {
      sendResponse({ success: false, error: err.message });
    });
}

// Waterfall across multiple Gemini models
function callGeminiWaterfall(payload, sendResponse, modelIndex = 0) {
  if (modelIndex >= MODELS.length) {
    sendResponse({ success: false, error: "All AI models reached quota. Please try again shortly." });
    return;
  }

  const model = MODELS[modelIndex];

  chrome.storage.local.get(['geminiApiKey'], (result) => {
    const apiKey = result.geminiApiKey || DEFAULT_API_KEY;
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
    
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        console.warn(`Model ${model} error:`, data.error.message);
        if (data.error.code === 429 || data.error.code === 404 || data.error.status === 'RESOURCE_EXHAUSTED') {
          console.log(`Switching from ${model} to next model...`);
          callGeminiWaterfall(payload, sendResponse, modelIndex + 1);
          return;
        }
        sendResponse({ success: false, error: data.error.message });
      } else if (data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts) {
        const parts = data.candidates[0].content.parts;
        const textPart = parts.find(p => p.text && !p.thought) || parts[parts.length - 1];
        if (textPart && textPart.text) {
          sendResponse({ success: true, text: textPart.text.trim() });
        } else {
          callGeminiWaterfall(payload, sendResponse, modelIndex + 1);
        }
      } else {
        callGeminiWaterfall(payload, sendResponse, modelIndex + 1);
      }
    })
    .catch(error => {
      console.warn(`Model ${model} request failed:`, error);
      callGeminiWaterfall(payload, sendResponse, modelIndex + 1);
    });
  });
}
