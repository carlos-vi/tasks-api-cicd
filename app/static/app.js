const form = document.getElementById("form");
const titleInput = document.getElementById("title");
const list = document.getElementById("tasks");
const message = document.getElementById("message");
const button = form.querySelector("button");

function showMessage(text, isError = false) {
  message.textContent = text;
  message.classList.toggle("error", isError);
}

function render(tasks) {
  list.replaceChildren();
  if (tasks.length === 0) {
    showMessage("There are no tasks yet.");
    return;
  }
  showMessage("");
  for (const task of tasks) {
    const item = document.createElement("li");
    const id = document.createElement("span");
    id.className = "id";
    id.textContent = `#${task.id}`;
    const title = document.createElement("span");
    // textContent (not innerHTML): the title is plain text, never HTML, so nobody can inject code
    title.textContent = task.title;
    item.append(id, title);
    list.append(item);
  }
}

async function loadTasks() {
  try {
    // Relative path: the page and the API live on the same server, so no configuration is needed
    const response = await fetch("/tasks");
    if (!response.ok) throw new Error(`Error ${response.status}`);
    render(await response.json());
  } catch (error) {
    showMessage(`Could not load the tasks (${error.message}).`, true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = titleInput.value.trim();
  if (!title) return;

  button.disabled = true;
  try {
    const response = await fetch("/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    if (!response.ok) throw new Error(`Error ${response.status}`);
    titleInput.value = "";
    await loadTasks();
  } catch (error) {
    showMessage(`Could not create the task (${error.message}).`, true);
  } finally {
    button.disabled = false;
    titleInput.focus();
  }
});

loadTasks();
