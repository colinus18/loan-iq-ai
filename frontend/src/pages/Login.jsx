import { useState } from "react"
import { useNavigate } from "react-router-dom"

function Login() {
    const navigate = useNavigate()

    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")

    const handleLogin = (e) => {
        e.preventDefault()
        setError("")

        // Gmail validation
        const gmailRegex = /^[a-zA-Z0-9._%+-]+@gmail\.com$/

        if (!gmailRegex.test(email)) {
            setError("Please enter a valid Gmail address ending with @gmail.com.")
            return
        }

        // Strong password validation
        const strongPassword =
            /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/

        if (!strongPassword.test(password)) {
            setError(
                "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character."
            )
            return
        }

        // Everything is valid
        navigate("/dashboard")
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-950 px-4">

            <div className="w-full max-w-md">

                {/* Logo / Heading */}
                <div className="mb-8 text-center">
                    <h1 className="text-4xl font-bold text-white">
                        Loan IQ
                    </h1>

                    <p className="mt-2 text-slate-400">
                        Intelligent Loan Document Processing
                    </p>
                </div>

                {/* Login Card */}
                <div className="rounded-2xl bg-white p-8 shadow-xl">

                    <h2 className="text-2xl font-semibold text-slate-900">
                        Welcome back
                    </h2>

                    <p className="mt-1 text-sm text-slate-500">
                        Sign in to continue to your dashboard.
                    </p>

                    <form onSubmit={handleLogin} className="mt-6 space-y-5">

                        {/* Email */}
                        <div>
                            <label className="block text-sm font-medium text-slate-700">
                                Email
                            </label>

                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="you@gmail.com"
                                className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-slate-900 placeholder-slate-400 outline-none transition focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                                required
                            />
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-medium text-slate-700">
                                Password
                            </label>

                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Enter your password"
                                className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-slate-900 placeholder-slate-400 outline-none transition focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                                required
                            />

                            
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
                                {error}
                            </div>
                        )}

                        {/* Sign In */}
                        <button
                            type="submit"
                            className="w-full rounded-lg bg-slate-900 py-3 font-medium text-white transition hover:bg-purple-700"
                        >
                            Sign In
                        </button>

                    </form>

                </div>

            </div>

        </div>
    )
}

export default Login