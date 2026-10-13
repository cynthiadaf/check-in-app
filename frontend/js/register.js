const body = document.querySelector("#entries-body");
if (body) {
  const state = {page: 1, pageSize: 25};
  const dateInput = document.querySelector("#filter-date"), searchInput = document.querySelector("#filter-search");
  const load = async () => {
    document.querySelector("#register-loading").hidden = false;
    try {
      const query = new URLSearchParams({page: state.page, page_size: state.pageSize});
      if (dateInput.value) query.set("date", dateInput.value);
      if (searchInput.value.trim()) query.set("search", searchInput.value.trim());
      const data = await api(`/api/guest-entries?${query}`);
      body.innerHTML = data.items.map(entry => `<tr><td>${escapeHtml(entry.guest_name)}</td><td>${formatTime(entry.check_in_time)}</td><td>${escapeHtml(entry.notes)}</td><td>${paymentLabel(entry.payment_method)}</td><td><a href="/pages/edit-entry.html?id=${entry.id}">View / edit</a></td></tr>`).join("");
      document.querySelector("#empty-state").hidden = data.items.length !== 0;
      document.querySelector("#page-indicator").textContent = data.total_pages ? `Page ${data.page} of ${data.total_pages}` : "No results";
      document.querySelector("#previous-page").disabled = data.page <= 1;
      document.querySelector("#next-page").disabled = data.page >= data.total_pages || data.total_pages === 0;
      document.querySelector("#page-message").textContent = "";
    } catch (error) { document.querySelector("#page-message").textContent = error.message; } finally { document.querySelector("#register-loading").hidden = true; }
  };
  const escapeHtml = value => value.replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
  document.querySelector("#register-filters").addEventListener("submit", event => { event.preventDefault(); state.page = 1; load(); });
  document.querySelector("#previous-page").addEventListener("click", () => { state.page--; load(); });
  document.querySelector("#next-page").addEventListener("click", () => { state.page++; load(); });
  load();
}

