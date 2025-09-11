import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

interface FormErrors {
  email?: string;
  password?: string;
}

export default function SignIn() {
  const navigate = useNavigate();
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [serverError, setServerError] = useState<string | null>(null);

  function validate(): boolean {
    const e: FormErrors = {};
    if (!email.trim()) e.email = "Email is required";
    else if (!/^\S+@\S+\.\S+$/.test(email)) e.email = "Enter a valid email";
    if (!password.trim()) e.password = "Password is required";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(ev: React.FormEvent<HTMLFormElement>) {
    ev.preventDefault();
    setServerError(null);
    if (!validate()) return;
    setLoading(true);
    try {
      // Simulate API call - replace with your real API
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay
      
      // For demo purposes, accept any email/password combination
      // In real implementation, this would be your actual API call:
      // const res = await fetch("/api/auth/signin", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({ email, password }),
      // });
      // if (!res.ok) {
      //   const body = await res.json().catch(() => ({}));
      //   throw new Error(body?.message || "Sign in failed");
      // }
      
      // Store user session (in real app, this would come from API response)
      localStorage.setItem("user", JSON.stringify({ email, name: "Demo User" }));
      
      // Navigate to dashboard
      navigate("/dashboard");
    } catch (err: any) {
      setServerError(err.message || "Sign in failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-8">
      <form 
        onSubmit={handleSubmit}
        className="bg-white text-gray-500 max-w-[340px] w-full mx-4 md:p-6 p-4 py-8 text-left text-sm rounded-lg shadow-[0px_0px_10px_0px] shadow-black/10"
      >
        <h2 className="text-2xl font-bold mb-9 text-center text-gray-800">Sign In</h2>
        
        <div className="flex items-center my-2 border bg-indigo-500/5 border-gray-500/10 rounded gap-1 pl-2">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 8l9 6 9-6" stroke="#6B7280" strokeOpacity=".6" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
            <rect x="3" y="4" width="18" height="16" rx="2" stroke="#6B7280" strokeOpacity=".6" strokeWidth="1.3" />
          </svg>
          <input 
            className="w-full outline-none bg-transparent py-2.5" 
            type="email" 
            placeholder="Email" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required 
          />
        </div>
        {errors.email && <div className="text-red-500 text-xs mb-2">{errors.email}</div>}

        <div className="flex items-center mt-2 mb-2 border bg-indigo-500/5 border-gray-500/10 rounded gap-1 pl-2">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="#6B7280" strokeOpacity=".6" strokeWidth="1.3"/>
            <circle cx="12" cy="16" r="1" fill="#6B7280" fillOpacity=".6"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="#6B7280" strokeOpacity=".6" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <input 
            className="w-full outline-none bg-transparent py-2.5" 
            type={showPassword ? "text" : "password"}
            placeholder="Password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required 
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="text-xs text-gray-400 px-2 hover:text-gray-600"
          >
            {showPassword ? "Hide" : "Show"}
          </button>
        </div>
        {errors.password && <div className="text-red-500 text-xs mb-4">{errors.password}</div>}
        
        <div className="flex items-center justify-between mb-6">
          <label className="flex items-center text-xs">
            <input type="checkbox" className="mr-2 rounded" />
            Remember me
          </label>
          <Link to="/forgot-password" className="text-xs text-blue-500 hover:underline">
            Forgot password?
          </Link>
        </div>
        
        {serverError && <div className="text-red-500 text-sm mb-4 text-center">{serverError}</div>}

        <button 
          type="submit"
          disabled={loading}
          className="w-full mb-3 bg-indigo-500 hover:bg-indigo-600 transition-all active:scale-95 py-2.5 rounded text-white font-medium disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading && (
            <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" className="opacity-30"/>
              <path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="opacity-80"/>
            </svg>
          )}
          {loading ? "Signing in..." : "Sign In"}
        </button>
        
        <p className="text-center mt-4">
          Don't have an account? <Link to="/signup" className="text-blue-500 underline">Sign Up</Link>
        </p>
      </form>
    </div>
  );
}