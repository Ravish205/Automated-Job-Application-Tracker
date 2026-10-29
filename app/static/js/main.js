/**
 * Main application JavaScript
 */

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Lucide icons if available
  if (window.lucide && typeof window.lucide.createIcons === "function") {
    window.lucide.createIcons();
  }

  // Dismissible alerts
  const alertCloseButtons = document.querySelectorAll(".alert .btn-close, .alert [data-dismiss='alert']");
  alertCloseButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const alertElem = e.target.closest(".alert");
      if (alertElem) {
        alertElem.remove();
      }
    });
  });

  // Modal triggers
  const modalTriggers = document.querySelectorAll("[data-modal-target]");
  modalTriggers.forEach((trigger) => {
    trigger.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = trigger.getAttribute("data-modal-target");
      const modal = document.getElementById(targetId);
      if (modal) {
        modal.classList.add("active");
        const autoFocus = modal.querySelector("[autofocus], input:not([type=hidden])");
        if (autoFocus) autoFocus.focus();
      }
    });
  });

  const modalCloses = document.querySelectorAll("[data-modal-close]");
  modalCloses.forEach((closeBtn) => {
    closeBtn.addEventListener("click", () => {
      const modal = closeBtn.closest(".modal-overlay");
      if (modal) modal.classList.remove("active");
    });
  });

  // Close modals on ESC key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const activeModal = document.querySelector(".modal-overlay.active");
      if (activeModal) activeModal.classList.remove("active");
    }
  });
});

/**
 * Helper to fetch JSON with CSRF token included
 */
async function fetchWithCsrf(url, options = {}) {
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content");
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const error = new Error(errorData.error || `HTTP error ${response.status}`);
    error.status = response.status;
    error.data = errorData;
    throw error;
  }

  return response.json();
}

