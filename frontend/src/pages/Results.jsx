import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

function Results() {
  const navigate = useNavigate()

  const [document, setDocument] = useState(null)

  useEffect(() => {
    const savedDocument = localStorage.getItem("uploadedDocument")

    if (savedDocument) {
      setDocument(JSON.parse(savedDocument))
    }
  }, [])

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
                Document Analysis Results
              </h1>
            </div>

          </div>

          <p className="max-w-2xl text-sm leading-6 text-slate-400">
            AI-powered analysis and verification results for your uploaded
            loan document.
          </p>
        </div>

        {/* Verification Status */}
        <div className="mb-6 overflow-hidden rounded-3xl border border-emerald-400/20 bg-emerald-500/[0.06] p-6 backdrop-blur-xl">

          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">

            <div className="flex items-center gap-4">

              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-emerald-500/10 text-2xl text-emerald-400">
                ✓
              </div>

              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-emerald-400">
                  Verification Status
                </p>

                <h2 className="mt-1 text-2xl font-bold text-white">
                  Document Verified
                </h2>

                <p className="mt-1 text-sm text-slate-400">
                  All required information was detected successfully.
                </p>
              </div>

            </div>

            {/* Confidence */}
            <div className="rounded-2xl border border-purple-400/10 bg-white/[0.04] px-8 py-4 text-center">

              <p className="text-xs uppercase tracking-wider text-slate-500">
                AI Confidence
              </p>

              <p className="mt-1 text-3xl font-bold text-purple-300">
                94%
              </p>

            </div>

          </div>
        </div>

        {/* Summary Cards */}
        <div className="mb-6 grid gap-5 md:grid-cols-3">

          {/* Applicant */}
          <div className="rounded-2xl border border-white/10 bg-white/[0.05] p-6 backdrop-blur-xl">

            <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
              Applicant
            </p>

            <h3 className="mt-3 text-xl font-semibold text-white">
              John Doe
            </h3>

            <p className="mt-1 text-sm text-slate-400">
              Primary Applicant
            </p>

          </div>

          {/* Loan */}
          <div className="rounded-2xl border border-white/10 bg-white/[0.05] p-6 backdrop-blur-xl">

            <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
              Requested Loan
            </p>

            <h3 className="mt-3 text-xl font-semibold text-white">
              ₹5,00,000
            </h3>

            <p className="mt-1 text-sm text-slate-400">
              Personal Loan
            </p>

          </div>

          {/* Document */}
          <div className="rounded-2xl border border-white/10 bg-white/[0.05] p-6 backdrop-blur-xl">

            <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
              Document
            </p>

            <h3 className="mt-3 break-all text-lg font-semibold text-white">
              {document ? document.name : "No document found"}
            </h3>

            {document && (
              <p className="mt-1 text-sm text-slate-400">
                {(document.size / 1024 / 1024).toFixed(2)} MB
              </p>
            )}

            <p className="mt-2 text-sm text-emerald-400">
              ✓ Successfully processed
            </p>

          </div>

        </div>

        {/* AI Analysis */}
        <div className="mb-6 rounded-3xl border border-white/10 bg-white/[0.05] p-6 backdrop-blur-xl md:p-7">

          <div className="mb-6 flex items-center gap-4">

            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10">
              <span className="text-2xl">
                🤖
              </span>
            </div>

            <div>
              <h2 className="text-xl font-semibold text-white">
                AI Analysis
              </h2>

              <p className="text-sm text-slate-500">
                Automated document assessment
              </p>
            </div>

          </div>

          {/* Analysis text */}
          <div className="rounded-2xl border border-purple-400/10 bg-purple-500/[0.05] p-5">

            <p className="leading-7 text-slate-300">
              The uploaded loan document appears complete and consistent.
              Required applicant information, employment details, income,
              and loan information were successfully extracted. No major
              inconsistencies were detected during automated verification.
            </p>

          </div>

          {/* Confidence */}
          <div className="mt-7">

            <div className="mb-3 flex justify-between">

              <span className="text-sm font-medium text-slate-400">
                AI Confidence Score
              </span>

              <span className="text-sm font-bold text-purple-300">
                94%
              </span>

            </div>

            <div className="h-3 overflow-hidden rounded-full bg-white/10">

              <div
                className="h-full rounded-full bg-gradient-to-r from-purple-600 to-violet-400 shadow-lg shadow-purple-500/20"
                style={{ width: "94%" }}
              />

            </div>

          </div>

        </div>

        {/* Extracted Information */}
        <div className="mb-6 rounded-3xl border border-white/10 bg-white/[0.05] p-6 backdrop-blur-xl md:p-7">

          <div className="mb-6">

            <p className="text-xs font-medium uppercase tracking-wider text-purple-300">
              OCR + AI
            </p>

            <h2 className="mt-1 text-xl font-semibold text-white">
              Extracted Information
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Information identified from the uploaded document
            </p>

          </div>

          <div className="grid gap-4 md:grid-cols-2">

            <div className="rounded-2xl border border-white/5 bg-black/10 p-5">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Applicant Name
              </p>
              <p className="mt-2 font-semibold text-white">
                John Doe
              </p>
            </div>

            <div className="rounded-2xl border border-white/5 bg-black/10 p-5">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Loan Amount
              </p>
              <p className="mt-2 font-semibold text-white">
                ₹5,00,000
              </p>
            </div>

            <div className="rounded-2xl border border-white/5 bg-black/10 p-5">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Employment Status
              </p>
              <p className="mt-2 font-semibold text-white">
                Employed
              </p>
            </div>

            <div className="rounded-2xl border border-white/5 bg-black/10 p-5">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Monthly Income
              </p>
              <p className="mt-2 font-semibold text-white">
                ₹60,000
              </p>
            </div>

            <div className="rounded-2xl border border-white/5 bg-black/10 p-5">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Employment Type
              </p>
              <p className="mt-2 font-semibold text-white">
                Full Time
              </p>
            </div>

            <div className="rounded-2xl border border-white/5 bg-black/10 p-5">
              <p className="text-xs uppercase tracking-wider text-slate-500">
                Document Type
              </p>
              <p className="mt-2 font-semibold text-white">
                Loan Application
              </p>
            </div>

          </div>

        </div>

        {/* Verification Checks */}
        <div className="mb-6 rounded-3xl border border-white/10 bg-white/[0.05] p-6 backdrop-blur-xl md:p-7">

          <div className="mb-6">

            <p className="text-xs font-medium uppercase tracking-wider text-purple-300">
              Verification Engine
            </p>

            <h2 className="mt-1 text-xl font-semibold text-white">
              Document Verification
            </h2>

          </div>

          <div className="space-y-3">

            <div className="flex items-center justify-between rounded-2xl border border-emerald-400/10 bg-emerald-500/[0.05] p-4">
              <span className="text-sm text-slate-300">
                Required fields
              </span>

              <span className="text-sm font-medium text-emerald-400">
                ✓ Complete
              </span>
            </div>

            <div className="flex items-center justify-between rounded-2xl border border-emerald-400/10 bg-emerald-500/[0.05] p-4">
              <span className="text-sm text-slate-300">
                Applicant information
              </span>

              <span className="text-sm font-medium text-emerald-400">
                ✓ Verified
              </span>
            </div>

            <div className="flex items-center justify-between rounded-2xl border border-emerald-400/10 bg-emerald-500/[0.05] p-4">
              <span className="text-sm text-slate-300">
                Income information
              </span>

              <span className="text-sm font-medium text-emerald-400">
                ✓ Detected
              </span>
            </div>

            <div className="flex items-center justify-between rounded-2xl border border-emerald-400/10 bg-emerald-500/[0.05] p-4">
              <span className="text-sm text-slate-300">
                Document consistency
              </span>

              <span className="text-sm font-medium text-emerald-400">
                ✓ Passed
              </span>
            </div>

          </div>

        </div>

        {/* AI Recommendation */}
        <div className="mb-8 overflow-hidden rounded-3xl border border-purple-400/20 bg-gradient-to-br from-purple-900/30 to-violet-900/10 p-6 shadow-2xl shadow-purple-950/20 backdrop-blur-xl md:p-7">

          <div className="flex items-start gap-5">

            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-purple-500/10 text-2xl">
              🧠
            </div>

            <div>

              <p className="text-xs font-medium uppercase tracking-wider text-purple-300">
                AI Recommendation
              </p>

              <h2 className="mt-1 text-xl font-semibold text-white">
                Ready for Further Review
              </h2>

              <p className="mt-3 leading-7 text-slate-300">
                Based on the extracted information and document
                verification checks, the application can proceed to
                the next stage of loan evaluation.
              </p>

              <div className="mt-5 inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-400">
                <span>✓</span>
                <span>Ready for Further Review</span>
              </div>

            </div>

          </div>

        </div>

        {/* Action Buttons */}
        <div className="flex flex-col gap-4 sm:flex-row">

          <button
            onClick={() => navigate("/upload")}
            className="flex-1 rounded-xl bg-gradient-to-r from-purple-600 to-violet-500 px-6 py-4 font-semibold text-white shadow-lg shadow-purple-900/30 transition-all duration-300 hover:-translate-y-0.5 hover:from-purple-500 hover:to-violet-400"
          >
            📄 Process Another Document
          </button>

          <button
            onClick={() => navigate("/dashboard")}
            className="flex-1 rounded-xl border border-white/10 bg-white/[0.05] px-6 py-4 font-medium text-slate-300 backdrop-blur-md transition-all duration-300 hover:bg-white/[0.10] hover:text-white"
          >
            ← Back to Dashboard
          </button>

        </div>

      </div>
    </div>
  )
}

export default Results