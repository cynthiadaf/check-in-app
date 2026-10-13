const dateInput = document.querySelector("#dashboard-date");
if (dateInput) {
  dateInput.value = todayUtc();
  const load = async () => {
    const message = document.querySelector("#page-message");
    message.textContent = "Loading…";
    try {
      const data = await api(`/api/dashboard?date=${encodeURIComponent(dateInput.value)}`);
      document.querySelector("#today-count").textContent = data.today_guest_count;
      document.querySelector("#selected-count").textContent = data.selected_date_guest_count;
      document.querySelector("#common-payment").textContent = paymentLabel(data.most_common_payment_method);
      message.textContent = "";
    } catch (error) { message.textContent = error.message; }
  };
  document.querySelector("#refresh-dashboard").addEventListener("click", load);
  load();
}

