import { useState } from "react";
import { useNavigate } from 'react-router-dom';
import type React from "react";
import { createUser } from "@/api/auth/users";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PasswordInput } from "@/components/custom/PasswordInput";
import { PasswordRequirements, passwordRequirements } from "@/components/custom/PasswordRequirements";

export default function Register() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [created, setCreated] = useState(false);

  const handleSubmit = async (event: React.SubmitEvent) => {
    event.preventDefault();
    setError("");

    if (password !== confirmation) {
      setError("Hasła nie są identyczne.");
      return;
    }
    if (!passwordRequirements.every((requirement) => requirement.test(password))) {
      setError("Hasło nie spełnia wszystkich wymagań bezpieczeństwa.");
      return;
    }

    try {
      await createUser({ username, email, plain_password: password });
      setCreated(true);
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || "Nie udało się utworzyć konta.");
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-2 text-center">
          {created ? (
            <CardTitle className="text-2xl">Account Created</CardTitle>
          ) : (
            <CardTitle className="text-2xl">Create an account</CardTitle>
          )}
        </CardHeader>
        <CardContent>
          {created ? (
            <div className="space-y-4 text-center text-sm">
              <p>Please check your email and click the activation link.</p>
            </div>
          ) : (
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div className="grid gap-2">
                <Label htmlFor="register-username">Username</Label>
                <Input id="register-username" value={username} onChange={(event) => setUsername(event.target.value)} minLength={3} maxLength={40} pattern="[a-zA-Z0-9_\-]+" required />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="register-email">E-mail</Label>
                <Input id="register-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="register-password">Password</Label>
                <PasswordInput id="register-password" value={password} onChange={(event) => setPassword(event.target.value)} required />
                <PasswordRequirements password={password} inputId="register-password" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="register-confirm-password">Confirm Password</Label>
                <PasswordInput id="register-confirm-password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} required />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <Button className="w-full" type="submit">Sign up</Button>
                <div className="text-sm text-muted-foreground text-center">
                    Have an account?{" "}
                    <button
                    type="button"
                    className="text-primary underline"
                    onClick={() => navigate('/login')}
                    >
                    Sign in
                    </button>
                </div>
            </form>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
