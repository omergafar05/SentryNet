// "data" is a prop: information the parent component passes to this component.
export default function TrafficChart({ data }) {
  // Handle an empty list instead of displaying a misleading blank chart.
  if (data.length === 0) {
    return (
      <section className="panel traffic-chart">
        <div className="panel-header">
          <h2>Traffic activity</h2>
        </div>
        <p className="empty-state">No traffic measurements available.</p>
      </section>
    );
  }

  // Find the largest packet count to scale the bars.
  // The minimum of 1 prevents division by zero when every count is zero.
  const highestCount = Math.max(1, ...data.map((point) => point.packets));

  return (
    <section className="panel traffic-chart">
      <div className="panel-header">
        <div>
          <h2>Traffic activity</h2>
          <p>Sample packets captured per five-second interval</p>
        </div>
        <span className="demo-badge">Sample data</span>
      </div>

      {/* Allow horizontal scrolling when the screen is narrow. */}
      <div className="chart-scroll">
        <ol className="traffic-bars" aria-label="Sample packet counts over time">
          {data.map((point) => (
            <li className="chart-column" key={point.time}>
              {/* Every bar uses the same available vertical space. */}
              <div className="chart-track">
                {/* The exact count remains readable above each bar. */}
                <span className="chart-value">{point.packets}</span>

                {/* A larger packet count produces a taller bar.
                    The visible text already explains the value,
                    so screen readers can ignore this decorative shape. */}
                <div
                  className="chart-bar"
                  style={{
                    height: `${(point.packets / highestCount) * 100}%`,
                  }}
                  aria-hidden="true"
                />
              </div>

              <span className="chart-time">{point.time}</span>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}