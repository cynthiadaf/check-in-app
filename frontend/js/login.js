const loginForm = document.querySelector("#login-form");
if (loginForm)
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = document.querySelector("#page-message");
    message.textContent = "Signing in...";
    try {
      await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: loginForm.email.value,
          password: loginForm.password.value,
        }),
      });
      const next = new URLSearchParams(window.location.search).get("next");
      window.location.href =
        next && next.startsWith("/") ? next : "/index.html";
    } catch (error) {
      message.textContent = error.message;
    }
  });
