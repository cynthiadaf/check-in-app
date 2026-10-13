const API_BASE_URL = (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL || "").replace(/\/$/, "");
const PAYMENT_LABELS = {CASH:"Cash",CARD:"Card",BANK_TRANSFER:"Bank transfer",MOBILE_PAYMENT:"Mobile payment",MEMBERSHIP:"Membership",NONE:"None",OTHER:"Other"};
const api = async (path, options = {}) => {
  const response = await fetch(`${API_BASE_URL}${path}`, {headers: {"Content-Type":"application/json", ...(options.headers || {})}, ...options});
  if (!response.ok) { let message = "Something went wrong."; try { const body = await response.json(); message = body.detail?.detail || body.detail || message; } catch (_) {} throw new Error(message); }
  return response.status === 204 ? null : response.json();
};
const formatTime = value => new Intl.DateTimeFormat("en-GB", {timeZone:"Europe/London", dateStyle:"medium", timeStyle:"short"}).format(new Date(value));
const paymentLabel = value => value ? (PAYMENT_LABELS[value] || value) : "Not recorded";
const todayUtc = () => new Date().toISOString().slice(0, 10);

