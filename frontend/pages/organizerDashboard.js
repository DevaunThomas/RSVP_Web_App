// Render the organizer dashboard page
export function renderOrganizerDashboard(mainContent) {
  mainContent.innerHTML = `
    <section class="dashboard-page">
        <div class="dashboard-header">
            <h1>Organizer Dashboard</h1>
            <p>
                Manage your campus events and monitor attendee registrations.
            </p>
        </div>

        <div class="dashboard-grid">
            <section class="dashboard-card">
                <div class="dashboard-card__header">
                    <h2>My Events</h2>
                
                    <a href="#/create-event" class="button dashboard-action">
                        Create Event
                    </a>
                </div>
                
                <div class="dashboard-list">
                    <p>You haven't created any events yet.</p>
                </div>
                </section>

            <section class="dashboard-card">
                <h2>Recent RSVPs</h2>

                <div class="dashboard-list">
                    <p>No attendee registrations yet.</p>
                </div>
            </section>
        </div>
    </section>
  `;
}