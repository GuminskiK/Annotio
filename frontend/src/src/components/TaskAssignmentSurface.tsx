import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AssignmentView } from "@/api/tasks";

interface TaskAssignmentSurfaceProps {
  view: AssignmentView;
  review: boolean;
  onSubmit: (answer: string | string[]) => Promise<void>;
  onReview?: (action: "accept" | "reject") => Promise<void>;
}

export default function TaskAssignmentSurface({ view, review, onSubmit, onReview }: TaskAssignmentSurfaceProps) {
  const options = view.data_json.options || [];
  const instruction = view.data_json.instruction || "";
  const [mediaIndex, setMediaIndex] = useState(0);
  const [answer, setAnswer] = useState<string | string[]>(view.result_data_json?.answer || (view.task_answer_type === "multiple_choice" ? [] : ""));

  useEffect(() => {
    setAnswer(view.result_data_json?.answer || (view.task_answer_type === "multiple_choice" ? [] : ""));
  }, [view.assignment_id]);

  const toggleOption = (option: string) => {
    if (review) return;
    const selected = Array.isArray(answer) ? answer : [];
    setAnswer(selected.includes(option) ? selected.filter((item) => item !== option) : [...selected, option]);
  };

  return (
    <main className="mx-auto flex min-h-[calc(100vh-65px)] w-full max-w-4xl flex-col gap-6 p-6">
      <Card><CardHeader><CardTitle>Treść zadania</CardTitle></CardHeader><CardContent className="space-y-4"><p className="whitespace-pre-wrap text-base">{instruction || "Brak dodatkowej instrukcji."}</p>
        {view.task_content_type === "image" && view.resource_files.length > 0 && <div className="space-y-3"><div className="flex min-h-64 items-center justify-center rounded-lg bg-muted p-3"><img src={view.resource_files[mediaIndex].url} alt={view.resource_files[mediaIndex].original_name} className="max-h-[28rem] max-w-full object-contain" /></div><div className="flex items-center justify-between"><Button variant="outline" disabled={mediaIndex === 0} onClick={() => setMediaIndex((index) => index - 1)}>Poprzednie</Button><span className="text-sm text-muted-foreground">{mediaIndex + 1} / {view.resource_files.length}</span><Button variant="outline" disabled={mediaIndex === view.resource_files.length - 1} onClick={() => setMediaIndex((index) => index + 1)}>Następne</Button></div></div>}
        {view.task_content_type === "video" && view.resource_files[0] && <video className="max-h-[28rem] w-full rounded-lg bg-black" controls src={view.resource_files[0].url} />}
      </CardContent></Card>
      <Card><CardHeader><CardTitle>Odpowiedź</CardTitle></CardHeader><CardContent className="space-y-4">
        {view.task_answer_type === "text" && <textarea className="min-h-36 w-full rounded-md border bg-background p-3 text-sm" value={typeof answer === "string" ? answer : answer.join(", ")} onChange={(event) => setAnswer(event.target.value)} disabled={review} placeholder="Wpisz odpowiedź" />}
        {view.task_answer_type === "single_choice" && <div className="space-y-3">{options.map((option) => <label key={option} className="flex items-center gap-3 rounded-md border p-3"><input type="radio" name="task-answer" value={option} checked={answer === option} onChange={() => setAnswer(option)} disabled={review} />{option}</label>)}</div>}
        {view.task_answer_type === "multiple_choice" && <div className="space-y-3">{options.map((option) => <label key={option} className="flex items-center gap-3 rounded-md border p-3"><input type="checkbox" value={option} checked={Array.isArray(answer) && answer.includes(option)} onChange={() => toggleOption(option)} disabled={review} />{option}</label>)}</div>}
        <div className="flex justify-end gap-3">{review ? <><Button variant="destructive" onClick={() => onReview?.("reject")}>Odrzuć</Button><Button onClick={() => onReview?.("accept")}>Zatwierdź</Button></> : <Button onClick={() => onSubmit(answer)} disabled={!answer || (Array.isArray(answer) && answer.length === 0)}>Wyślij odpowiedź</Button>}</div>
      </CardContent></Card>
    </main>
  );
}
