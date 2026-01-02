import './DashboardCard.css'

/**
 * DashboardCard Component
 * Reusable card component for displaying notes and reminders
 */
function DashboardCard({ title, content, timestamp, onClick, type = 'note' }) {
  const formatDate = (date) => {
    if (!date) return ''
    const d = new Date(date)
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className={`dashboard-card ${type}`} onClick={onClick}>
      <div className="dashboard-card-header">
        <h3 className="dashboard-card-title">{title}</h3>
        {timestamp && (
          <span className="dashboard-card-timestamp">
            {formatDate(timestamp)}
          </span>
        )}
      </div>
      {content && (
        <p className="dashboard-card-content">{content}</p>
      )}
    </div>
  )
}

export default DashboardCard

