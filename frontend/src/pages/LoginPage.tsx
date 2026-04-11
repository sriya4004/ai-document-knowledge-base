import { useState } from "react";
import toast from "react-hot-toast";
import { useLocation, useNavigate } from "react-router-dom";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsLoading(true);
    try {
      await login(email, password);
      toast.success("Logged in successfully");
      const nextPath = (location.state as { from?: { pathname?: string } } | null)?.from
        ?.pathname;
      navigate(nextPath || "/", { replace: true });
    } catch {
      toast.error("Login failed. Check your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="mx-auto flex min-h-screen max-w-6xl items-center justify-center px-4">
      <div className="grid w-full overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xl md:grid-cols-2">
        <div className="hidden bg-gradient-to-br from-brand-600 to-brand-700 p-8 text-white md:block">
          <h2 className="text-2xl font-semibold">AI-Powered Document Knowledge Base</h2>
          <p className="mt-3 text-sm text-indigo-100">
            Securely search company documents with role and department-aware semantic retrieval.
          </p>
        </div>
        <div className="p-8 md:p-10">
          <h3 className="text-2xl font-semibold text-slate-800">Sign in</h3>
          <p className="mt-1 text-sm text-slate-500">Use your employee credentials to continue.</p>
          <form onSubmit={handleSubmit} method="POST" className="mt-6 space-y-4">
            <Input
              type="email"
              name="username"
              label="Email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
              required
            />
            <Input
              type="password"
              name="password"
              label="Password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
            <Button isLoading={isLoading} className="w-full" type="submit">
              {isLoading ? "Signing in..." : "Sign in"}
            </Button>
          </form>
        </div>
      </div>
    </section>
  );
}
