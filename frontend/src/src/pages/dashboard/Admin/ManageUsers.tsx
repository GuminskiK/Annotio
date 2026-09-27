import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { 
  Dialog, 
  DialogClose, 
  DialogContent, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from "@/components/ui/dialog"
import { Field, FieldGroup } from "@/components/ui/field"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { PasswordInput } from "@/components/custom/PasswordInput"
import type { UserReadData, UserCreateData } from "@/api/auth/types" // Dodano UserCreateData
import { useEffect, useState, useRef } from "react"
import { getAllUsers, createUser } from "@/api/auth/users"
import { useNavigate } from "react-router"
import { toast } from "sonner"

export default function ManageUsers() {
  const [users, setUsers] = useState<UserReadData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Ref dla formularza, by móc go łatwo zresetować
  const formRef = useRef<HTMLFormElement>(null);

  // Stany dla formularza dodawania użytkownika
  const [isDialogOpen, setIsDialogOpen] = useState(false); 
  const [errors, setErrors] = useState({ username: "", password: "", confirmPassword: "" });
  const [passwordValue, setPasswordValue] = useState("");

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
    if (score === 0) return "bg-gray-200"
    if (score <= 2) return "bg-destructive"
    if (score <= 4) return "bg-yellow-500"
    return "bg-green-500"
  }

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setIsLoading(true);
    try {
      const response = await getAllUsers();
      setUsers(response);
    } catch (error) {
      console.error(error);
      toast.error("Nie udało się pobrać listy użytkowników.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateUser = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setErrors({ username: "", password: "", confirmPassword: "" })

    const formData = new FormData(event.currentTarget)
    // Poprawiono klucz na "username" z "name"
    const username = formData.get("username") as string 
    const password = formData.get("password") as string
    const confirmPassword = formData.get("confirm-password") as string

    let hasError = false
    const newErrors = { username: "", password: "", confirmPassword: "" }

    if (!username || !password) {
      toast.info("Wypełnij wymagane pola.")
      return
    }

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
        newErrors.password = "Hasło jest zbyt słabe."
        hasError = true
      }
      if (password !== confirmPassword) {
        newErrors.confirmPassword = "Hasła nie są identyczne."
        hasError = true
      }
    }

    if (hasError) {
      setErrors(newErrors)
      return
    }

    // Dopasowanie do interfejsu UserCreateData
    const payload: UserCreateData = {
      username: username,
      plain_password: password
    }

    toast.promise(createUser(payload), {
      loading: "Tworzenie użytkownika...",
      success: () => {
        handleReset();
        setIsDialogOpen(false); // Zamknięcie modala
        fetchUsers(); // Odświeżenie listy w tle
        return "Użytkownik został utworzony pomyślnie.";
      },
      error: () => "Nie udało się utworzyć użytkownika.",
    })
  }

  const handleReset = () => {
    formRef.current?.reset();
    setErrors({ username: "", password: "", confirmPassword: "" });
    setPasswordValue("");
  }

  // Zamknięcie modala czyści formularz
  const handleOpenChange = (open: boolean) => {
    setIsDialogOpen(open);
    if (!open) {
      handleReset();
    }
  }

  return (
    <div className="flex flex-col h-full w-full text-left">
        <div className="text-2xl font-bold mb-4">Manage Users</div>

        <div className="overflow-x-auto w-full">
          <Table className="w-full">
            <TableHeader>
              <TableRow>
                <TableHead>Avatar</TableHead>
                <TableHead className="w-[150px]">ID</TableHead>
                <TableHead>Username</TableHead>
                <TableHead>Is Superuser</TableHead>
                <TableHead>Is Banned</TableHead>
                <TableHead>Is TOTP Enabled</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-4">
                    Ładowanie użytkowników...
                  </TableCell>
                </TableRow>
              ) : users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-4">
                    Brak aktywnych użytkowników.
                  </TableCell>
                </TableRow>
              ) : (
                users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      {user.avatar_url ? (
                        <img src={user.avatar_url} alt="Avatar" className="w-10 h-10 rounded-full" />
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center">
                          <span className="text-xs font-bold">{user.username.charAt(0).toUpperCase()}</span>
                        </div>
                      )}
                    </TableCell>
                    <TableCell className="font-medium">{user.id}</TableCell>
                    <TableCell className="font-medium">{user.username}</TableCell>
                    <TableCell className="font-medium">{user.is_superuser ? 'Admin' : 'User'}</TableCell>
                    <TableCell className="font-medium">{user.is_banned ? 'Banned' : 'Active'}</TableCell>
                    <TableCell className="font-medium">{user.is_totp_enabled ? 'Enabled' : 'Disabled'}</TableCell>
                    <TableCell className="text-right">
                      <Button 
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/user/settings/${user.id}`)}
                      >
                        See more
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={handleOpenChange}>
            <DialogTrigger asChild>
              <Button className="w-1/2 mt-5 sm:w-auto" variant="outline">Create User</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-sm">
              <form ref={formRef} onSubmit={handleCreateUser}>
                <DialogHeader>
                  <DialogTitle>Create User</DialogTitle>
                </DialogHeader>
                <FieldGroup className="mt-4 space-y-4">
                  <Field>
                    <Label htmlFor="username">Username</Label>
                    <Input id="username" name="username" placeholder="Username" required />
                    {errors.username && <p className="text-xs text-destructive mt-1">{errors.username}</p>}
                  </Field>
                  
                  <Field>
                    <Label htmlFor="password">Password</Label>
                    <PasswordInput 
                        id="password"
                        name="password"
                        required 
                        value={passwordValue}
                        onChange={(e) => setPasswordValue(e.target.value)}
                    />
                    
                    {/* Wskaźnik siły hasła */}
                    {passwordValue && (
                      <div className="flex gap-1 mt-2">
                        {[1, 2, 3, 4, 5].map((level) => (
                          <div
                            key={level}
                            className={`h-1.5 w-full rounded-full transition-colors ${
                              strengthScore >= level ? getStrengthColor(strengthScore) : "bg-gray-200"
                            }`}
                          />
                        ))}
                      </div>
                    )}
                    
                    {errors.password && <p className="text-xs text-destructive mt-1">{errors.password}</p>}
                  </Field>
                  
                  <Field>
                    <Label htmlFor="confirm-password">Confirm Password</Label>
                    <PasswordInput 
                        id="confirm-password"
                        name="confirm-password"
                        required 
                    />
                    {errors.confirmPassword && <p className="text-xs text-destructive mt-1">{errors.confirmPassword}</p>}
                  </Field>
                </FieldGroup>
                
                <DialogFooter className="mt-6">
                  <DialogClose asChild>
                    <Button type="button" variant="outline">Cancel</Button>
                  </DialogClose>
                  <Button type="submit">Create User</Button>
                </DialogFooter>
              </form>
            </DialogContent>
        </Dialog>
    </div>
  )
}