import { useState } from "react";
import type React from "react";
import { Link } from "react-router-dom";
import { requestPasswordResetApi } from "@/api/auth/auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: React.SubmitEvent) => {
    event.preventDefault();
    setError("");
    try {
      await requestPasswordResetApi(email);
      setSent(true);
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || "Nie udało się wysłać wiadomości.");
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Reset hasła</CardTitle>
          <CardDescription>Podaj adres e-mail przypisany do konta.</CardDescription>
        </CardHeader>
        <CardContent>
          {sent ? (
            <div className="space-y-4 text-sm">
              <p>If the account exists, a password reset link has been sent to the provided email address.</p>
              <Link className="text-primary underline underline-offset-4" to="/login">Go to login</Link>
            </div>
          ) : (
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div className="grid gap-2">
                <Label htmlFor="reset-email">E-mail</Label>
                <Input id="reset-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button className="w-full" type="submit">Send reset link</Button>
              <Link className="block text-center text-sm text-primary underline underline-offset-4" to="/login">Go to login</Link>
            </form>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
