import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { useEffect, useState } from "react"
import type { APIKey } from "@/api/auth/types"
import { getUserApiKeys, deleteApiKey } from "@/api/auth/apikeys"
import { useParams } from 'react-router-dom';

export default function ProfileAPIKeys(){
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { id } = useParams();

  useEffect(() => {
    fetchApiKeys();
  }, [id]);

  const fetchApiKeys = async () => {
    if (!id) {
      setIsLoading(false);
      return; 
    }

    try {
      const response = await getUserApiKeys(id);
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
        
    </div>
  )
}