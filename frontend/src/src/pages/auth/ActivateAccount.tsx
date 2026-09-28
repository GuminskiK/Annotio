import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { activateAccountApi } from "@/api/auth/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function ActivateAccount() {
  const [searchParams] = useSearchParams();
  const [state, setState] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("Aktywujemy konto...");

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setState("error");
      setMessage("Link aktywacyjny jest nieprawidłowy lub niekompletny.");
      return;
    }
    activateAccountApi(token)
      .then(() => {
        setState("success");
        setMessage("Konto zostało aktywowane. Możesz się teraz zalogować.");
      })
      .catch((error: any) => {
        setState("error");
        setMessage(error.response?.data?.detail || "Link aktywacyjny wygasł lub jest nieprawidłowy.");
      });
  }, [searchParams]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <CardTitle>{state === "success" ? "Konto aktywowane" : state === "error" ? "Nie udało się aktywować konta" : "Aktywacja konta"}</CardTitle>
          <CardDescription>{message}</CardDescription>
        </CardHeader>
        {state !== "loading" && <CardContent><Link className="text-primary underline underline-offset-4" to="/login">Przejdź do logowania</Link></CardContent>}
      </Card>
    </main>
  );
}
