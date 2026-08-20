import { useNavigate } from "react-router-dom"


function Dashboard() {
  const navigate = useNavigate()

  return (
    <div className="mx-auto max-w-6xl">

      {/* Hero */}
      <section className="mb-10">

        <p className="mb-3 text-sm font-medium tracking-widest text-purple-300 uppercase">
          AI-powered document intelligence
        </p>

        <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-white md:text-5xl">
          Process loan documents
          <span className="text-purple-300"> smarter.</span>
        </h1>

        <p className="mt-4 max-w-2xl text-base leading-7 text-slate-400">
          Upload, analyze and manage loan applications with intelligent
          document processing.
        </p>

      </section>

      {/* Summary Cards */}
      <section className="mb-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

        <div className="dashboard-card">
          <p className="card-label">
            Total Applications
          </p>

          <p className="card-number">
            24
          </p>

          <p className="card-description">
            All applications
          </p>
        </div>

        <div className="dashboard-card">
          <p className="card-label">
            Approved
          </p>

          <p className="card-number text-emerald-300">
            15
          </p>

          <p className="card-description">
            Ready for review
          </p>
        </div>

        <div className="dashboard-card">
          <p className="card-label">
            Pending
          </p>

          <p className="card-number text-amber-300">
            6
          </p>

          <p className="card-description">
            Being processed
          </p>
        </div>

        <div className="dashboard-card">
          <p className="card-label">
            Rejected
          </p>

          <p className="card-number text-rose-300">
            3
          </p>

          <p className="card-description">
            Need attention
          </p>
        </div>

      </section>

      {/* Upload CTA */}
      <section className="mb-10">

        <div className="upload-cta">

          <div>
            <div className="mb-3 text-2xl">
              ✦
            </div>

            <h2 className="text-2xl font-semibold text-white">
              Start a new analysis
            </h2>

            <p className="mt-2 max-w-lg text-sm leading-6 text-slate-400">
              Upload a loan document and let our AI pipeline extract,
              analyze and validate the important information.
            </p>
          </div>

          <button
            onClick={() => navigate("/upload")}
            className="primary-button"
          >
            Upload Document
            <span>→</span>
          </button>

        </div>

      </section>

      {/* Quick Actions */}
      <section>

        <div className="mb-5">
          <h2 className="text-xl font-semibold text-white">
            Quick Actions
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Manage your loan processing workspace.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">

          <button
            onClick={() => navigate("/applications")}
            className="action-card"
          >
            <span className="action-icon">📄</span>

            <div>
              <h3>
                Applications
              </h3>

              <p>
                View application history and analysis results.
              </p>
            </div>

            <span className="action-arrow">
              →
            </span>
          </button>

          <button
            onClick={() => navigate("/profile")}
            className="action-card"
          >
            <span className="action-icon">👤</span>

            <div>
              <h3>
                Profile
              </h3>

              <p>
                View and manage your profile information.
              </p>
            </div>

            <span className="action-arrow">
              →
            </span>
          </button>

          <button
            onClick={() => navigate("/history")}
            className="action-card"
          >
            <span className="action-icon">◷</span>

            <div>
              <h3>
                History
              </h3>

              <p>
                Review your previous document processing activity.
              </p>
            </div>

            <span className="action-arrow">
              →
            </span>
          </button>

        </div>

      </section>

    </div>
  )
}

export default Dashboard