import { BarChart3, History, LogOut, Search, Upload } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Button from "./ui/Button";

export default function Layout() {
  const navigate = useNavigate();
  const { logout, user } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const navItemClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-2 rounded-xl px-3 py-2 transition-all duration-200 ${
      isActive
        ? "bg-brand-50 text-brand-700 shadow-sm"
        : "text-slate-600 hover:bg-slate-100 hover:text-slate-800"
    }`;

  return (
    <div className="min-h-screen bg-slate-100">
      <div className="mx-auto flex max-w-7xl gap-6 p-4 md:p-6">
        <aside className="hidden w-64 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm md:block">
          <h1 className="mb-6 text-lg font-semibold text-brand-700">AI Knowledge Base</h1>
          <nav className="space-y-2 text-sm">
            <NavLink to="/" className={navItemClass}>
              <BarChart3 size={16} />
              Dashboard
            </NavLink>
            <NavLink to="/search" className={navItemClass}>
              <Search size={16} />
              Search
            </NavLink>
            <NavLink to="/history" className={navItemClass}>
              <History size={16} />
              History
            </NavLink>
            {user?.role === "admin" && (
              <NavLink to="/upload" className={navItemClass}>
                <Upload size={16} />
                Upload
              </NavLink>
            )}
          </nav>
          <div className="mt-8 border-t pt-4 text-xs text-slate-500">
            <p>{user?.email}</p>
            <p className="capitalize">
              {user?.role} - {user?.department}
            </p>
            <Button
              onClick={handleLogout}
              variant="secondary"
              className="mt-3 text-xs"
            >
              <LogOut size={14} />
              Logout
            </Button>
          </div>
        </aside>
        <main className="flex-1 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
