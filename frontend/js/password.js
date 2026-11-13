const passwordForm = document.querySelector("#password-form");
if (passwordForm)
  passwordForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = document.querySelector("#page-message");
    if (
      passwordForm.new_password.value !== passwordForm["confirm-password"].value
    ) {
      message.textContent = "New passwords do not match.";
      return;
    }
    message.textContent = "Updating...";
    try {
      await api("/api/auth/password", {
        method: "POST",
        body: JSON.stringify({
          current_password: passwordForm.current_password.value,
          new_password: passwordForm.new_password.value,
        }),
      });
      message.className = "message success";
      message.textContent = "Password updated.";
      passwordForm.reset();
    } catch (error) {
      message.className = "message";
      message.textContent = error.message;
    }
  });
