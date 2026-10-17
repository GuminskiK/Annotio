import { useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { ListTodo, LogOut, Plus, ShieldAlert, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";

type ViewMode = "worker" | "auditor" | "requester";

export default function AuthenticatedShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();
  const businessRoles = user?.roles?.map((role) => role.toLowerCase()) || ["worker"];
  const isAdmin = user?.is_superuser === true;
  const availableModes: ViewMode[] = isAdmin
    ? ["worker", "auditor", "requester"]
    : businessRoles.includes("auditor")
      ? ["auditor"]
      : businessRoles.includes("client") || businessRoles.includes("requester")
        ? ["requester"]
        : ["worker"];
  const [viewMode, setViewMode] = useState<ViewMode>(() => {
    const stored = sessionStorage.getItem("annotio-view-mode") as ViewMode | null;
    return stored && availableModes.includes(stored) ? stored : availableModes[0];
  });

  useEffect(() => {
    if (!availableModes.includes(viewMode)) {
      setViewMode(availableModes[0]);
    }
  }, [user?.is_superuser, user?.roles]);

  const changeView = (mode: ViewMode) => {
    setViewMode(mode);
    sessionStorage.setItem("annotio-view-mode", mode);
    navigate(mode === "requester" ? "/dashboard" : "/tasks");
  };

  const handleLogout = async () => {
    if (await logout()) navigate("/");
  };

  const avatarUrl = user?.avatar_url;
  const onTasks = location.pathname.startsWith("/tasks");

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-30 border-b bg-background/95 px-4 py-3 backdrop-blur sm:px-6">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3">
          <button className="text-xl font-bold tracking-tight" onClick={() => navigate("/dashboard")}>Annotio</button>
          <div className="flex items-center gap-2">
            <label className="sr-only" htmlFor="view-mode">Tryb widoku</label>
            <select id="view-mode" className="h-9 rounded-md border bg-background px-3 text-sm" value={viewMode} onChange={(event) => changeView(event.target.value as ViewMode)}>
              {availableModes.map((mode) => <option key={mode} value={mode}>{mode === "worker" ? "Worker" : mode === "auditor" ? "Auditor" : "Requester"}</option>)}
            </select>
            {viewMode === "worker" && <Button variant={onTasks ? "secondary" : "ghost"} size="sm" onClick={() => navigate("/tasks")}><ListTodo className="mr-2 h-4 w-4" />Zadania</Button>}
            {viewMode === "requester" && <><Button variant="ghost" size="sm" onClick={() => navigate("/campaigns/new")}><Plus className="mr-2 h-4 w-4" />Kampania</Button><Button variant="ghost" size="sm" onClick={() => navigate("/tasks/new")}><Plus className="mr-2 h-4 w-4" />Task</Button></>}
            {isAdmin && <Button variant="ghost" size="sm" onClick={() => navigate("/admin")}><ShieldAlert className="mr-2 h-4 w-4" />Admin</Button>}
            <button className="flex items-center gap-2 rounded-md px-2 py-1 hover:bg-muted" onClick={() => navigate("/profile")}>
              <span className="flex h-8 w-8 items-center justify-center overflow-hidden rounded-full border bg-muted">{avatarUrl ? <img src={avatarUrl} alt="Avatar" className="h-full w-full object-cover" /> : <User className="h-4 w-4" />}</span>
              <span className="hidden text-sm font-medium sm:inline">{user?.username || "Użytkownik"}</span>
            </button>
            <Button variant="ghost" size="icon" title="Wyloguj" onClick={handleLogout}><LogOut className="h-4 w-4" /></Button>
          </div>
        </div>
      </header>
      <Outlet />
    </div>
  );
}
