import { useState } from "react";
import "./App.css";

const flows = [
  {
    id: 1,
    src_ip: "192.0.2.10",
    dst_ip: "198.51.100.20",
    packet_count: 312,
    total_bytes: 221000,
    avg_packet_size: 708.3,
  },
  {
    id: 2,
    src_ip: "203.0.113.15",
    dst_ip: "192.0.2.10",
    packet_count: 148,
    total_bytes: 98000,
    avg_packet_size: 662.2,
  },
  {
    id: 3,
    src_ip: "192.0.2.10",
    dst_ip: "203.0.113.15",
    packet_count: 64,
    total_bytes: 6272,
    avg_packet_size: 98,
  },
  {
    id: 4,
    src_ip: "198.51.100.20",
    dst_ip: "192.0.2.10",
    packet_count: 420,
    total_bytes: 310000,
    avg_packet_size: 738.1,
  },
];

const alerts = [
  {
    id: 1,
    severity: "High",
    title: "Unusual port activity",
    source: "192.0.2.10",
    detail: "24 destination ports contacted within five seconds.",
    explanation:
      "This example shows activity worth investigating. Multiple destination ports alone do not prove an attack.",
  },
  {
    id: 2,
    severity: "Medium",
    title: "Traffic spike",
    source: "198.51.100.20",
    detail: "Traffic volume increased above the sample baseline.",
    explanation:
      "A large download or software update could explain this increase. Review the activity before drawing conclusions.",
  },
  {
    id: 3,
    severity: "Low",
    title: "New connection",
    source: "203.0.113.15",
    detail: "A connection to a previously unseen address was recorded.",
    explanation:
      "New connections are common during normal browsing. This example is informational.",
  },
];

function formatBytes(bytes) {
  if (bytes >= 1000000) return `${(bytes / 1000000).toFixed(2)} MB`;
  return `${(bytes / 1000).toFixed(1)} KB`;
}

export default function App() {
  const [page, setPage] = useState("Overview");
  const [search, setSearch] = useState("");
  const [selectedAlert, setSelectedAlert] = useState(alerts[0]);
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

  function markReviewed() {
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

              <div className="alert-list">
                {alerts.map((alert) => (
                  <button
                    key={alert.id}
                    className={`alert-row ${
                      selectedAlert.id === alert.id ? "selected" : ""
                    }`}
                    aria-pressed={selectedAlert.id === alert.id}
                    onClick={() => setSelectedAlert(alert)}
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
              </div>
            </section>

            <section className="panel details-panel">
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
              <p className="detail-description">{selectedAlert.detail}</p>

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
            </section>
          </div>
        )}

        <footer className="page-footer">
          SentryNet · Demo data only · Review status resets on page reload
        </footer>
      </main>
    </div>
  );
}