import { useState } from "react";
import type React from "react";
import { Link, useSearchParams } from "react-router-dom";
import { changePasswordApi } from "@/api/auth/auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PasswordInput } from "@/components/custom/PasswordInput";
import { Label } from "@/components/ui/label";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (event: React.SubmitEvent) => {
    event.preventDefault();
    setError("");
    if (!token) {
      setError("Link resetujący jest nieprawidłowy lub niekompletny.");
      return;
    }
    if (password !== confirmation) {
      setError("Hasła nie są identyczne.");
      return;
    }
    try {
      const response = await changePasswordApi(token, password);
      setMessage(response.message || "Hasło zostało zmienione.");
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || "Link resetujący wygasł lub jest nieprawidłowy.");
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Ustaw nowe hasło</CardTitle>
          <CardDescription>Wybierz hasło spełniające wymagania bezpieczeństwa.</CardDescription>
        </CardHeader>
        <CardContent>
          {message ? (
            <div className="space-y-4 text-sm"><p>{message}</p><Link className="text-primary underline underline-offset-4" to="/login">Przejdź do logowania</Link></div>
          ) : (
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div className="grid gap-2"><Label htmlFor="new-password">Nowe hasło</Label><PasswordInput id="new-password" value={password} onChange={(event) => setPassword(event.target.value)} required /></div>
              <div className="grid gap-2"><Label htmlFor="confirm-password">Powtórz hasło</Label><PasswordInput id="confirm-password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} required /></div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button className="w-full" type="submit">Zmień hasło</Button>
            </form>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
