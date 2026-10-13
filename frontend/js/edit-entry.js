const editForm = document.querySelector("#edit-entry-form");
if (editForm) {
  const id = new URLSearchParams(location.search).get("id"), message = document.querySelector("#page-message");
  const load = async () => { try { const entry = await api(`/api/guest-entries/${id}`); editForm.dataset.entryId = id; document.querySelector("#guest-name").value = entry.guest_name; document.querySelector("#check-in-time").value = formatTime(entry.check_in_time); document.querySelector("#notes").value = entry.notes; document.querySelector("#payment-method").value = entry.payment_method || ""; } catch (error) { message.textContent = error.message; } };
  editForm.addEventListener("submit", async event => { event.preventDefault(); message.textContent = "Saving…"; try { await api(`/api/guest-entries/${id}`, {method:"PATCH", body:JSON.stringify({notes:document.querySelector("#notes").value, payment_method:document.querySelector("#payment-method").value || null})}); message.className = "message success"; message.textContent = "Changes saved."; } catch (error) { message.className = "message"; message.textContent = error.message; } });
  document.querySelector("#delete-entry").addEventListener("click", async () => { if (!confirm("Delete this guest entry permanently?")) return; try { await api(`/api/guest-entries/${id}`, {method:"DELETE"}); location.href = "/pages/register.html"; } catch (error) { message.textContent = error.message; } });
  load();
}

