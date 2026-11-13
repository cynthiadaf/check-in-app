const API_BASE_URL = (
  (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL) ||
  ""
).replace(/\/$/, "");
const PAYMENT_LABELS = {
  CASH: "Cash",
  CARD: "Card",
  BANK_TRANSFER: "Bank transfer",
  MOBILE_PAYMENT: "Mobile payment",
  MEMBERSHIP: "Membership",
  NONE: "None",
  OTHER: "Other",
};
const api = async (path, options = {}) => {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    let message = "Something went wrong.";
    try {
      const body = await response.json();
      message = body.detail?.detail || body.detail || message;
    } catch (_) {}
    const error = new Error(message);
    error.status = response.status;
    if (response.status === 401 && !path.startsWith("/api/auth/"))
      window.location.href = `/pages/login.html?next=${encodeURIComponent(window.location.pathname)}`;
    throw error;
  }
  return response.status === 204 ? null : response.json();
};
const formatTime = (value) =>
  new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/London",
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
const paymentLabel = (value) =>
  value ? PAYMENT_LABELS[value] || value : "Not recorded";
const todayUtc = () => new Date().toISOString().slice(0, 10);

const isLoginPage = window.location.pathname.endsWith("/login.html");
if (!isLoginPage) {
  api("/api/auth/me")
    .then((account) => {
      const nav = document.querySelector(".site-header nav");
      if (nav) {
        const accountLink = document.createElement("a");
        accountLink.href = "/pages/password.html";
        accountLink.textContent = account.email;
        nav.append(accountLink);
        const logout = document.createElement("button");
        logout.className = "button button-small button-secondary";
        logout.type = "button";
        logout.textContent = "Sign out";
        logout.addEventListener("click", async () => {
          await api("/api/auth/logout", { method: "POST" });
          window.location.href = "/pages/login.html";
        });
        nav.append(logout);
      }
      document.documentElement.classList.remove("auth-pending");
    })
    .catch((error) => {
      if (error.status === 401) {
        window.location.href = `/pages/login.html?next=${encodeURIComponent(window.location.pathname)}`;
        return;
      }
      document.documentElement.classList.remove("auth-pending");
      const message = document.querySelector("#page-message");
      if (message) message.textContent = "Unable to verify your session. Please try again.";
    });
}
