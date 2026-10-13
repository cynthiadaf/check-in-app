const newForm = document.querySelector("#new-entry-form");
if (newForm) newForm.addEventListener("submit", async event => {
  event.preventDefault(); const message = document.querySelector("#page-message"); message.textContent = "Saving…";
  try { await api("/api/guest-entries", {method:"POST", body:JSON.stringify({guest_name:newForm.guest_name.value, notes:newForm.notes.value})}); message.className = "message success"; message.textContent = "Check-in saved."; newForm.reset(); newForm.guest_name.focus(); }
  catch (error) { message.className = "message"; message.textContent = error.message; }
});

