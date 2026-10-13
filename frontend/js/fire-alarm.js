const entriesList = document.querySelector("#entries-list");
if (entriesList) {
  const selectedDate = todayUtc();
  const escapeHtml = value => value.replace(/[&<>"']/g, character => (
    {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[character]
  ));
  const load = async () => {
    const loading = document.querySelector("#fire-alarm-loading");
    const message = document.querySelector("#page-message");
    loading.hidden = false;
    message.textContent = "";
    try {
      const firstPage = await api(`/api/guest-entries?date=${selectedDate}&page=1&page_size=100`);
      const pages = [firstPage];
      for (let page = 2; page <= firstPage.total_pages; page++) {
        pages.push(await api(`/api/guest-entries?date=${selectedDate}&page=${page}&page_size=100`));
      }
      const entries = pages.flatMap(page => page.items);
      document.querySelector("#guest-count").textContent = entries.length;
      entriesList.innerHTML = entries.map(entry => (
        `<li><strong>${escapeHtml(entry.guest_name)}</strong><span>Checked in ${formatTime(entry.check_in_time)}</span></li>`
      )).join("");
      document.querySelector("#empty-state").hidden = entries.length !== 0;
    } catch (error) {
      message.textContent = error.message;
      document.querySelector("#guest-count").textContent = "—";
      entriesList.innerHTML = "";
      document.querySelector("#empty-state").hidden = true;
    } finally {
      loading.hidden = true;
    }
  };
  document.querySelector("#refresh-fire-alarm").addEventListener("click", load);
  load();
}
