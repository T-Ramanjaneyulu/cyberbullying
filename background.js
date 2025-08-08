chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "analyzeText") {
    fetch("http://localhost:5003/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: request.text }),
    })
      .then((res) => res.json())
      .then((data) => sendResponse(data))
      .catch((error) => sendResponse({ error: error.message }));

    return true; // keep channel open for async
  }
});
