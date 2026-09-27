import React, { useState } from 'react';
import { Eye, EyeOff } from "lucide-react";
import { Input } from "@/components/ui/input.tsx";

interface PasswordInputProps extends React.ComponentPropsWithoutRef<typeof Input> {}

export function PasswordInput({ className, ...props }: PasswordInputProps) {
  // Stan ukrywania hasła żyje teraz wyłącznie tutaj
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="relative w-full">
      <Input 
        {...props} // To automatycznie przekaże name="password", id, required itp.
        type={showPassword ? "text" : "password"} 
        className={`pr-10 ${className || ''}`}
      />
      <button
        type="button"
        onClick={() => setShowPassword(!showPassword)}
        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
        aria-label={showPassword ? "Hide password" : "Show password"}
      >
        {showPassword ? (
          <EyeOff className="h-4 w-4" />
        ) : (
          <Eye className="h-4 w-4" />
        )}
      </button>
    </div>
  );
}