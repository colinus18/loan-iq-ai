import { useNavigate } from "react-router-dom"

function Applications() {
  const navigate = useNavigate()

  return (
    <div className="relative min-h-screen overflow-hidden text-white">

      {/* Background glows */}
      <div className="pointer-events-none absolute -left-40 top-20 h-96 w-96 rounded-full bg-purple-600/20 blur-3xl" />

      <div className="pointer-events-none absolute -right-40 bottom-20 h-96 w-96 rounded-full bg-violet-500/10 blur-3xl" />

      <div className="relative mx-auto max-w-6xl px-6 py-10">

        {/* Header */}
        <div className="mb-8">
          <div className="mb-3 flex items-center gap-3">

            <div className="h-10 w-1 rounded-full bg-purple-400" />

            <div>
              <p className="text-sm font-medium uppercase tracking-[0.2em] text-purple-300">
                LoanLens AI
              </p>

              <h1 className="text-3xl font-bold tracking-tight text-white">
                Applications
              </h1>
            </div>

          </div>

          <p className="text-sm leading-6 text-slate-400">
            View and manage loan document applications processed by
            LoanLens.
          </p>
        </div>

        {/* Stats */}
        <div className="mb-6 grid gap-4 sm:grid-cols-3">

          <div className="rounded-2xl border border-emerald-400/10 bg-emerald-500/[0.05] p-5 backdrop-blur-xl">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Approved
            </p>

            <p className="mt-2 text-2xl font-bold text-emerald-400">
              1
            </p>
          </div>

          <div className="rounded-2xl border border-yellow-400/10 bg-yellow-500/[0.05] p-5 backdrop-blur-xl">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Pending
            </p>

            <p className="mt-2 text-2xl font-bold text-yellow-400">
              1
            </p>
          </div>

          <div className="rounded-2xl border border-red-400/10 bg-red-500/[0.05] p-5 backdrop-blur-xl">
            <p className="text-xs uppercase tracking-wider text-slate-500">
              Rejected
            </p>

            <p className="mt-2 text-2xl font-bold text-red-400">
              1
            </p>
          </div>

        </div>

        {/* Applications Table */}
        <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.05] shadow-2xl shadow-purple-950/20 backdrop-blur-xl">

          <div className="border-b border-white/10 px-6 py-5">
            <h2 className="font-semibold text-white">
              Recent Applications
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Loan applications and their current processing status.
            </p>
          </div>

          {/* Desktop table */}
          <div className="hidden overflow-x-auto md:block">

            <table className="w-full">

              <thead className="border-b border-white/10 bg-white/[0.03]">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                    Applicant
                  </th>

                  <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                    Document
                  </th>

                  <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                    Status
                  </th>

                  <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                    Action
                  </th>
                </tr>
              </thead>

              <tbody>

                {/* John */}
                <tr className="border-b border-white/5 transition hover:bg-white/[0.03]">

                  <td className="px-6 py-5">
                    <div className="flex items-center gap-3">

                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 font-semibold text-purple-300">
                        JD
                      </div>

                      <div>
                        <p className="font-medium text-white">
                          John Doe
                        </p>

                        <p className="text-xs text-slate-500">
                          Primary Applicant
                        </p>
                      </div>

                    </div>
                  </td>

                  <td className="px-6 py-5">
                    <p className="text-sm text-slate-300">
                      📄 Loan_Application.pdf
                    </p>
                  </td>

                  <td className="px-6 py-5">
                    <span className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400">
                      <span>✓</span>
                      Approved
                    </span>
                  </td>

                  <td className="px-6 py-5">
                    <button
                      onClick={() => navigate("/results")}
                      className="rounded-xl border border-purple-400/20 bg-purple-500/10 px-4 py-2 text-sm font-medium text-purple-300 transition hover:bg-purple-500/20 hover:text-white"
                    >
                      View Results →
                    </button>
                  </td>

                </tr>

                {/* Jane */}
                <tr className="border-b border-white/5 transition hover:bg-white/[0.03]">

                  <td className="px-6 py-5">
                    <div className="flex items-center gap-3">

                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 font-semibold text-purple-300">
                        JS
                      </div>

                      <div>
                        <p className="font-medium text-white">
                          Jane Smith
                        </p>

                        <p className="text-xs text-slate-500">
                          Applicant
                        </p>
                      </div>

                    </div>
                  </td>

                  <td className="px-6 py-5">
                    <p className="text-sm text-slate-300">
                      📄 Income_Proof.pdf
                    </p>
                  </td>

                  <td className="px-6 py-5">
                    <span className="inline-flex items-center gap-2 rounded-full border border-yellow-400/20 bg-yellow-500/10 px-3 py-1 text-xs font-medium text-yellow-400">
                      <span>●</span>
                      Pending
                    </span>
                  </td>

                  <td className="px-6 py-5">
                    <button
                      onClick={() => navigate("/results")}
                      className="rounded-xl border border-purple-400/20 bg-purple-500/10 px-4 py-2 text-sm font-medium text-purple-300 transition hover:bg-purple-500/20 hover:text-white"
                    >
                      View Results →
                    </button>
                  </td>

                </tr>

                {/* Alex */}
                <tr className="transition hover:bg-white/[0.03]">

                  <td className="px-6 py-5">
                    <div className="flex items-center gap-3">

                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 font-semibold text-purple-300">
                        AJ
                      </div>

                      <div>
                        <p className="font-medium text-white">
                          Alex Johnson
                        </p>

                        <p className="text-xs text-slate-500">
                          Applicant
                        </p>
                      </div>

                    </div>
                  </td>

                  <td className="px-6 py-5">
                    <p className="text-sm text-slate-300">
                      📄 Passport.pdf
                    </p>
                  </td>

                  <td className="px-6 py-5">
                    <span className="inline-flex items-center gap-2 rounded-full border border-red-400/20 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-400">
                      <span>✕</span>
                      Rejected
                    </span>
                  </td>

                  <td className="px-6 py-5">
                    <button
                      onClick={() => navigate("/results")}
                      className="rounded-xl border border-purple-400/20 bg-purple-500/10 px-4 py-2 text-sm font-medium text-purple-300 transition hover:bg-purple-500/20 hover:text-white"
                    >
                      View Results →
                    </button>
                  </td>

                </tr>

              </tbody>

            </table>

          </div>

          {/* Mobile cards */}
          <div className="space-y-3 p-4 md:hidden">

            {[
              {
                initials: "JD",
                name: "John Doe",
                document: "Loan_Application.pdf",
                status: "Approved",
                statusClass:
                  "border-emerald-400/20 bg-emerald-500/10 text-emerald-400",
              },
              {
                initials: "JS",
                name: "Jane Smith",
                document: "Income_Proof.pdf",
                status: "Pending",
                statusClass:
                  "border-yellow-400/20 bg-yellow-500/10 text-yellow-400",
              },
              {
                initials: "AJ",
                name: "Alex Johnson",
                document: "Passport.pdf",
                status: "Rejected",
                statusClass:
                  "border-red-400/20 bg-red-500/10 text-red-400",
              },
            ].map((app) => (
              <div
                key={app.name}
                className="rounded-2xl border border-white/5 bg-black/10 p-4"
              >

                <div className="flex items-center gap-3">

                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 font-semibold text-purple-300">
                    {app.initials}
                  </div>

                  <div className="flex-1">
                    <p className="font-medium text-white">
                      {app.name}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      📄 {app.document}
                    </p>
                  </div>

                  <span
                    className={`rounded-full border px-3 py-1 text-xs ${app.statusClass}`}
                  >
                    {app.status}
                  </span>

                </div>

                <button
                  onClick={() => navigate("/results")}
                  className="mt-4 w-full rounded-xl bg-purple-500/10 px-4 py-2 text-sm font-medium text-purple-300 hover:bg-purple-500/20"
                >
                  View Results →
                </button>

              </div>
            ))}

          </div>

        </div>

      </div>
    </div>
  )
}

export default Applications