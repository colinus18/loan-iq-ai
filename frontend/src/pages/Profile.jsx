import { useState } from "react"

function Profile() {
  const [profile, setProfile] = useState({
    name: "John Doe",
    email: "john@example.com",
    role: "Loan Officer",
  })

  const [isEditing, setIsEditing] = useState(false)

  return (
    <div className="relative min-h-screen overflow-hidden text-white">

      {/* Background glows */}
      <div className="pointer-events-none absolute -left-40 top-20 h-96 w-96 rounded-full bg-purple-600/20 blur-3xl" />

      <div className="pointer-events-none absolute -right-40 bottom-20 h-96 w-96 rounded-full bg-violet-500/10 blur-3xl" />

      <div className="relative mx-auto max-w-4xl px-6 py-10">

        {/* Header */}
        <div className="mb-8">

          <div className="mb-3 flex items-center gap-3">

            <div className="h-10 w-1 rounded-full bg-purple-400" />

            <div>

              <p className="text-sm font-medium uppercase tracking-[0.2em] text-purple-300">
                LoanLens AI
              </p>

              <h1 className="text-3xl font-bold tracking-tight text-white">
                Profile
              </h1>

            </div>

          </div>

          <p className="text-sm leading-6 text-slate-400">
            Manage your LoanLens account information and profile details.
          </p>

        </div>

        {/* Profile Card */}
        <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.05] shadow-2xl shadow-purple-950/20 backdrop-blur-xl">

          {/* Profile Header */}
          <div className="border-b border-white/10 bg-purple-500/[0.03] p-8">

            <div className="flex flex-col items-center gap-5 sm:flex-row">

              {/* Avatar */}
              <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-3xl border border-purple-400/20 bg-gradient-to-br from-purple-600/30 to-violet-500/10 text-3xl font-bold text-purple-200 shadow-lg shadow-purple-950/30">
                JD
              </div>

              <div className="text-center sm:text-left">

                <p className="text-xs font-medium uppercase tracking-[0.2em] text-purple-300">
                  LoanLens User
                </p>

                <h2 className="mt-1 text-2xl font-bold text-white">
                  {profile.name}
                </h2>

                <p className="mt-1 text-sm text-slate-400">
                  {profile.role}
                </p>

              </div>

            </div>

          </div>

          {/* Profile Details */}
          <div className="p-8">

            <div className="mb-7 flex items-center justify-between">

              <div>

                <h3 className="text-lg font-semibold text-white">
                  Account Information
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  Your personal and professional details
                </p>

              </div>

              <div className="hidden rounded-full border border-emerald-400/20 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400 sm:block">
                ● Active
              </div>

            </div>

            {/* Full Name */}
            <div className="mb-6">

              <label className="mb-2 block text-sm font-medium text-slate-400">
                Full Name
              </label>

              <input
                type="text"
                value={profile.name}
                readOnly={!isEditing}
                onChange={(e) =>
                  setProfile({
                    ...profile,
                    name: e.target.value,
                  })
                }
                className={`w-full rounded-xl border px-4 py-3 text-sm text-white outline-none transition ${
                  isEditing
                    ? "border-purple-400/30 bg-purple-500/[0.06] focus:border-purple-400/60 focus:ring-2 focus:ring-purple-500/10"
                    : "border-white/5 bg-white/[0.03] cursor-default"
                }`}
              />

            </div>

            {/* Email */}
            <div className="mb-6">

              <label className="mb-2 block text-sm font-medium text-slate-400">
                Email Address
              </label>

              <input
                type="email"
                value={profile.email}
                readOnly={!isEditing}
                onChange={(e) =>
                  setProfile({
                    ...profile,
                    email: e.target.value,
                  })
                }
                className={`w-full rounded-xl border px-4 py-3 text-sm text-white outline-none transition ${
                  isEditing
                    ? "border-purple-400/30 bg-purple-500/[0.06] focus:border-purple-400/60 focus:ring-2 focus:ring-purple-500/10"
                    : "border-white/5 bg-white/[0.03] cursor-default"
                }`}
              />

            </div>

            {/* Role */}
            <div className="mb-8">

              <label className="mb-2 block text-sm font-medium text-slate-400">
                Role
              </label>

              <input
                type="text"
                value={profile.role}
                readOnly={!isEditing}
                onChange={(e) =>
                  setProfile({
                    ...profile,
                    role: e.target.value,
                  })
                }
                className={`w-full rounded-xl border px-4 py-3 text-sm text-white outline-none transition ${
                  isEditing
                    ? "border-purple-400/30 bg-purple-500/[0.06] focus:border-purple-400/60 focus:ring-2 focus:ring-purple-500/10"
                    : "border-white/5 bg-white/[0.03] cursor-default"
                }`}
              />

            </div>

            {/* Button */}
            <button
              onClick={() => setIsEditing(!isEditing)}
              className={`w-full rounded-xl px-6 py-4 font-semibold transition-all duration-300 ${
                isEditing
                  ? "bg-gradient-to-r from-emerald-600 to-green-500 text-white shadow-lg shadow-emerald-900/20 hover:-translate-y-0.5 hover:from-emerald-500 hover:to-green-400"
                  : "bg-gradient-to-r from-purple-600 to-violet-500 text-white shadow-lg shadow-purple-900/30 hover:-translate-y-0.5 hover:from-purple-500 hover:to-violet-400"
              }`}
            >
              {isEditing ? "✓ Save Profile" : "✎ Edit Profile"}
            </button>

          </div>

        </div>

        {/* Security / Account Info */}
        <div className="mt-6 grid gap-4 sm:grid-cols-2">

          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 backdrop-blur-md">

            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10">
              🔐
            </div>

            <h3 className="font-semibold text-white">
              Account Security
            </h3>

            <p className="mt-1 text-sm leading-6 text-slate-500">
              Your account information is protected within the
              LoanLens platform.
            </p>

          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 backdrop-blur-md">

            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10">
              🤖
            </div>

            <h3 className="font-semibold text-white">
              LoanLens AI
            </h3>

            <p className="mt-1 text-sm leading-6 text-slate-500">
              AI-powered document processing and loan analysis
              at your fingertips.
            </p>

          </div>

        </div>

      </div>
    </div>
  )
}

export default Profile