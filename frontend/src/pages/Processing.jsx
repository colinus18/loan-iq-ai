import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

function Processing() {
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState(0)
  const [document, setDocument] = useState(null)

  const navigate = useNavigate()

  useEffect(() => {
    const savedDocument = localStorage.getItem("uploadedDocument")

    if (savedDocument) {
      setDocument(JSON.parse(savedDocument))
    }
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        const next = prev + 5

        if (next >= 100) {
          clearInterval(interval)
          return 100
        }

        return next
      })
    }, 200)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (progress < 25) {
      setStage(0)
    } else if (progress < 50) {
      setStage(1)
    } else if (progress < 75) {
      setStage(2)
    } else {
      setStage(3)
    }
  }, [progress])

  useEffect(() => {
    if (progress === 100) {
      const timer = setTimeout(() => {
        navigate("/results")
      }, 1000)

      return () => clearTimeout(timer)
    }
  }, [progress, navigate])

  const steps = [
    {
      icon: "📄",
      title: "Document uploaded",
    },
    {
      icon: "🔍",
      title: "OCR text extraction",
    },
    {
      icon: "🧠",
      title: "AI document analysis",
    },
    {
      icon: "📊",
      title: "Generating results",
    },
  ]

  return (
    <div className="relative min-h-screen overflow-hidden text-white">

      {/* Background glows */}
      <div className="pointer-events-none absolute -left-40 top-10 h-96 w-96 rounded-full bg-purple-600/20 blur-3xl" />

      <div className="pointer-events-none absolute -right-40 bottom-0 h-96 w-96 rounded-full bg-violet-500/10 blur-3xl" />

      <div className="relative mx-auto max-w-4xl px-6 py-10">

        {/* Header */}
        <div className="mb-10">
          <div className="mb-3 flex items-center gap-3">

            <div className="h-10 w-1 rounded-full bg-purple-400" />

            <div>
              <p className="text-sm font-medium uppercase tracking-[0.2em] text-purple-300">
                LoanLens AI
              </p>

              <h1 className="text-3xl font-bold tracking-tight text-white">
                AI Document Processing
              </h1>
            </div>

          </div>

          <p className="max-w-2xl text-sm leading-6 text-slate-400">
            LoanLens is analyzing your document using OCR and AI.
            Please wait while we process your application.
          </p>
        </div>

        {/* Main glass card */}
        <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.06] p-8 shadow-2xl shadow-purple-950/20 backdrop-blur-xl md:p-10">

          {/* Card glow */}
          <div className="pointer-events-none absolute left-1/2 top-0 h-64 w-64 -translate-x-1/2 rounded-full bg-purple-500/10 blur-3xl" />

          <div className="relative">

            {/* AI Processing Visual */}
            <div className="mb-8 flex justify-center">

              <div className="relative">

                {/* Outer glow */}
                <div className="absolute inset-0 animate-pulse rounded-full bg-purple-500/20 blur-xl" />

                {/* Circle */}
                <div className="relative flex h-28 w-28 items-center justify-center rounded-full border border-purple-400/30 bg-purple-500/10 shadow-lg shadow-purple-900/30">

                  <div className="flex h-20 w-20 items-center justify-center rounded-full border border-purple-300/20 bg-purple-500/10">

                    <span className="text-4xl">
                      🤖
                    </span>

                  </div>

                </div>

              </div>

            </div>

            {/* Status */}
            <div className="text-center">

              <h2 className="text-2xl font-semibold text-white">
                {progress === 100
                  ? "Processing Complete!"
                  : "Processing Document"}
              </h2>

              <p className="mt-2 text-sm text-slate-400">
                {progress === 100
                  ? "Preparing your results..."
                  : "OCR and AI analysis are currently in progress..."}
              </p>

            </div>

            {/* Uploaded document */}
            {document && (
              <div className="mt-8 flex items-center gap-4 rounded-2xl border border-white/10 bg-black/10 p-5">

                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-purple-500/10">
                  <span className="text-xl">
                    📎
                  </span>
                </div>

                <div className="min-w-0 flex-1">

                  <p className="text-xs font-medium uppercase tracking-wider text-purple-300">
                    Processing document
                  </p>

                  <p className="mt-1 truncate font-medium text-white">
                    {document.name}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    {(document.size / 1024 / 1024).toFixed(2)} MB
                  </p>

                </div>

                <div className="text-sm text-purple-300">
                  {progress}%
                </div>

              </div>
            )}

            {/* Progress */}
            <div className="mt-8">

              <div className="mb-3 flex items-center justify-between">

                <span className="text-sm font-medium text-slate-300">
                  Processing progress
                </span>

                <span className="text-sm font-semibold text-purple-300">
                  {progress}%
                </span>

              </div>

              <div className="h-3 overflow-hidden rounded-full bg-white/10">

                <div
                  className="h-full rounded-full bg-gradient-to-r from-purple-600 to-violet-400 transition-all duration-200 shadow-lg shadow-purple-500/30"
                  style={{ width: `${progress}%` }}
                />

              </div>

            </div>

            {/* Processing Steps */}
            <div className="mt-10">

              <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">
                Processing stages
              </h3>

              <div className="space-y-3">

                {steps.map((step, index) => {

                  const completed = index < stage
                  const active = index === stage

                  return (
                    <div
                      key={step.title}
                      className={`flex items-center gap-4 rounded-2xl border p-4 transition-all duration-300 ${
                        active
                          ? "border-purple-400/30 bg-purple-500/[0.10] shadow-lg shadow-purple-950/20"
                          : completed
                          ? "border-emerald-400/10 bg-emerald-500/[0.05]"
                          : "border-white/5 bg-white/[0.025]"
                      }`}
                    >

                      {/* Icon */}
                      <div
                        className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${
                          active
                            ? "bg-purple-500/20"
                            : completed
                            ? "bg-emerald-500/10"
                            : "bg-white/5"
                        }`}
                      >
                        <span className="text-xl">
                          {step.icon}
                        </span>
                      </div>

                      {/* Text */}
                      <div className="flex-1">

                        <p
                          className={`font-medium ${
                            active || completed
                              ? "text-white"
                              : "text-slate-500"
                          }`}
                        >
                          {step.title}
                        </p>

                        {completed && (
                          <p className="mt-1 text-xs text-emerald-400">
                            ✓ Completed
                          </p>
                        )}

                        {active && !completed && (
                          <p className="mt-1 text-xs text-purple-300">
                            ⏳ Processing...
                          </p>
                        )}

                        {!completed && !active && (
                          <p className="mt-1 text-xs text-slate-600">
                            Waiting...
                          </p>
                        )}

                      </div>

                      {/* Status indicator */}
                      <div>

                        {completed && (
                          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-500/10 text-sm text-emerald-400">
                            ✓
                          </div>
                        )}

                        {active && !completed && (
                          <div className="h-3 w-3 animate-pulse rounded-full bg-purple-400 shadow-lg shadow-purple-400/50" />
                        )}

                      </div>

                    </div>
                  )
                })}

              </div>

            </div>

            {/* AI Analysis Information */}
            <div className="mt-8 rounded-2xl border border-purple-400/10 bg-purple-500/[0.05] p-5">

              <div className="flex items-start gap-4">

                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-purple-500/10">
                  <span className="text-xl">
                    🧠
                  </span>
                </div>

                <div>

                  <h3 className="font-semibold text-white">
                    LoanLens AI Analysis
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    The system is extracting information from your
                    document, identifying important fields, and
                    preparing an automated loan document analysis.
                  </p>

                </div>

              </div>

            </div>

          </div>
        </div>

        {/* Bottom status */}
        <div className="mt-6 flex items-center justify-center gap-2 text-xs text-slate-500">
          <span className="h-2 w-2 animate-pulse rounded-full bg-purple-400" />
          LoanLens AI processing engine is running
        </div>

      </div>
    </div>
  )
}

export default Processing