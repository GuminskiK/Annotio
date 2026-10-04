import { useState } from "react";
import type React from "react";
import { useNavigate } from "react-router-dom";
import { createCampaign } from "@/api/campaigns";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function CampaignWizard() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [form, setForm] = useState({ title: "", description: "", total_budget: "", acceptance_strategy: "auto_48h", status: "draft" });
  const update = (key: string, value: string) => setForm((current) => ({ ...current, [key]: value }));

  const submit = async (event: React.SubmitEvent) => {
    event.preventDefault();
    setError("");
    try {
      const campaign = await createCampaign({ ...form, total_budget: form.total_budget, acceptance_strategy: form.acceptance_strategy as "auto_48h" | "auditor_required", status: form.status as "draft" | "active" | "paused" | "finished" });
      navigate(`/tasks/new?campaign_id=${campaign.id}`);
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || "Nie udało się utworzyć kampanii.");
    }
  };

  return <main className="flex min-h-screen items-center justify-center bg-background p-4"><Card className="w-full max-w-2xl"><CardHeader><CardTitle>Kreator kampanii</CardTitle><CardDescription>Uzupełnij podstawowe informacje, a następnie dodaj taski.</CardDescription></CardHeader><CardContent><form className="space-y-5" onSubmit={submit}><div><Label htmlFor="title">Tytuł</Label><Input id="title" value={form.title} onChange={(e) => update("title", e.target.value)} required /></div><div><Label htmlFor="description">Opis</Label><textarea id="description" className="min-h-28 w-full rounded-md border bg-background px-3 py-2 text-sm" value={form.description} onChange={(e) => update("description", e.target.value)} required /></div><div className="grid gap-4 sm:grid-cols-3"><div><Label htmlFor="budget">Budżet</Label><Input id="budget" type="number" step="0.01" min="0" value={form.total_budget} onChange={(e) => update("total_budget", e.target.value)} required /></div><div><Label>Strategia akceptacji</Label><select className="h-9 w-full rounded-md border bg-background px-3 text-sm" value={form.acceptance_strategy} onChange={(e) => update("acceptance_strategy", e.target.value)}><option value="auto_48h">Automatycznie po 48h</option><option value="auditor_required">Wymagany audytor</option></select></div><div><Label>Status</Label><select className="h-9 w-full rounded-md border bg-background px-3 text-sm" value={form.status} onChange={(e) => update("status", e.target.value)}><option value="draft">Szkic</option><option value="active">Aktywna</option></select></div></div>{error && <p className="text-sm text-destructive">{error}</p>}<div className="flex justify-end gap-2"><Button type="button" variant="outline" onClick={() => navigate("/tasks")}>Anuluj</Button><Button type="submit">Zapisz i dodaj task</Button></div></form></CardContent></Card></main>;
}
