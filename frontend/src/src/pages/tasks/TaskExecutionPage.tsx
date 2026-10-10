import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import TaskAssignmentSurface from "@/components/TaskAssignmentSurface";
import { getAssignmentView, reserveTask, submitTask, type AssignmentView } from "@/api/tasks";

export default function TaskExecutionPage() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [view, setView] = useState<AssignmentView | null>(null);
  const [token, setToken] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!taskId) return;
    reserveTask(taskId)
      .then((assignment) => {
        setToken(assignment.token);
        return getAssignmentView(assignment.id);
      })
      .then(setView)
      .catch((requestError: any) => setError(requestError.response?.data?.detail || "Nie udało się zarezerwować zadania."));
  }, [taskId]);

  if (error) return <main className="p-8 text-center text-destructive">{error}</main>;
  if (!view) return <main className="p-8 text-center text-muted-foreground">Ładowanie zadania...</main>;

  return <TaskAssignmentSurface view={view} review={false} onSubmit={async (answer) => { await submitTask(token, answer); navigate("/tasks"); }} />;
}
