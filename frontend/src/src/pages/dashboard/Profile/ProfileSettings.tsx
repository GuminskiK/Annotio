import { useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { PasswordInput } from "@/components/custom/PasswordInput"
import { updateUser } from "@/api/auth/users"
import { enable2FA, disable2FA, setup2FA } from "@/api/auth/totp" // Zakładamy osobny moduł API
import { toast } from "sonner"
import { cn } from "@/lib/utils"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { QRCodeSVG } from "qrcode.react" // Opcjonalnie do generowania QR po stronie klienta z otpauth URI
import { useAuth } from "@/context/AuthContext"

export default function ProfileSettings() {
  const formRef = useRef<HTMLFormElement>(null)
  const { user } = useAuth();
  const is_totp_enabled = user?.is_totp_enabled || false;

  // Stany formularza profilu
  const [errors, setErrors] = useState({ username: "", password: "", confirmPassword: "" })
  const [passwordValue, setPasswordValue] = useState("")

  // Stany procesu 2FA
  const [isTotpEnabledState, setIsTotpEnabledState] = useState(is_totp_enabled)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [totpStep, setTotpStep] = useState<"setup" | "disable">("setup")
  const [qrCodeUri, setQrCodeUri] = useState<string>("")
  const [secretKey, setSecretKey] = useState<string>("")
  const [totpCode, setTotpCode] = useState("")
  const [isSubmitting2FA, setIsSubmitting2FA] = useState(false)

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

  // --- OBSŁUGA 2FA ---

  const handleStart2FASetup = async () => {
    try {
      // Pobieramy secret oraz url do QR
      const data = await setup2FA() 
      // Oczekujemy np. { secret: "ABC...", qr_code_uri: "otpauth://totp/..." }
      setQrCodeUri(data.qr_code_uri || data.totp_uri)
      setSecretKey(data.secret)
      setTotpStep("setup")
      setTotpCode("")
      setIsModalOpen(true)
    } catch (error) {
      console.error("2FA Setup failed:", error)
      toast.error("Nie udało się wygenerować danych konfiguracji 2FA.")
    }
  }

  const handleStart2FADisable = () => {
    setTotpStep("disable")
    setTotpCode("")
    setIsModalOpen(true)
  }

  const handleConfirm2FA = async () => {
    if (totpCode.length < 6) {
      toast.error("Wprowadź poprawny 6-cyfrowy kod TOTP.")
      return
    }

    setIsSubmitting2FA(true)

    try {
      if (totpStep === "setup") {
        await enable2FA(totpCode)
        setIsTotpEnabledState(true)
        toast.success("Weryfikacja dwuetapowa została pomyślnie włączona!")
      } else {
        await disable2FA(totpCode)
        setIsTotpEnabledState(false)
        toast.success("Weryfikacja dwuetapowa została wyłączona.")
      }
      setIsModalOpen(false)
    } catch (error: any) {
      console.error("2FA Action failed:", error)
      toast.error(error.response?.data?.detail || "Niepoprawny kod 2FA. Spróbuj ponownie.")
    } finally {
      setIsSubmitting2FA(false)
    }
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

    toast.promise(updateUser(payload), {
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

      {/* SEKCJA KARTY 2FA */}
      <div className="flex flex-row gap-4 justify-start items-center">
        {/* Usunięto max-w-md i mx-w-full */}
        <Card className="flex flex-col items-center w-full gap-4">
          <div className="font-medium text-center">
            Two-Factor Authentication (2FA):
            <span className={isTotpEnabledState ? " text-green-600 font-semibold" : " text-destructive font-semibold"}>
              {isTotpEnabledState ? " Włączone" : " Wyłączone"}
            </span>
          </div>

          <Button
            variant={isTotpEnabledState ? "destructive" : "default"}
            onClick={isTotpEnabledState ? handleStart2FADisable : handleStart2FASetup}
            className="w-full"
          >
            {isTotpEnabledState ? "Wyłącz 2FA" : "Włącz 2FA"}
          </Button>
        </Card>
      </div>

      {/* MODAL / DIALOG DLA AKCJI 2FA */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>
              {totpStep === "setup" ? "Konfiguracja Weryfikacji Dwuetapowej" : "Wyłączanie 2FA"}
            </DialogTitle>
            <DialogDescription>
              {totpStep === "setup"
                ? "Zeskanuj kod QR w aplikacji uwierzytelniającej (np. Google Authenticator), a następnie wprowadź wygenerowany kod."
                : "Aby potwierdzić wyłączenie weryfikacji dwuetapowej, wprowadź aktualny kod z aplikacji."}
            </DialogDescription>
          </DialogHeader>

          <div className="flex flex-col items-center gap-4 py-4">
            {totpStep === "setup" && qrCodeUri && (
              <div className="flex flex-col items-center gap-2 border p-4 rounded-lg bg-white">
                <QRCodeSVG value={qrCodeUri} size={180} />
                {secretKey && (
                  <p className="text-xs text-muted-foreground font-mono mt-2 break-all max-w-xs text-center">
                    Klucz opcjonalny: {secretKey}
                  </p>
                )}
              </div>
            )}

            <Field className="w-full">
              <FieldLabel htmlFor="totp-code" className="text-center block">
                Kod weryfikacyjny TOTP
              </FieldLabel>
              <Input
                id="totp-code"
                type="text"
                inputMode="numeric"
                maxLength={6}
                placeholder="123456"
                className="text-center text-lg tracking-widest font-mono"
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, ""))}
              />
            </Field>
          </div>

          <DialogFooter className="flex gap-2 sm:justify-end">
            <Button variant="outline" onClick={() => setIsModalOpen(false)}>
              Anuluj
            </Button>
            <Button
              onClick={handleConfirm2FA}
              disabled={totpCode.length !== 6 || isSubmitting2FA}
              variant={totpStep === "disable" ? "destructive" : "default"}
            >
              {isSubmitting2FA ? "Weryfikacja..." : totpStep === "setup" ? "Włącz 2FA" : "Wyłącz 2FA"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}