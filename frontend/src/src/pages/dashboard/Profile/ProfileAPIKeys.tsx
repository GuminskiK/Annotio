import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Dialog, DialogClose, DialogContent, DialogFooter, DialogTrigger, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Field, FieldGroup } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useEffect, useState } from "react"
import type { APIKey } from "@/api/auth/types"
import { getApiKeys, deleteApiKey, createApiKey } from "@/api/auth/apikeys"

export default function ProfileAPIKeys(){
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Stany dla modalu tworzenia
  const [isDialogOpen, setIsDialogOpen] = useState(false); 
  
  // Stany dla modalu wyświetlającego gotowy klucz
  const [isResultDialogOpen, setIsResultDialogOpen] = useState(false);
  const [newlyGeneratedKey, setNewlyGeneratedKey] = useState<string | null>(null);

  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    try {
      const response = await getApiKeys();
      setApiKeys(response);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async (keyId: string) => {
    try {
      await deleteApiKey(keyId);
      setApiKeys((prevApiKeys) => 
        prevApiKeys.filter((apiKey) => apiKey.id !== keyId)
      );
    } catch (error) {
      console.error(error);
    }
  };

const handleCreateApiKey = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    // 1. ZAPISUJEMY REFERENCJĘ DO FORMULARZA PRZED AWAIT
    const form = e.currentTarget; 
    const formData = new FormData(form);
    const name = formData.get("name") as string;

    if (!name || name.trim() === "") return;

    try {
      const response = await createApiKey(name);
      
      // DEBUG: Zerknij w konsolę w przeglądarce po dodaniu klucza!
      // Upewnij się, że obiekt zawiera pole "id". 
      // Jeśli ma format { data: { id: ... } }, musisz użyć response.data
      console.log("Co zwraca backend?", response);
      
      // Założenie: backend faktycznie zwraca płaski obiekt { id, name, key, ... }
      const { key, ...newApiKeyData } = response;
      
      setApiKeys((prevApiKeys) => [...prevApiKeys, newApiKeyData]);
      setNewlyGeneratedKey(key);
      
      setIsDialogOpen(false);
      setIsResultDialogOpen(true);
      
      // 2. UŻYWAMY ZAPISANEJ ZMIENNEJ FORM, NIE e.currentTarget
      form.reset(); 
    } catch (error) {
      console.error(error);
    }
  };

  // Funkcja pomocnicza do kopiowania klucza
  const copyToClipboard = () => {
    if (newlyGeneratedKey) {
      navigator.clipboard.writeText(newlyGeneratedKey);
    }
  };

  return (
    <div className="flex flex-col h-full w-full text-left">
        <div className="text-2xl font-bold mb-4">Your API Keys</div>

        <div className="overflow-x-auto w-full">
          <Table className="w-full">
            <TableHeader>
              <TableRow>
                <TableHead className="w-[150px]">Name</TableHead>
                <TableHead>Key Hint</TableHead>
                <TableHead>Created At</TableHead>
                <TableHead>Last Used</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-4">
                    Ładowanie apikeys...
                  </TableCell>
                </TableRow>
              ) : apiKeys.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-4">
                    Brak aktywnych apikeys.
                  </TableCell>
                </TableRow>
              ) : (
                apiKeys.map((apiKey) => (
                  <TableRow key={apiKey.id}>
                    <TableCell className="font-medium">{apiKey.name}</TableCell>
                    <TableCell className="font-mono text-xs">{apiKey.key_hint}</TableCell>
                    <TableCell>{new Date(apiKey.created_at).toLocaleString()}</TableCell>
                    <TableCell>{apiKey.last_used_at ? new Date(apiKey.last_used_at).toLocaleString() : "Nigdy"}</TableCell>
                    <TableCell className="text-right">
                      <Button 
                        variant="outline"
                        size="sm"
                        onClick={() => handleLogout(apiKey.id)}
                      >
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
        
        {/* Modal TWORZENIA klucza */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button className="w-[200px] mt-5" variant="outline">Create API Key</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-sm">
            <form onSubmit={handleCreateApiKey}>
              <DialogHeader>
                <DialogTitle>Create API Key</DialogTitle>
              </DialogHeader>
              <FieldGroup className="py-4">
                <Field>
                  <Label htmlFor="name-1">Name</Label>
                  <Input id="name-1" name="name" placeholder="np. Mój skrypt pythona" required />
                </Field>
              </FieldGroup>
              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="outline" type="button">Cancel</Button>
                </DialogClose>
                <Button type="submit">Create API Key</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Modal WYŚWIETLAJĄCY wygenerowany klucz */}
        <Dialog 
          open={isResultDialogOpen} 
          onOpenChange={(open) => {
            setIsResultDialogOpen(open);
            if (!open) setNewlyGeneratedKey(null); // Czyścimy klucz z pamięci przy zamknięciu
          }}
        >
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Klucz API wygenerowany</DialogTitle>
            </DialogHeader>
            <div className="flex flex-col space-y-4">
              <p className="text-sm font-medium text-red-500 my-3">
                Proszę skopiuj i zapisz ten klucz w bezpiecznym miejscu. Ze względów bezpieczeństwa nie będziesz mógł zobaczyć go ponownie!
              </p>
              <div className="flex items-center space-x-2 my-3">
                <Input 
                  readOnly 
                  value={newlyGeneratedKey || ""} 
                  className="font-mono text-sm" 
                />
                <Button type="button" onClick={copyToClipboard} variant="default">
                  Copy
                </Button>
              </div>
            </div>
            <DialogFooter className="py-2">
              <Button type="button" onClick={() => {
                setIsResultDialogOpen(false);
                setNewlyGeneratedKey(null);
              }}>
                Close & I have saved it
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
    </div>
  )
}