import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ChevronDown, ChevronUp, SlidersHorizontal } from "lucide-react";
import { listTasks, type Task, type TaskAnswerType, type TaskContentType } from "@/api/tasks";

const contentTypes: TaskContentType[] = ["text", "image", "video"];
const answerTypes: TaskAnswerType[] = ["text", "single_choice", "multiple_choice"];

export default function TasksPage() {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(0);
  const [filtersOpen, setFiltersOpen] = useState(true);
  const [filters, setFilters] = useState({
    reward_min: "", reward_max: "", time_limit_min: "", time_limit_max: "",
    reward_order: "", time_order: "", task_content_type: "", task_answer_type: "",
    owner_id: "", campaign_id: "",
  });

  const loadTasks = async () => {
    const result = await listTasks({
      page,
      page_size: 12,
      ...filters,
      reward_order: filters.reward_order as "asc" | "desc" | undefined,
      time_order: filters.time_order as "asc" | "desc" | undefined,
      task_content_type: filters.task_content_type as TaskContentType | undefined,
      task_answer_type: filters.task_answer_type as TaskAnswerType | undefined,
    });
    setTasks(result.items);
    setPages(result.pages);
  };

  useEffect(() => { loadTasks().catch(console.error); }, [page]);

  const updateFilter = (key: string, value: string) => {
    setFilters((current) => ({ ...current, [key]: value }));
    setPage(1);
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 p-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle className="flex items-center gap-2 text-base"><SlidersHorizontal className="h-4 w-4" />Filtry</CardTitle>
          <Button variant="ghost" size="icon" title={filtersOpen ? "Zwiń filtry" : "Rozwiń filtry"} onClick={() => setFiltersOpen((open) => !open)}>
            {filtersOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </CardHeader>
        {filtersOpen && <CardContent className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div><Label className="mb-2">Reward od</Label><Input type="number" step="0.01" value={filters.reward_min} onChange={(e) => updateFilter("reward_min", e.target.value)} /></div>
          <div><Label className="mb-2">Reward do</Label><Input type="number" step="0.01" value={filters.reward_max} onChange={(e) => updateFilter("reward_max", e.target.value)} /></div>
          <div><Label className="mb-2">Czas od (min)</Label><Input type="number" value={filters.time_limit_min} onChange={(e) => updateFilter("time_limit_min", e.target.value)} /></div>
          <div><Label className="mb-2">Czas do (min)</Label><Input type="number" value={filters.time_limit_max} onChange={(e) => updateFilter("time_limit_max", e.target.value)} /></div>
          <div><Label className="mb-2">Reward sortowanie</Label><select className="h-9 w-full rounded-md border bg-background px-3 text-sm" value={filters.reward_order} onChange={(e) => updateFilter("reward_order", e.target.value)}><option value="">Brak</option><option value="asc">Rosnąco</option><option value="desc">Malejąco</option></select></div>
          <div><Label className="mb-2">Czas sortowanie</Label><select className="h-9 w-full rounded-md border bg-background px-3 text-sm" value={filters.time_order} onChange={(e) => updateFilter("time_order", e.target.value)}><option value="">Brak</option><option value="asc">Rosnąco</option><option value="desc">Malejąco</option></select></div>
          <div><Label className="mb-2">Typ treści</Label><select className="h-9 w-full rounded-md border bg-background px-3 text-sm" value={filters.task_content_type} onChange={(e) => updateFilter("task_content_type", e.target.value)}><option value="">Wszystkie</option>{contentTypes.map((type) => <option key={type} value={type}>{type}</option>)}</select></div>
          <div><Label className="mb-2">Typ odpowiedzi</Label><select className="h-9 w-full rounded-md border bg-background px-3 text-sm" value={filters.task_answer_type} onChange={(e) => updateFilter("task_answer_type", e.target.value)}><option value="">Wszystkie</option>{answerTypes.map((type) => <option key={type} value={type}>{type}</option>)}</select></div>
          <div className="lg:col-span-2"><Label className="mb-2">Owner ID</Label><Input value={filters.owner_id} onChange={(e) => updateFilter("owner_id", e.target.value)} /></div>
          <div className="lg:col-span-2"><Label className="mb-2">Campaign ID</Label><Input value={filters.campaign_id} onChange={(e) => updateFilter("campaign_id", e.target.value)} /></div>
          <Button className="sm:col-span-2 lg:col-span-4" variant="outline" onClick={() => loadTasks().catch(console.error)}>Zastosuj filtry</Button>
        </CardContent>}
      </Card>
      <Card><CardContent className="p-0"><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="border-b text-muted-foreground"><tr><th className="p-4">Task</th><th className="p-4">Reward</th><th className="p-4">Czas</th><th className="p-4">Treść</th><th className="p-4">Odpowiedź</th><th className="p-4">Campaign</th><th className="p-4" /></tr></thead><tbody>{tasks.map((task) => <tr key={task.id} className="border-b last:border-0"><td className="p-4 font-mono text-xs">{task.id}</td><td className="p-4">{task.reward}</td><td className="p-4">{task.time_limit_minutes} min</td><td className="p-4">{task.task_content_type}</td><td className="p-4">{task.task_answer_type}</td><td className="p-4 font-mono text-xs">{task.campaign_id}</td><td className="p-4"><Button size="sm" onClick={() => navigate(`/tasks/${task.id}/execute`)}>Wykonaj</Button></td></tr>)}{tasks.length === 0 && <tr><td className="p-8 text-center text-muted-foreground" colSpan={7}>Brak zadań dla wybranych filtrów.</td></tr>}</tbody></table></div></CardContent></Card>
      <div className="flex items-center justify-between"><span className="text-sm text-muted-foreground">Strona {page} z {Math.max(pages, 1)}</span><div className="flex gap-2"><Button variant="outline" disabled={page <= 1} onClick={() => setPage((current) => current - 1)}>Poprzednia</Button><Button variant="outline" disabled={page >= pages} onClick={() => setPage((current) => current + 1)}>Następna</Button></div></div>
    </main>
  );
}
