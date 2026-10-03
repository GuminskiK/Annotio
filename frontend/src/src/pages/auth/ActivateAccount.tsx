import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { activateAccountApi } from "@/api/auth/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function ActivateAccount() {
  const [searchParams] = useSearchParams();
  const [state, setState] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("Activating account...");

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setState("error");
      setMessage("A valid activation link is required.");
      return;
    }
    activateAccountApi(token)
      .then(() => {
        setState("success");
        setMessage("Account has been activated. You can now log in.");
      })
      .catch((error: any) => {
        setState("error");
        setMessage(error.response?.data?.detail || "Account activation failed. The link may have expired or is invalid.");
      });
  }, [searchParams]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <CardTitle>{state === "success" ? "Account activated" : state === "error" ? "Failed to activate account" : "Activating account"}</CardTitle>
          <CardDescription>{message}</CardDescription>
        </CardHeader>
        {state !== "loading" && <CardContent><Link className="text-primary underline underline-offset-4" to="/login">Go to login</Link></CardContent>}
      </Card>
    </main>
  );
}
