const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const modeButtons = document.querySelectorAll(".mode-btn");
const resetButton = document.getElementById("resetButton");

let activeMode = "chill_friend";
let waitingForResponse = false;

const modeLabel = {
  chill_friend: "Chill Friend",
  strict_professor: "Strict Professor",
  savage_roast: "Savage Roast",
};

function addMessage(role, text, cssClass = "") {
  const message = document.createElement("div");
  message.className = `message ${role} ${cssClass}`.trim();
  message.textContent = text;
  chatWindow.appendChild(message);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return message;
}

function addTypingIndicator() {
  const wrapper = document.createElement("div");
  wrapper.className = "message assistant";
  wrapper.innerHTML = '<div class="typing-wrap"><span class="typing-label">PersonaBot is typing</span><div class="typing"><span></span><span></span><span></span></div></div>';
  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return wrapper;
}

function setLoadingState(isLoading) {
  waitingForResponse = isLoading;
  sendButton.disabled = isLoading;
  messageInput.disabled = isLoading;
  resetButton.disabled = isLoading;
  modeButtons.forEach((button) => {
    button.disabled = isLoading;
  });
  sendButton.textContent = isLoading ? "..." : "Send";
}

function setActiveMode(mode, announce = true) {
  activeMode = mode;
  document.body.classList.remove("mode-chill_friend", "mode-strict_professor", "mode-savage_roast");
  document.body.classList.add(`mode-${mode}`);

  modeButtons.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === mode);
  });

  if (announce) {
    addMessage("notice", `Mode switched to ${modeLabel[activeMode]}.`, "notice");
  }
}

modeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    if (waitingForResponse) {
      return;
    }
    setActiveMode(button.dataset.mode);
  });
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const userText = messageInput.value.trim();
  if (!userText || waitingForResponse) {
    return;
  }

  addMessage("user", userText);
  messageInput.value = "";
  setLoadingState(true);

  const typingBubble = addTypingIndicator();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: userText,
        personality: activeMode,
      }),
    });

    const data = await response.json();
    typingBubble.remove();

    if (!response.ok) {
      addMessage("assistant", data.error || "Something went wrong. Please try again.");
      return;
    }

    addMessage("assistant", data.reply || "I have no response right now.");
  } catch (error) {
    typingBubble.remove();
    addMessage("assistant", "Network issue: unable to reach the server. Check if Flask is running.");
  } finally {
    setLoadingState(false);
    messageInput.focus();
  }
});

resetButton.addEventListener("click", async () => {
  if (waitingForResponse) {
    return;
  }

  try {
    await fetch("/reset", { method: "POST" });
  } catch (error) {
    // Local UI reset still works if backend reset fails.
  }

  chatWindow.innerHTML = "";
  addMessage("assistant", "Fresh start. Pick a mode and send your first message.");
});

setActiveMode(activeMode, false);
addMessage("assistant", "Welcome to PersonaBot. Pick a personality mode and ask me anything.");
messageInput.focus();
