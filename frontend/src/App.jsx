import { BrowserRouter, Routes, Route } from "react-router-dom"

import Login from "./pages/Login"
import Dashboard from "./pages/Dashboard"
import UploadDocuments from "./pages/UploadDocuments"
import Processing from "./pages/Processing"
import Results from "./pages/Results"
import History from "./pages/History"
import Profile from "./pages/Profile"
import Applications from "./pages/Applications"
import Logout from "./pages/Logout"

import Layout from "./components/Layout"

function App() {
  return (
    <BrowserRouter>

      <Routes>

        {/* Login does not use the main header */}
        <Route path="/" element={<Login />} />

        {/* Main application layout */}
        <Route
          path="/dashboard"
          element={
            <Layout>
              <Dashboard />
            </Layout>
          }
        />

        <Route
          path="/upload"
          element={
            <Layout>
              <UploadDocuments />
            </Layout>
          }
        />

        <Route
          path="/processing"
          element={
            <Layout>
              <Processing />
            </Layout>
          }
        />

        <Route
          path="/results"
          element={
            <Layout>
              <Results />
            </Layout>
          }
        />

        <Route
          path="/history"
          element={
            <Layout>
              <History />
            </Layout>
          }
        />

        <Route
          path="/profile"
          element={
            <Layout>
              <Profile />
            </Layout>
          }
        />

        <Route
          path="/applications"
          element={
            <Layout>
              <Applications />
            </Layout>
          }
        />

        <Route path="/logout" element={<Logout />} />

      </Routes>

    </BrowserRouter>
  )
}

export default App