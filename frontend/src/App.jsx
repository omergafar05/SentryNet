
// React's hook for remembering values that change during interaction.
import { useState } from "react";

// Import the sample data used by the table, alerts, and chart.
import { flows, alerts, trafficHistory } from "./data/mockData";

// Import the reusable chart component.
import TrafficChart from "./components/TrafficChart";

// Apply the dashboard styles.
import "./App.css";

function formatBytes(bytes) {
  if (bytes >= 1000000) return `${(bytes / 1000000).toFixed(2)} MB`;
  return `${(bytes / 1000).toFixed(1)} KB`;
}

export default function App() {
  const [page, setPage] = useState("Overview");
  const [search, setSearch] = useState("");
    // Remember the selected alert by its unique ID.
  const [selectedAlertId, setSelectedAlertId] = useState(alerts[0]?.id);

  // "All" means that this filter does not restrict the results.
  const [severityFilter, setSeverityFilter] = useState("All");
  const [reviewFilter, setReviewFilter] = useState("All");
  const [reviewed, setReviewed] = useState([]);

  const totalPackets = flows.reduce(
    (total, flow) => total + flow.packet_count,
    0,
  );
  const totalBytes = flows.reduce(
    (total, flow) => total + flow.total_bytes,
    0,
  );
  const filteredFlows = flows.filter((flow) =>
    `${flow.src_ip} ${flow.dst_ip}`.includes(search.trim()),
  );

    // On Overview, show all alerts. On Alerts, apply both filters.
  const filteredAlerts = alerts.filter((alert) => {
    if (page !== "Alerts") return true;

    const isReviewed = reviewed.includes(alert.id);

    const matchesSeverity =
      severityFilter === "All" || alert.severity === severityFilter;

    const matchesReview =
      reviewFilter === "All" ||
      (reviewFilter === "Reviewed" && isReviewed) ||
      (reviewFilter === "Unreviewed" && !isReviewed);

    // An alert must satisfy both filters to appear.
    return matchesSeverity && matchesReview;
  });

  // Keep the selected alert if it is visible.
  // Otherwise, display the first matching alert.
  // If the list is empty, selectedAlert will be undefined.
  const selectedAlert =
    filteredAlerts.find((alert) => alert.id === selectedAlertId) ??
    filteredAlerts[0];

  function markReviewed() {
    // There is nothing to review when no alerts match.
    if (!selectedAlert) return;

    setReviewed((current) =>
      current.includes(selectedAlert.id)
        ? current
        : [...current, selectedAlert.id],
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview" onClick={() => setPage("Overview")}>
          <span className="brand-icon">S</span>
          SentryNet
        </a>

        <p className="nav-label">WORKSPACE</p>

        <nav aria-label="Main navigation">
          {["Overview", "Traffic", "Alerts"].map((item) => (
            <button
              key={item}
              className={`nav-button ${page === item ? "active" : ""}`}
              aria-current={page === item ? "page" : undefined}
              onClick={() => setPage(item)}
            >
              {item}
              {item === "Alerts" && (
                <span className="nav-count">
                  {alerts.length - reviewed.length}
                </span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-note">
          <span className="status-dot" />
          Frontend preview
          <small>Backend connection coming later</small>
        </div>
      </aside>

      <main>
        <header className="page-header">
          <div>
            <p className="eyebrow">NETWORK MONITORING</p>
            <h1>{page === "Overview" ? "Network overview" : page}</h1>
            <p className="subtitle">
              Explore traffic and investigate unusual activity.
            </p>
          </div>
          <span className="demo-badge">Demo · Sample data</span>
        </header>

        {page === "Overview" && (
          <section className="stats-grid" aria-label="Traffic summary">
            <article className="stat-card">
              <span>Packets captured</span>
              <strong>{totalPackets.toLocaleString()}</strong>
              <small>Across four sample flows</small>
            </article>
            <article className="stat-card">
              <span>Traffic volume</span>
              <strong>{formatBytes(totalBytes)}</strong>
              <small>Total captured bytes</small>
            </article>
            <article className="stat-card">
              <span>Unreviewed alerts</span>
              <strong>{alerts.length - reviewed.length}</strong>
              <small>Simulated examples</small>
            </article>
            <article className="stat-card">
              <span>Data source</span>
              <strong className="accent-text">Demo</strong>
              <small>No live capture connected</small>
            </article>
          </section>
        )}

        {/* Display the chart only on Overview.
    Pass trafficHistory into the component through its "data" prop. */}
        {page === "Overview" && <TrafficChart data={trafficHistory} />}

        {(page === "Overview" || page === "Traffic") && (
          <section className="panel traffic-panel">
            <div className="panel-header">
              <div>
                <h2>Recent traffic</h2>
                <p>Aggregated traffic between source and destination addresses</p>
              </div>
              <label className="search-field">
                <span className="sr-only">Search by IP address</span>
                <input
                  type="search"
                  placeholder="Search IP address…"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </label>
            </div>

            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Source IP</th>
                    <th>Destination IP</th>
                    <th>Packets</th>
                    <th>Total bytes</th>
                    <th>Avg. packet size</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredFlows.map((flow) => (
                    <tr key={flow.id}>
                      <td className="ip-address">{flow.src_ip}</td>
                      <td className="ip-address">{flow.dst_ip}</td>
                      <td>{flow.packet_count.toLocaleString()}</td>
                      <td>{formatBytes(flow.total_bytes)}</td>
                      <td>{flow.avg_packet_size.toFixed(1)} B</td>
                    </tr>
                  ))}
                  {filteredFlows.length === 0 && (
                    <tr>
                      <td colSpan={5} className="empty-state">
                        No traffic matches that IP address.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <div className="table-footer">
              Showing {filteredFlows.length} of {flows.length} sample flows
            </div>
          </section>
        )}

        {(page === "Overview" || page === "Alerts") && (
          <div className="alerts-grid">
            <section className="panel">
              <div className="panel-header">
                <div>
                  <h2>Recent alerts</h2>
                  <p>Select an alert to inspect its details</p>
                </div>
              </div>

              {/* Filters appear only on the dedicated Alerts page. */}
              {page === "Alerts" && (
                <div className="alert-filters">
                  <label className="filter-field">
                    <span>Severity</span>
                    <select
                      value={severityFilter}
                      onChange={(event) =>
                        setSeverityFilter(event.target.value)
                      }
                    >
                      <option value="All">All severities</option>
                      <option value="High">High</option>
                      <option value="Medium">Medium</option>
                      <option value="Low">Low</option>
                    </select>
                  </label>

                  <label className="filter-field">
                    <span>Review status</span>
                    <select
                      value={reviewFilter}
                      onChange={(event) =>
                        setReviewFilter(event.target.value)
                      }
                    >
                      <option value="All">All statuses</option>
                      <option value="Unreviewed">Unreviewed</option>
                      <option value="Reviewed">Reviewed</option>
                    </select>
                  </label>
                                        {/* Reset both dropdowns without changing reviewed alerts. */}
                  <button
                    type="button"
                    className="clear-filters-button"
                    onClick={() => {
                      setSeverityFilter("All");
                      setReviewFilter("All");
                    }}
                    disabled={
                      severityFilter === "All" && reviewFilter === "All"
                    }
                  >
                    Clear filters
                  </button>
                </div>
              )}

              {/* Announce the result count when filtering changes it. */}
              <p className="alert-results" role="status">
                Showing {filteredAlerts.length} of {alerts.length} sample alerts
              </p>

              <div className="alert-list">
                {filteredAlerts.map((alert) => (
                  <button
                    key={alert.id}
                    className={`alert-row ${
                      selectedAlert?.id === alert.id ? "selected" : ""
                    }`}
                    aria-pressed={selectedAlert?.id === alert.id}
                    onClick={() => setSelectedAlertId(alert.id)}
                  >
                    <span
                      className={`severity ${alert.severity.toLowerCase()}`}
                    >
                      {alert.severity}
                    </span>
                    <span className="alert-copy">
                      <strong>{alert.title}</strong>
                      <small>
                        {reviewed.includes(alert.id)
                          ? "Reviewed"
                          : alert.source}
                      </small>
                    </span>
                    <span aria-hidden="true">→</span>
                  </button>
                ))}

                {/* An empty result is valid, so explain it clearly. */}
                {filteredAlerts.length === 0 && (
                  <p className="empty-state">
                    No alerts match these filters. Try another severity or
                    review status.
                  </p>
                )}
              </div>
            </section>

            <section className="panel details-panel">
              {/* Only read alert fields when a matching alert exists. */}
              {selectedAlert ? (
                <>
                  <div className="panel-header">
                    <h2>Alert details</h2>
                    <span
                      className={`severity ${selectedAlert.severity.toLowerCase()}`}
                    >
                      {selectedAlert.severity}
                    </span>
                  </div>

                  <h3>{selectedAlert.title}</h3>
                  <p className="detail-source">
                    Source <span>{selectedAlert.source}</span>
                  </p>
                  <p className="detail-description">
                    {selectedAlert.detail}
                  </p>

                  <div className="explanation">
                    <strong>Example explanation</strong>
                    <p>{selectedAlert.explanation}</p>
                    <small>Static demo text · Not AI-generated analysis</small>
                  </div>

                  <button
                    className="review-button"
                    onClick={markReviewed}
                    disabled={reviewed.includes(selectedAlert.id)}
                  >
                    {reviewed.includes(selectedAlert.id)
                      ? "Reviewed"
                      : "Mark reviewed"}
                  </button>
                </>
              ) : (
                <>
                  <div className="panel-header">
                    <h2>Alert details</h2>
                  </div>
                  <p className="empty-state">No matching alert to display.</p>
                </>
              )}
            </section>
          </div>
        )}
        {/* Remind users that the dashboard currently uses sample data. */}
        <footer className="page-footer">
          SentryNet · Demo data only · Review status resets on page reload
        </footer>
      </main>
    </div>
  );
}