import { useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { PasswordInput } from "@/components/custom/PasswordInput"
import { updateUserAdmin } from "@/api/auth/users"
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import { useParams } from 'react-router-dom';
import { PasswordRequirements } from "@/components/custom/PasswordRequirements"

export default function ProfileSettings() {
    const formRef = useRef<HTMLFormElement>(null)

    // Stany formularza profilu
    const [errors, setErrors] = useState({ username: "", password: "", confirmPassword: "" })
    const [password, setPassword] = useState("")

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

    const strengthScore = getPasswordStrength(password)

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
            setPassword("")
            return "Profil zaktualizowany pomyślnie."
        },
        error: () => "Nie udało się zaktualizować profilu.",
        })
    }

  const handleReset = () => {
    setErrors({ username: "", password: "", confirmPassword: "" })
    setPassword("")
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
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={cn(errors.password && "border-destructive focus-visible:ring-destructive")}
            />
            <PasswordRequirements password={password} inputId="register-password" />
            {errors.password && <p className="text-sm text-destructive mt-1">{errors.password}</p>}
          </Field>

          <Field>
            <FieldLabel htmlFor="confirm-password">Confirm Password</FieldLabel>
            <PasswordInput
              id="confirm-password"
              name="confirm-password"
              className={cn(errors.confirmPassword && "border-destructive focus-visible:ring-destructive")}
              disabled={!password}
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