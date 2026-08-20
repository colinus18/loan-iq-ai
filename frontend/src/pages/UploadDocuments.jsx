import { useState } from "react"
import { useNavigate } from "react-router-dom"

function Upload() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [message, setMessage] = useState("")
  const navigate = useNavigate()

  const handleFileChange = (e) => {
    const file = e.target.files[0]

    if (!file) {
      return
    }

    const allowedExtensions = ["pdf", "jpg", "jpeg", "png"]

    const fileExtension = file.name
      .split(".")
      .pop()
      .toLowerCase()

    if (!allowedExtensions.includes(fileExtension)) {
      setMessage("Please upload a PDF, JPG, or PNG file.")
      setSelectedFile(null)

      e.target.value = ""

      return
    }

    setSelectedFile(file)
    setMessage("")
  }

  const handleUpload = () => {
    if (!selectedFile) {
      setMessage("Please select a file first.")
      return
    }

    const documentData = {
      name: selectedFile.name,
      size: selectedFile.size,
      type: selectedFile.type,
    }

    localStorage.setItem(
      "uploadedDocument",
      JSON.stringify(documentData)
    )

    navigate("/processing")
  }

  return (
    <div className="relative min-h-screen overflow-hidden text-white">

      {/* Decorative purple glow */}
      <div className="pointer-events-none absolute -left-32 top-20 h-80 w-80 rounded-full bg-purple-600/20 blur-3xl" />
      <div className="pointer-events-none absolute -right-32 bottom-10 h-96 w-96 rounded-full bg-violet-500/10 blur-3xl" />

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
                Upload Documents
              </h1>
            </div>
          </div>

          <p className="max-w-2xl text-sm leading-6 text-slate-400">
            Upload your loan documents and let LoanLens use OCR and AI
            analysis to extract and verify important information.
          </p>
        </div>

        {/* Message */}
        {message && (
          <div className="mb-6 rounded-xl border border-red-400/20 bg-red-500/10 px-5 py-4 text-sm text-red-300 backdrop-blur-md">
            {message}
          </div>
        )}

        {/* Main Upload Card */}
        <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.06] p-8 shadow-2xl shadow-purple-950/20 backdrop-blur-xl md:p-10">

          {/* Card glow */}
          <div className="pointer-events-none absolute -right-20 -top-20 h-56 w-56 rounded-full bg-purple-500/10 blur-3xl" />

          <div className="relative">

            {/* Upload heading */}
            <div className="mb-8 text-center">

              <div className="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-2xl border border-purple-400/20 bg-purple-500/10 shadow-lg shadow-purple-900/20">
                <span className="text-4xl">📄</span>
              </div>

              <h2 className="text-2xl font-semibold text-white">
                Upload a loan document
              </h2>

              <p className="mt-2 text-sm text-slate-400">
                Choose a document to begin AI-powered processing
              </p>
            </div>

            {/* Drag/drop style area */}
            <label
              htmlFor="document-upload"
              className="group block cursor-pointer rounded-2xl border border-dashed border-purple-400/30 bg-purple-500/[0.04] p-10 text-center transition-all duration-300 hover:border-purple-400/60 hover:bg-purple-500/[0.08]"
            >
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-purple-500/10 transition group-hover:scale-105">
                <span className="text-2xl">⬆️</span>
              </div>

              <p className="font-medium text-white">
                Click to choose your document
              </p>

              <p className="mt-2 text-sm text-slate-500">
                PDF, JPG or PNG
              </p>

              <input
                id="document-upload"
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                className="hidden"
                onChange={handleFileChange}
              />
            </label>

            {/* Selected file */}
            {selectedFile && (
              <div className="mt-6 flex items-center gap-4 rounded-2xl border border-emerald-400/20 bg-emerald-500/[0.06] p-5">

                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-emerald-500/10">
                  <span className="text-xl">📎</span>
                </div>

                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium uppercase tracking-wider text-emerald-400">
                    Selected document
                  </p>

                  <p className="mt-1 truncate font-medium text-white">
                    {selectedFile.name}
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>

                <span className="text-lg text-emerald-400">
                  ✓
                </span>
              </div>
            )}

            {/* Upload button */}
            <button
              onClick={handleUpload}
              className="mt-7 w-full rounded-xl bg-gradient-to-r from-purple-600 to-violet-500 px-6 py-4 font-semibold text-white shadow-lg shadow-purple-900/30 transition-all duration-300 hover:-translate-y-0.5 hover:from-purple-500 hover:to-violet-400 hover:shadow-purple-500/20"
            >
              Upload & Start Processing
            </button>

          </div>
        </div>

        {/* What happens next */}
        <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur-md">

          <div className="flex items-start gap-4">

            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-purple-500/10">
              <span className="text-xl">🤖</span>
            </div>

            <div>
              <h3 className="font-semibold text-white">
                What happens next?
              </h3>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                LoanLens will extract text using OCR, analyze the
                document using AI, identify important loan information,
                and prepare your results automatically.
              </p>
            </div>

          </div>
        </div>

        {/* Supported formats */}
        <div className="mt-5 flex items-center justify-center gap-3 text-xs text-slate-500">
          <span>Secure document processing</span>
          <span>•</span>
          <span>PDF</span>
          <span>•</span>
          <span>JPG</span>
          <span>•</span>
          <span>PNG</span>
        </div>

      </div>
    </div>
  )
}

export default Upload