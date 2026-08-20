import { useNavigate } from "react-router-dom"

function Logout() {
  const navigate = useNavigate()

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#0d0d10] px-6">

      {/* Background Glow */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-purple-600/20 blur-3xl" />

      {/* Decorative Orbits */}
      <div className="pointer-events-none absolute left-[-180px] top-[15%] h-[450px] w-[900px] rotate-[20deg] rounded-[50%] border border-white/[0.06]" />

      <div className="pointer-events-none absolute right-[-200px] top-[-100px] h-[350px] w-[700px] -rotate-[30deg] rounded-[50%] border border-white/[0.06]" />

      {/* Logout Card */}
      <div className="relative z-10 w-full max-w-md rounded-3xl border border-white/10 bg-white/[0.05] p-10 text-center shadow-2xl shadow-purple-950/30 backdrop-blur-xl">

        {/* Logo */}
        <div className="mb-6 flex justify-center">

          <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-purple-400/20 bg-purple-500/10 text-3xl text-purple-300 shadow-lg shadow-purple-950/30">
            ✦
          </div>

        </div>

        {/* Brand */}
        <p className="mb-6 text-sm font-semibold tracking-wide text-purple-300">
          Loan<span className="text-white">Lens</span>
        </p>

        {/* Status Icon */}
        <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-full border border-emerald-400/20 bg-emerald-500/10 text-2xl text-emerald-400">
          ✓
        </div>

        <h1 className="text-3xl font-bold text-white">
          Logged Out
        </h1>

        <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-slate-400">
          You have been successfully logged out of your LoanLens
          workspace.
        </p>

        {/* Button */}
        <button
          onClick={() => navigate("/")}
          className="mt-8 w-full rounded-xl bg-gradient-to-r from-purple-600 to-violet-500 px-6 py-3.5 font-semibold text-white shadow-lg shadow-purple-900/30 transition-all duration-300 hover:-translate-y-0.5 hover:from-purple-500 hover:to-violet-400"
        >
          Back to Login
          <span className="ml-2">→</span>
        </button>

        {/* Footer */}
        <p className="mt-6 text-xs text-slate-600">
          LoanLens AI · Intelligent Loan Document Processing
        </p>

      </div>

    </div>
  )
}

export default Logout