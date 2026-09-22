const form = document.querySelector("#chat-form");
const messageInput = document.querySelector("#message");
const messages = document.querySelector("#messages");
const actionInput = document.querySelector("#action");
const educationLevelInput = document.querySelector("#education-level");
const planForm = document.querySelector("#plan-form");
const planResult = document.querySelector("#plan-result");
let conversationId = null;

function addMessage(role, content) {
  const item = document.createElement("p");
  item.className = `message message-${role}`;
  item.textContent = content;
  messages.append(item);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) return;

  const emptyState = messages.querySelector(".empty-state");
  if (emptyState) emptyState.remove();

  addMessage("user", message);
  messageInput.value = "";

  const button = form.querySelector("button");
  button.disabled = true;
  button.textContent = "Thinking...";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        action: actionInput.value,
        education_level: educationLevelInput.value,
        conversation_id: conversationId,
      }),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error?.message || "Request failed.");
    conversationId = body.conversation_id;
    addMessage("assistant", body.message.content);
    addMessage("notice", body.uncertainty_notice);
  } catch (error) {
    addMessage("notice", error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Send question";
    messageInput.focus();
  }
});

planForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = planForm.querySelector("button");
  button.disabled = true;
  button.textContent = "Building...";
  try {
    const response = await fetch("/api/plans", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        subjects: document.querySelector("#subjects").value.split(",").map((item) => item.trim()),
        minutes_per_day: Number(document.querySelector("#minutes-per-day").value),
        target_date: document.querySelector("#target-date").value,
        education_level: educationLevelInput.value,
      }),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error?.message || "Could not create plan.");
    planResult.textContent = body.plan.content;
  } catch (error) {
    planResult.textContent = error.message;
  } finally {
    button.disabled = false;
    button.textContent = "Create plan";
  }
});
