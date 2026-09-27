"use client" // Wymagane w Next.js App Router dla useState/useEffect

import { useState, useEffect } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import type { Session } from "@/api/auth/types"
import {getSessions, deleteSession} from "@/api/auth/sessions"

export default function ProfileSecurity() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchSessions()
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await getSessions();
      setSessions(response);
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async (sessionId: string) => {
    try {
      await deleteSession(sessionId);

      setSessions((prevSessions) => 
        prevSessions.filter((session) => session.session_id !== sessionId)
      );
    } catch (error) {
      console.error(error);
    }
  };

return (
    // Usunąłem m-10, bo komponent jest już wewnątrz <Card> z paddingiem, więc lepiej użyć pełnej szerokości
    <div className="flex flex-col h-full w-full text-left">
      <div className="text-2xl font-bold mb-4">Your sessions</div>

      {/* Kontener pozwalający na przewijanie tabeli na małych ekranach zamiast psucia layoutu */}
      <div className="overflow-x-auto w-full">
        <Table className="w-full">
          <TableHeader>
            <TableRow>
              <TableHead className="w-[80px]">ID Sesji</TableHead>
              <TableHead className="w-[150px]">Created</TableHead> {/* BRAKUJĄCY NAGŁÓWEK */}
              <TableHead className="w-1/3">Device</TableHead> {/* Zarezerwowanie max 1/3 szerokości */}
              <TableHead>IP Address</TableHead>
              <TableHead className="text-right">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-4"> {/* Zmieniono colSpan na 5 */}
                  Ładowanie sesji...
                </TableCell>
              </TableRow>
            ) : sessions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-4">
                  Brak aktywnych sesji.
                </TableCell>
              </TableRow>
            ) : (
              sessions.map((session) => (
                <TableRow key={session.session_id}>
                  <TableCell className="font-medium">{session.session_id}</TableCell>
                  <TableCell className="whitespace-nowrap">
                    {new Date(session.created_at).toLocaleString()}
                  </TableCell>
                  
                  {/* KLUCZOWA ZMIANA: max-width, break-words i mniejszy tekst dla długich danych urządzenia */}
                  <TableCell className="max-w-[150px] sm:max-w-[250px] whitespace-normal break-words text-xs text-gray-500">
                    {session.device}
                  </TableCell>
                  
                  <TableCell className="whitespace-nowrap">{session.ip}</TableCell>
                  <TableCell className="text-right">
                    <Button 
                      variant="outline"
                      size="sm"
                      onClick={() => handleLogout(session.session_id)}
                    >
                      Logout
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