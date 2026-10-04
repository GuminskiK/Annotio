import { useEffect, useState } from "react";
import type React from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { getMyCampaigns, type Campaign } from "@/api/campaigns";
import { createTask, uploadTaskFiles, type TaskAnswerType, type TaskContentType } from "@/api/tasks";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const answerTypes: TaskAnswerType[] = ["text", "single_choice", "multiple_choice"];

export default function TaskWizard() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ campaign_id: searchParams.get("campaign_id") || "", reward: "", time_limit_minutes: "30", required_assignments: "1", task_content_type: "text", task_answer_type: "text", instruction: "", options: "" });

  useEffect(() => { getMyCampaigns().then(setCampaigns).catch(() => setError("Nie udało się pobrać kampanii.")); }, []);
  const update = (key: string, value: string) => setForm((current) => ({ ...current, [key]: value }));
  const isMedia = form.task_content_type === "image" || form.task_content_type === "video";

  const submit = async (event: React.SubmitEvent) => {
    event.preventDefault();
    setError("");
    try {
      const task = await createTask({
        campaign_id: form.campaign_id,
        reward: form.reward,
        time_limit_minutes: Number(form.time_limit_minutes),
        required_assignments: Number(form.required_assignments),
        task_content_type: form.task_content_type as TaskContentType,
        task_answer_type: form.task_answer_type as TaskAnswerType,
        data_json: { instruction: form.instruction, options: form.options.split("\n").map((option) => option.trim()).filter(Boolean) },
      });
      if (files.length > 0) await uploadTaskFiles(task.id, files);
      navigate("/tasks");
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || "Nie udało się utworzyć taska.");
    }
  };

  return <main className="flex min-h-screen items-center justify-center bg-background p-4"><Card className="w-full max-w-3xl"><CardHeader><CardTitle>Kreator taska</CardTitle><CardDescription>Wybierz rodzaj danych i sposób odpowiedzi. Dla obrazu lub wideo możesz dodać wiele plików.</CardDescription></CardHeader><CardContent><form className="space-y-5" onSubmit={submit}><div><Label>Kampania</Label><select className="h-9 w-full rounded-md border bg-background px-3 text-sm" value={form.campaign_id} onChange={(e) => update("campaign_id", e.target.value)} required><option value="">Wybierz kampanię</option>{campaigns.map((campaign) => <option key={campaign.id} value={campaign.id}>{campaign.title}</option>)}</select></div><div className="grid gap-4 sm:grid-cols-2"><div><Label>Typ treści</Label><select className="h-9 w-full rounded-md border bg-background px-3 text-sm" value={form.task_content_type} onChange={(e) => { update("task_content_type", e.target.value); setFiles([]); }}><option value="text">Tekst</option><option value="image">Obraz</option><option value="video">Wideo</option></select></div><div><Label>Typ odpowiedzi</Label><select className="h-9 w-full rounded-md border bg-background px-3 text-sm" value={form.task_answer_type} onChange={(e) => update("task_answer_type", e.target.value)}>{answerTypes.map((type) => <option key={type} value={type}>{type}</option>)}</select></div><div><Label>Reward</Label><Input type="number" min="0" step="0.01" value={form.reward} onChange={(e) => update("reward", e.target.value)} required /></div><div><Label>Czas na wykonanie (min)</Label><Input type="number" min="1" value={form.time_limit_minutes} onChange={(e) => update("time_limit_minutes", e.target.value)} required /></div><div><Label>Liczba assignmentów</Label><Input type="number" min="1" value={form.required_assignments} onChange={(e) => update("required_assignments", e.target.value)} required /></div></div><div><Label>Instrukcja / tekst</Label><textarea className="min-h-28 w-full rounded-md border bg-background px-3 py-2 text-sm" value={form.instruction} onChange={(e) => update("instruction", e.target.value)} required={form.task_content_type === "text"} /></div>{(form.task_answer_type === "single_choice" || form.task_answer_type === "multiple_choice") && <div><Label>Opcje odpowiedzi, jedna w wierszu</Label><textarea className="min-h-24 w-full rounded-md border bg-background px-3 py-2 text-sm" value={form.options} onChange={(e) => update("options", e.target.value)} required /></div>}{isMedia && <div><Label>Pliki ({form.task_content_type === "image" ? "obrazy" : "wideo"})</Label><Input type="file" accept={form.task_content_type === "image" ? "image/*" : "video/*"} multiple onChange={(e) => setFiles(Array.from(e.target.files || []))} /><p className="mt-1 text-xs text-muted-foreground">Wybrano: {files.length}</p></div>}{error && <p className="text-sm text-destructive">{error}</p>}<div className="flex justify-end gap-2"><Button type="button" variant="outline" onClick={() => navigate("/tasks")}>Anuluj</Button><Button type="submit">Utwórz task</Button></div></form></CardContent></Card></main>;
}
