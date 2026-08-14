import { getCurrentUser } from "../utils/session.js";
import { authenticatedFetch } from "../utils/api.js";
import {
  updateNotificationBadge,
} from "../components/navbar.js";

const API_BASE_URL = "http://127.0.0.1:5000/api";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatNotificationDate(value) {
  if (!value) {
    return "Date unavailable";
  }

  const normalizedValue = String(value).includes("T")
    ? String(value)
    : `${String(value).replace(" ", "T")}Z`;

  const date = new Date(normalizedValue);

  if (Number.isNaN(date.getTime())) {
    return "Date unavailable";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function getNotificationTypeClass(type) {
  const normalizedType = String(type || "").toLowerCase();

  return [
    "update",
    "cancellation",
    "reminder",
  ].includes(normalizedType)
    ? normalizedType
    : "general";
}

function renderLoadError(mainContent, message) {
  mainContent.innerHTML = `
    <section class="page-section">
      <div class="state-message state-message--error">
        <h1>Notifications could not be loaded</h1>
        <p>${escapeHtml(message)}</p>

        <a href="#/events" class="button button--primary">
          Return to Events
        </a>
      </div>
    </section>
  `;
}

export async function renderNotifications(mainContent) {
  const currentUser = getCurrentUser();

  if (!currentUser) {
    window.location.hash = "#/login";
    return;
  }

  mainContent.innerHTML = `
    <section class="page-section">
      <div class="state-message">
        <h1>Loading notifications...</h1>
      </div>
    </section>
  `;

  try {
    const response = await authenticatedFetch(
      `${API_BASE_URL}/users/${currentUser.user_id}/notifications`
    );

    const notifications = await response.json();

    if (!response.ok) {
      throw new Error(
        notifications.error ||
          "Unable to load notifications."
      );
    }

    const unreadCount = notifications.filter(
      (notification) =>
        !Boolean(notification.read_status)
    ).length;

    mainContent.innerHTML = `
      <section class="page-section notifications-page">
        <div class="notifications-page__header">
          <div>
            <h1>Notifications</h1>

            <p>
              ${
                unreadCount === 0
                  ? "You have no unread notifications."
                  : `${unreadCount} unread ${
                      unreadCount === 1
                        ? "notification"
                        : "notifications"
                    }.`
              }
            </p>
          </div>

          <button
            type="button"
            id="mark-all-notifications-read"
            class="button button--secondary"
            ${unreadCount === 0 ? "disabled" : ""}
          >
            Mark All as Read
          </button>
        </div>

        <div class="notification-list">
          ${
            notifications.length === 0
              ? `
                <div class="notification-list__empty">
                  <h2>No notifications yet</h2>
                  <p>
                    Event updates, reminders, cancellations,
                    and waitlist changes will appear here.
                  </p>
                </div>
              `
              : notifications
                  .map((notification) => {
                    const isRead = Boolean(
                      notification.read_status
                    );

                    const typeClass =
                      getNotificationTypeClass(
                        notification.notification_type
                      );

                    return `
                      <article
                        class="notification-card ${
                          isRead
                            ? ""
                            : "notification-card--unread"
                        }"
                      >
                        <div class="notification-card__header">
                          <span
                            class="notification-type notification-type--${typeClass}"
                          >
                            ${escapeHtml(
                              notification.notification_type ||
                                "General"
                            )}
                          </span>

                          <time>
                            ${escapeHtml(
                              formatNotificationDate(
                                notification.sent_at
                              )
                            )}
                          </time>
                        </div>

                        <h2>
                          ${escapeHtml(
                            notification.event_title ||
                              "Campus Event"
                          )}
                        </h2>

                        <p>
                          ${escapeHtml(notification.message)}
                        </p>

                        <div class="notification-card__footer">
                          <a
                            href="#/event/${Number(
                              notification.event_id
                            )}"
                            class="button button--primary"
                          >
                            View Event
                          </a>

                          <div class="notification-card__actions">
                            ${
                              isRead
                                ? ""
                                : `
                                  <button
                                    type="button"
                                    class="button button--secondary mark-notification-read"
                                    data-notification-id="${Number(
                                      notification.notification_id
                                    )}"
                                  >
                                    Mark as Read
                                  </button>
                                `
                            }

                            <button
                              type="button"
                              class="button button--danger delete-notification"
                              data-notification-id="${Number(
                                notification.notification_id
                              )}"
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      </article>
                    `;
                  })
                  .join("")
          }
        </div>
      </section>
    `;

    const markAllButton = mainContent.querySelector(
      "#mark-all-notifications-read"
    );

    markAllButton?.addEventListener("click", async () => {
      markAllButton.disabled = true;
      markAllButton.textContent = "Updating...";

      try {
        const markAllResponse =
          await authenticatedFetch(
            `${API_BASE_URL}/users/${currentUser.user_id}/notifications/read-all`,
            {
              method: "PATCH",
            }
          );

        const result = await markAllResponse.json();

        if (!markAllResponse.ok) {
          throw new Error(
            result.error ||
              "Unable to mark notifications as read."
          );
        }

        await updateNotificationBadge();
        await renderNotifications(mainContent);
      } catch (error) {
        window.alert(error.message);
        markAllButton.disabled = false;
        markAllButton.textContent = "Mark All as Read";
      }
    });

    const markReadButtons = mainContent.querySelectorAll(
      ".mark-notification-read"
    );

    markReadButtons.forEach((button) => {
      button.addEventListener("click", async () => {
        const notificationId = Number(
          button.dataset.notificationId
        );

        button.disabled = true;
        button.textContent = "Updating...";

        try {
          const markReadResponse =
            await authenticatedFetch(
              `${API_BASE_URL}/notifications/${notificationId}/read`,
              {
                method: "PATCH",
              }
            );

          const result = await markReadResponse.json();

          if (!markReadResponse.ok) {
            throw new Error(
              result.error ||
                "Unable to mark the notification as read."
            );
          }

          await updateNotificationBadge();
          await renderNotifications(mainContent);
        } catch (error) {
          window.alert(error.message);
          button.disabled = false;
          button.textContent = "Mark as Read";
        }
      });
    });

    const deleteButtons = mainContent.querySelectorAll(
      ".delete-notification"
    );

    deleteButtons.forEach((button) => {
      button.addEventListener("click", async () => {
        const notificationId = Number(
          button.dataset.notificationId
        );

        const confirmed = window.confirm(
          "Delete this notification?"
        );

        if (!confirmed) {
          return;
        }

        button.disabled = true;
        button.textContent = "Deleting...";

        try {
          const deleteResponse =
            await authenticatedFetch(
              `${API_BASE_URL}/notifications/${notificationId}`,
              {
                method: "DELETE",
              }
            );

          const result = await deleteResponse.json();

          if (!deleteResponse.ok) {
            throw new Error(
              result.error ||
                "Unable to delete the notification."
            );
          }

          await updateNotificationBadge();
          await renderNotifications(mainContent);
        } catch (error) {
          window.alert(error.message);
          button.disabled = false;
          button.textContent = "Delete";
        }
      });
    });

    await updateNotificationBadge();
  } catch (error) {
    renderLoadError(mainContent, error.message);
  }
}