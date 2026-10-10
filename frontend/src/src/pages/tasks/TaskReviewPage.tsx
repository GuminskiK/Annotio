import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import TaskAssignmentSurface from "@/components/TaskAssignmentSurface";
import { getAssignmentView, reviewAssignment, type AssignmentView } from "@/api/tasks";

export default function TaskReviewPage() {
  const { assignmentId } = useParams();
  const navigate = useNavigate();
  const [view, setView] = useState<AssignmentView | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!assignmentId) return;
    getAssignmentView(assignmentId).then(setView).catch((requestError: any) => setError(requestError.response?.data?.detail || "Nie udało się pobrać odpowiedzi."));
  }, [assignmentId]);

  if (error) return <main className="p-8 text-center text-destructive">{error}</main>;
  if (!view) return <main className="p-8 text-center text-muted-foreground">Ładowanie odpowiedzi...</main>;

  return <TaskAssignmentSurface view={view} review onSubmit={async () => undefined} onReview={async (action) => { if (assignmentId) await reviewAssignment(assignmentId, action); navigate("/tasks"); }} />;
}
