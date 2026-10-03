import React, { useEffect, useState } from 'react';
import { Button } from "@/components/ui/button.tsx";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription
} from "@/components/ui/card";
import { Input } from "@/components/ui/input.tsx";
import { Label } from "@/components/ui/label.tsx";
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.tsx';
import { PasswordInput } from '@/components/custom/PasswordInput.tsx';

export default function Login() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, login, loginMfa } = useAuth();
  
  // Stany do obsługi dwuetapowego logowania
  const [step, setStep] = useState<1 | 2>(1);
  const [credentials, setCredentials] = useState({ username: '', password: '', mfaToken: '', rememberMe: false });
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate]);

  const handleLogin = async (event: React.SubmitEvent) => {
    event.preventDefault();
    setErrorMessage(null);
    const formData = new FormData(event.currentTarget as HTMLFormElement);

    if (step === 1) {
      const username = formData.get("username") as string;
      const password = formData.get("password") as string;
      const rememberMe = formData.get("remember_me") === "on";
      
      try {

        setCredentials({ username, password, mfaToken: '', rememberMe });
        
        const response = await login(username, password, rememberMe);

        if (response?.message === 'Logged in successfully!') {
          navigate('/dashboard'); 
        } else if (response?.status === "mfa_required") {
          response.mfa_token && setCredentials(prev => ({ ...prev, mfaToken: response.mfa_token }));
          setStep(2);
        }

      } catch (error: any) {

        setErrorMessage(error?.response?.data?.detail || "Nieprawidłowy login lub hasło.");
        console.error('Login failed:', error);
      }

    } else if (step === 2) {
      const mfaCode = formData.get("mfa_code") as string;
      
      try {
        const response = await loginMfa(mfaCode, credentials.mfaToken, credentials.rememberMe);
        if (response?.message === 'Logged in successfully!') {
          navigate('/dashboard'); 
        }
      } catch (error: any) {
        setErrorMessage(error?.response?.data?.detail || "Nieprawidłowy kod 2FA.");
        console.error('2FA validation failed:', error);
      }
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>
            <div className="text-2xl font-bold text-center mb-2">Annotio</div>
          </CardTitle>
          {step === 2 && (
            <CardDescription className="text-center mt-2">
              Wprowadź kod z aplikacji uwierzytelniającej.
            </CardDescription>
          )}
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin}>
            <div className="flex flex-col gap-6">
              
              {errorMessage && (
                <div className="text-sm font-medium text-destructive text-center">
                  {errorMessage}
                </div>
              )}

              {step === 1 ? (
                // --- KROK 1: LOGIN I HASŁO ---
                <>

                  <div className="grid gap-2">
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      name="username"
                      type="text"
                      placeholder="username"
                      required
                    />
                  </div>

                  <div className="grid gap-2">
                    <Label htmlFor="password">Password</Label>
                    <PasswordInput 
                      id="password"
                      name="password"
                      required 
                    />
                  </div>

                  <div className="flex flex-row justify-between items-center gap-2">                  
                    <label className="flex items-center gap-2 text-sm text-muted-foreground">
                      <input
                        type="checkbox"
                        name="remember_me"
                        className="h-4 w-4 accent-primary"
                      />
                      Remember for 30 days
                    </label>
                    
                    <button
                      type="button"
                      className="text-sm text-primary underline underline-offset-4 text-left"
                      onClick={() => navigate('/forgot-password')}
                    >
                      Forgot password
                    </button>


                  </div>

                </>
              ) : (
                // --- KROK 2: KOD 2FA ---
                <div className="grid gap-2">
                  <Label htmlFor="mfa_code">Kod 2FA (TOTP)</Label>
                  <Input
                    id="mfa_code"
                    name="mfa_code"
                    type="text"
                    inputMode="text"
                    pattern="[A-Za-z0-9]{6,8}"
                    maxLength={8}
                    placeholder="Kod TOTP lub zapasowy"
                    autoComplete="one-time-code"
                    required
                  />
                </div>
              )}
            </div>
            
            { step === 1 ? (
              <>
                <Button type="submit" className="w-full self-center mt-6">
                  Sign in
                </Button>

                <div className="text-sm text-muted-foreground text-center mt-2">
                  Don't have an account?{" "}
                  <button
                    type="button"
                    className="text-primary underline"
                    onClick={() => navigate('/register')}
                  >
                    Sign up
                  </button>
                </div>
              </>
              ) : (
                <Button type="submit" className="w-full self-center mt-6">
                  Verify code
                </Button>
              )
            }
            
            {step === 2 && (
              <Button 
                type="button" 
                variant="ghost" 
                className="w-full mt-2" 
                onClick={() => {
                  setStep(1);
                  setErrorMessage(null);
                }}
              >
                Wróć
              </Button>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  );
}