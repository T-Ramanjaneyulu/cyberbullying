let lastAnalyzedText = "";
let typingBoxObserver = null;
let messageBoxObserver = null;

function sendForPrediction(text) {
  chrome.runtime.sendMessage({ action: "analyzeText", text }, (response) => {
    if (!response) {
      console.error("❌ No response from backend");
      return;
    }

    const prediction = response.prediction;
    const confidence = response.confidence || 0;
    const lowerText = text.toLowerCase();
    const keywords = [
      "hate you",
      "disgusting loser",
      "fuck you",
      "bitch",
      "slut",
      "idiot",
      "stupid",
      "retard",
    ];
    const keywordMatch = keywords.some((kw) => lowerText.includes(kw));

    console.log("✅ Text:", text);
    console.log("📊 Prediction:", prediction, "| Confidence:", confidence);

    if (
      (prediction === "hate" || prediction === "offensive") &&
      confidence > 0.5
    ) {
      alert("⚠️ Hate Speech Detected: " + text);
    } else if (keywordMatch) {
      alert("⚠️ Potential Hate Speech Detected (Keyword Match): " + text);
    } else {
      console.log("ℹ️ No hate speech detected for: " + text);
    }
  });
}

function getCurrentPlatform() {
  const host = window.location.hostname;
  if (host.includes("web.whatsapp.com")) return "whatsapp";
  if (host.includes("web.telegram.org") || host.includes("webk.telegram.org"))
    return "telegram";
  if (host.includes("instagram.com")) return "instagram";
  return null;
}

/* 🟢 WHATSAPP SUPPORT */

function attachWhatsAppTypingObserver() {
  const inputBox = document.querySelector(
    'div[contenteditable="true"][role="textbox"][aria-label="Type a message"]'
  );
  if (!inputBox) return;

  if (typingBoxObserver) typingBoxObserver.disconnect();

  typingBoxObserver = new MutationObserver(() => {
    const spans = inputBox.querySelectorAll(
      'span.selectable-text.copyable-text.false[data-lexical-text="true"]'
    );
    const typedText = Array.from(spans)
      .map((el) => el.innerText)
      .join(" ")
      .trim();
    if (typedText && typedText !== lastAnalyzedText) {
      lastAnalyzedText = typedText;
      sendForPrediction(typedText);
    }
  });

  typingBoxObserver.observe(inputBox, {
    childList: true,
    subtree: true,
    characterData: true,
  });

  console.log("⌨️ WhatsApp typing observer re-attached.");
}

function attachWhatsAppMessageObserver() {
  const app = document.querySelector("#app");
  if (!app) return;

  if (messageBoxObserver) messageBoxObserver.disconnect();

  messageBoxObserver = new MutationObserver(() => {
    const elements = document.querySelectorAll(
      "div.message-in span.selectable-text, div.message-out span.selectable-text"
    );
    if (!elements.length) return;

    const last = elements[elements.length - 1];
    const text = last?.innerText?.trim() || "";
    if (text && text !== lastAnalyzedText) {
      lastAnalyzedText = text;
      sendForPrediction(text);
    }
  });

  messageBoxObserver.observe(app, { childList: true, subtree: true });
  console.log("👀 WhatsApp message observer re-attached.");
}

function watchWhatsAppChatSwitches() {
  const container = document.querySelector("#app");
  if (!container) {
    console.warn("⏳ Waiting for WhatsApp #app...");
    return setTimeout(watchWhatsAppChatSwitches, 2000);
  }

  const chatSwitchObserver = new MutationObserver(() => {
    attachWhatsAppTypingObserver();
    attachWhatsAppMessageObserver();
  });

  chatSwitchObserver.observe(container, { childList: true, subtree: true });
  console.log("🔄 Watching for WhatsApp chat switches.");
}

/* 🔵 TELEGRAM SUPPORT */
function observeTelegramTyping() {
  const inputBox = document.querySelector("#editable-message-text");

  if (!inputBox) {
    console.warn("⏳ Retrying Telegram input...");
    return setTimeout(observeTelegramTyping, 2000);
  }

  const observer = new MutationObserver(() => {
    const text = inputBox.innerText.trim();
    if (text && text !== lastAnalyzedText) {
      lastAnalyzedText = text;
      sendForPrediction(text);
    }
  });

  observer.observe(inputBox, {
    childList: true,
    subtree: true,
    characterData: true,
  });

  console.log("⌨️ Telegram typing observer attached.");
}

function observeTelegramMessages() {
  const body = document.querySelector("body");

  const observer = new MutationObserver(() => {
    const elements = document.querySelectorAll(".message .text-content");
    if (!elements.length) return;

    const last = elements[elements.length - 1];
    const text = last?.innerText?.trim() || "";
    if (text && text !== lastAnalyzedText) {
      lastAnalyzedText = text;
      sendForPrediction(text);
    }
  });

  observer.observe(body, { childList: true, subtree: true });
  console.log("👀 Telegram message observer attached.");
}

/* 🟣 INSTAGRAM SUPPORT */

function observeInstagramTyping() {
  console.log("⏳ Waiting for Instagram input...");

  const observer = new MutationObserver(() => {
    const inputBox = document.querySelector(
      'p[dir="ltr"] span[data-lexical-text="true"]'
    );

    if (inputBox) {
      console.log("✅ Instagram input box found.");
      observer.disconnect();

      const textObserver = new MutationObserver(() => {
        const typedText = inputBox.textContent.trim();
        if (typedText && typedText !== lastAnalyzedText) {
          lastAnalyzedText = typedText;
          sendForPrediction(typedText);
        }
      });

      textObserver.observe(inputBox, {
        childList: true,
        characterData: true,
        subtree: true,
      });

      console.log("⌨️ Instagram typing observer attached.");
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}

function observeInstagramMessages() {
  const chatContainer = document.querySelector('[role="main"]');

  if (!chatContainer) {
    console.warn("⏳ Waiting for Instagram chat container...");
    return setTimeout(observeInstagramMessages, 2000);
  }

  const observer = new MutationObserver(() => {
    const messageBubbles = document.querySelectorAll(
      '[role="main"] div._a9zr span'
    );

    if (!messageBubbles.length) return;

    const last = messageBubbles[messageBubbles.length - 1];
    const text = last?.innerText?.trim() || "";
    if (text && text !== lastAnalyzedText) {
      lastAnalyzedText = text;
      sendForPrediction(text);
    }
  });

  observer.observe(chatContainer, { childList: true, subtree: true });
  console.log("👀 Instagram message observer attached.");
}

function watchInstagramChatSwitches() {
  const mainContainer = document.querySelector('[role="main"]');
  if (!mainContainer) {
    console.warn("⏳ Waiting for Instagram main container...");
    return setTimeout(watchInstagramChatSwitches, 2000);
  }

  const chatSwitchObserver = new MutationObserver(() => {
    console.log("🔁 Instagram chat switched. Reattaching observers...");
    observeInstagramMessages();
    observeInstagramTyping();
  });

  chatSwitchObserver.observe(mainContainer, {
    childList: true,
    subtree: true,
  });

  console.log("🔄 Watching for Instagram chat switches.");
}

/* 🚀 INIT SCRIPT */
setTimeout(() => {
  const platform = getCurrentPlatform();
  if (platform === "whatsapp") {
    watchWhatsAppChatSwitches();
    attachWhatsAppTypingObserver();
    attachWhatsAppMessageObserver();
  } else if (platform === "telegram") {
    observeTelegramMessages();
    observeTelegramTyping();
  } else if (platform === "instagram") {
    watchInstagramChatSwitches();
    observeInstagramMessages();
    observeInstagramTyping();
  } else {
    console.warn("⚠️ Platform not supported.");
  }
}, 3000);
