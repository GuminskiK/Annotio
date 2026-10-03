import { useState } from "react";
import { Label } from "@/components/ui/label";

export const passwordRequirements = [
  { label: "At least 12 characters long", test: (value: string) => value.length >= 8 },
  { label: "Must contain at least one uppercase letter", test: (value: string) => /[A-Z]/.test(value) },
  { label: "Must contain at least one lowercase letter", test: (value: string) => /[a-z]/.test(value) },
  { label: "Must conatin at least one special character", test: (value: string) => /\d/.test(value) },
  { label: "Must contain at least one digit", test: (value: string) => /[^a-zA-Z0-9]/.test(value) },
];

interface PasswordRequirementsProps {
  password: string;
  inputId: string;
}

export function PasswordRequirements({ password, inputId }: PasswordRequirementsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const completed = passwordRequirements.filter((requirement) => requirement.test(password)).length;
  const progress = (completed / passwordRequirements.length) * 100;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label htmlFor={inputId}>Password Strength</Label>
        <div className="relative">
          <button
            type="button"
            aria-label="Pokaż wymagania hasła"
            aria-expanded={isOpen}
            className="flex h-5 w-7 items-center justify-center rounded-full border text-xs font-semibold text-muted-foreground hover:border-primary hover:text-primary"
            onClick={() => setIsOpen((open) => !open)}
          >
            ?
          </button>
          {isOpen && (
            <div className="absolute right-0 top-7 z-20 w-72 rounded-md border bg-popover p-3 text-xs text-popover-foreground shadow-md">
              <p className="font-medium">Password Requirements</p>
              <ul className="space-y-1 text-left mt-2">
                {passwordRequirements.map((requirement) => (
                  <li key={requirement.label} className={requirement.test(password) ? "text-emerald-600" : "text-muted-foreground"}>
                    {requirement.test(password) ? "✓" : "•"} {requirement.label}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-secondary" aria-label={`Password strength: ${completed} of ${passwordRequirements.length}`}>
        <div className={`h-full transition-all ${completed <= 2 ? "bg-destructive" : completed < 5 ? "bg-amber-500" : "bg-emerald-500"}`} style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
}
