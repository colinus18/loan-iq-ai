import { Link, useLocation, useNavigate } from "react-router-dom"

function Layout({ children }) {
  const location = useLocation()
  const navigate = useNavigate()

  const navItems = [
    { name: "Dashboard", path: "/dashboard" },
    { name: "Applications", path: "/applications" },
    { name: "Upload", path: "/upload" },
    { name: "History", path: "/history" },
  ]

  const handleLogout = () => {
    navigate("/logout")
  }

  return (
    <div className="app-shell">

      {/* Decorative background */}
      <div className="background-glow background-glow-one"></div>
      <div className="background-glow background-glow-two"></div>
      <div className="orbit orbit-one"></div>
      <div className="orbit orbit-two"></div>

      {/* Header */}
      <header className="app-header">

        {/* Logo */}
        <Link to="/dashboard" className="brand">
          <span className="brand-symbol">✦</span>
          <span>Loan<span className="brand-accent">Lens</span></span>
        </Link>

        {/* Navigation */}
        <nav className="main-nav">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive ? "nav-link-active" : ""}`}
              >
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* Right side */}
        <div className="header-actions">

          <Link to="/profile" className="profile-button">
            <span className="profile-icon">👤</span>
            <span>Profile</span>
          </Link>

          <button
            onClick={handleLogout}
            className="logout-button"
          >
            Logout
          </button>

        </div>

      </header>

      {/* Page content */}
      <main className="page-content">
        {children}
      </main>

    </div>
  )
}

export default Layout