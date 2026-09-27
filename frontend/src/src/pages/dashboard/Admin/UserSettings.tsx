import { useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { PasswordInput } from "@/components/custom/PasswordInput"
import { updateUserAdmin } from "@/api/auth/users"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { useParams } from 'react-router-dom';

export default function ProfileSettings() {
    const formRef = useRef<HTMLFormElement>(null)

    // Stany formularza profilu
    const [errors, setErrors] = useState({ username: "", password: "", confirmPassword: "" })
    const [passwordValue, setPasswordValue] = useState("")

    const { id } = useParams();
    // Ocena siły hasła
    const getPasswordStrength = (pass: string) => {
        let score = 0
        if (!pass) return score
        if (pass.length >= 8) score += 1
        if (/[a-z]/.test(pass)) score += 1
        if (/[A-Z]/.test(pass)) score += 1
        if (/[0-9]/.test(pass)) score += 1
        if (/[^a-zA-Z0-9]/.test(pass)) score += 1
        return score
    }

    const strengthScore = getPasswordStrength(passwordValue)

    const getStrengthColor = (score: number) => {
        if (score === 0) return "bg-transparent"
        if (score <= 2) return "bg-destructive"
        if (score <= 4) return "bg-yellow-500"
        return "bg-green-500"
    }

    // --- UPDATE PROFILU ---

    const handleProfileUpdate = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        setErrors({ username: "", password: "", confirmPassword: "" })

        const formData = new FormData(event.currentTarget)
        const username = formData.get("username") as string
        const password = formData.get("password") as string
        const confirmPassword = formData.get("confirm-password") as string

        if (!username && !password) {
        toast.info("Nie wprowadzono żadnych zmian.")
        return
        }

        let hasError = false
        const newErrors = { username: "", password: "", confirmPassword: "" }

        if (username) {
        if (!/^[a-zA-Z0-9]+$/.test(username)) {
            newErrors.username = "Nazwa użytkownika może zawierać tylko litery i cyfry."
            hasError = true
        }
        if (username.length < 3 || username.length > 40) {
            newErrors.username = "Nazwa użytkownika musi mieć od 3 do 40 znaków."
            hasError = true
        }
        }

        if (password) {
        if (strengthScore < 5) {
            newErrors.password = "Hasło nie spełnia wszystkich wymagań bezpieczeństwa."
            hasError = true
        }
        if (password !== confirmPassword) {
            newErrors.confirmPassword = "Hasła nie są identyczne."
            hasError = true
        }
        }

        if (hasError) {
        setErrors(newErrors)
        if (newErrors.confirmPassword) toast.error(newErrors.confirmPassword)
        return
        }

        const payload: { username?: string; password?: string } = {}
        if (username) payload.username = username
        if (password) payload.password = password

        if (!id) {
            toast.error("Nie znaleziono ID użytkownika.")
            return
        }

        toast.promise(updateUserAdmin(payload, id), {
        loading: "Aktualizowanie profilu...",
        success: () => {
            formRef.current?.reset()
            setPasswordValue("")
            return "Profil zaktualizowany pomyślnie."
        },
        error: () => "Nie udało się zaktualizować profilu.",
        })
    }

  const handleReset = () => {
    setErrors({ username: "", password: "", confirmPassword: "" })
    setPasswordValue("")
  }

  return (
    <div className="flex flex-col m-10 gap-10">
      <form ref={formRef} onSubmit={handleProfileUpdate} onReset={handleReset}>
        <FieldGroup className="space-y-2">
          <Field>
            <FieldLabel htmlFor="username">Name</FieldLabel>
            <Input
              id="username"
              name="username"
              placeholder="Jordan Lee"
              className={cn("w-full", errors.username && "border-destructive focus-visible:ring-destructive")}
            />
            {errors.username && <p className="text-sm text-destructive mt-1">{errors.username}</p>}
          </Field>

          <Field>
            <FieldLabel htmlFor="password">New Password</FieldLabel>
            <PasswordInput
              id="password"
              name="password"
              value={passwordValue}
              onChange={(e) => setPasswordValue(e.target.value)}
              className={cn(errors.password && "border-destructive focus-visible:ring-destructive")}
            />

            {passwordValue && (
              <div className="mt-2 flex flex-col gap-2">
                <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                  <div
                    className={cn("h-full transition-all duration-300 ease-out", getStrengthColor(strengthScore))}
                    style={{ width: `${(strengthScore / 5) * 100}%` }}
                  />
                </div>
                <ul className="text-xs text-muted-foreground grid grid-cols-2 gap-1">
                  <li className={passwordValue.length >= 8 ? "text-green-500" : ""}>✓ Min. 8 znaków</li>
                  <li className={/[A-Z]/.test(passwordValue) ? "text-green-500" : ""}>✓ Duża litera</li>
                  <li className={/[a-z]/.test(passwordValue) ? "text-green-500" : ""}>✓ Mała litera</li>
                  <li className={/[0-9]/.test(passwordValue) ? "text-green-500" : ""}>✓ Cyfra</li>
                  <li className={/[^a-zA-Z0-9]/.test(passwordValue) ? "text-green-500" : ""}>✓ Znak specjalny</li>
                </ul>
              </div>
            )}

            {errors.password && <p className="text-sm text-destructive mt-1">{errors.password}</p>}
          </Field>

          <Field>
            <FieldLabel htmlFor="confirm-password">Confirm Password</FieldLabel>
            <PasswordInput
              id="confirm-password"
              name="confirm-password"
              className={cn(errors.confirmPassword && "border-destructive focus-visible:ring-destructive")}
              disabled={!passwordValue}
            />
            {errors.confirmPassword && <p className="text-sm text-destructive mt-1">{errors.confirmPassword}</p>}
          </Field>

          <Field orientation="horizontal" className="flex gap-4">
            <Button type="reset" variant="outline">
              Reset
            </Button>
            <Button type="submit">Submit</Button>
          </Field>
        </FieldGroup>
      </form>
    </div>
  )
}