function History() {
  const applications = [
    {
      id: 1,
      applicant: "John Doe",
      document: "Loan_Application.pdf",
      status: "Approved",
    },
    {
      id: 2,
      applicant: "Jane Smith",
      document: "Income_Proof.pdf",
      status: "Pending",
    },
    {
      id: 3,
      applicant: "Alex Johnson",
      document: "Passport.pdf",
      status: "Rejected",
    },
  ]

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
                Application History
              </h1>

            </div>

          </div>

          <p className="text-sm leading-6 text-slate-400">
            Review previously processed loan documents and their
            verification status.
          </p>

        </div>

        {/* History Card */}
        <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.05] shadow-2xl shadow-purple-950/20 backdrop-blur-xl">

          {/* Card Header */}
          <div className="border-b border-white/10 px-6 py-5">

            <div className="flex items-center justify-between">

              <div>

                <h2 className="font-semibold text-white">
                  Processing History
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  {applications.length} applications recorded
                </p>

              </div>

              <div className="hidden h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 sm:flex">
                📋
              </div>

            </div>

          </div>

          {/* Desktop Table */}
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

                </tr>

              </thead>

              <tbody>

                {applications.map((app) => (

                  <tr
                    key={app.id}
                    className="border-b border-white/5 transition hover:bg-white/[0.03]"
                  >

                    <td className="px-6 py-5">

                      <div className="flex items-center gap-3">

                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 font-semibold text-purple-300">
                          {app.applicant
                            .split(" ")
                            .map((name) => name[0])
                            .join("")}
                        </div>

                        <div>

                          <p className="font-medium text-white">
                            {app.applicant}
                          </p>

                          <p className="text-xs text-slate-500">
                            Application #{app.id}
                          </p>

                        </div>

                      </div>

                    </td>

                    <td className="px-6 py-5">

                      <div className="flex items-center gap-3">

                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/5">
                          📄
                        </div>

                        <span className="text-sm text-slate-300">
                          {app.document}
                        </span>

                      </div>

                    </td>

                    <td className="px-6 py-5">

                      <span
                        className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium ${
                          app.status === "Approved"
                            ? "border-emerald-400/20 bg-emerald-500/10 text-emerald-400"
                            : app.status === "Pending"
                            ? "border-yellow-400/20 bg-yellow-500/10 text-yellow-400"
                            : "border-red-400/20 bg-red-500/10 text-red-400"
                        }`}
                      >

                        <span>
                          {app.status === "Approved"
                            ? "✓"
                            : app.status === "Pending"
                            ? "●"
                            : "✕"}
                        </span>

                        {app.status}

                      </span>

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

          {/* Mobile Cards */}
          <div className="space-y-3 p-4 md:hidden">

            {applications.map((app) => (

              <div
                key={app.id}
                className="rounded-2xl border border-white/5 bg-black/10 p-4"
              >

                <div className="flex items-center gap-3">

                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-purple-500/10 font-semibold text-purple-300">
                    {app.applicant
                      .split(" ")
                      .map((name) => name[0])
                      .join("")}
                  </div>

                  <div className="min-w-0 flex-1">

                    <p className="font-medium text-white">
                      {app.applicant}
                    </p>

                    <p className="mt-1 truncate text-xs text-slate-500">
                      📄 {app.document}
                    </p>

                  </div>

                  <span
                    className={`rounded-full border px-3 py-1 text-xs ${
                      app.status === "Approved"
                        ? "border-emerald-400/20 bg-emerald-500/10 text-emerald-400"
                        : app.status === "Pending"
                        ? "border-yellow-400/20 bg-yellow-500/10 text-yellow-400"
                        : "border-red-400/20 bg-red-500/10 text-red-400"
                    }`}
                  >
                    {app.status}
                  </span>

                </div>

              </div>

            ))}

          </div>

        </div>

      </div>
    </div>
  )
}

export default History