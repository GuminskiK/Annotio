import { useNavigate } from "react-router-dom";
import { ListTodo, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <main className="mx-auto flex min-h-[calc(100vh-65px)] w-full max-w-7xl items-center justify-center p-6">
      <section className="w-full rounded-xl border bg-card p-8 text-center text-muted-foreground">
        <p className="mb-6">Panel Annotio</p>
        <div className="flex flex-wrap justify-center gap-3">
          <Button onClick={() => navigate("/tasks")}><ListTodo className="mr-2 h-4 w-4" />Lista zadań</Button>
          <Button variant="outline" onClick={() => navigate("/campaigns/new")}><Plus className="mr-2 h-4 w-4" />Nowa kampania</Button>
          <Button variant="outline" onClick={() => navigate("/tasks/new")}><Plus className="mr-2 h-4 w-4" />Nowy task</Button>
        </div>
      </section>
    </main>
  );
}
