import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useNavigate } from 'react-router-dom';
import { useAuth } from "@/context/AuthContext";
import { LogOut, ShieldAlert, User } from "lucide-react";


export default function Dashboard() {
    const navigate = useNavigate();
    const { logout, user: profile } = useAuth(); 
    // Prosta symulacja uprawnień 
    const isAdmin = profile?.is_superuser === true || false; 

    const handleLogout = async () => {
        try {
            const success = await logout();
            if (success) navigate('/');
        } catch (error) {
            console.error('Błąd podczas wylogowywania:', error);
        }
    };
    
    const getAvatarSrc = (url: string) => url;

    return (
        <div className="w-full max-w-4xl mx-auto h-screen flex justify-center items-center p-8 box-border">
            <div className="w-full flex flex-col gap-6">
                
                {/* Cienki pasek górny z Avatarem */}
                <Card className="flex flex-row items-center justify-between p-3 shadow-sm shrink-0">
                    {/* Sekcja Użytkownika */}
                    <div 
                        className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
                        onClick={() => navigate('/profile')}
                        title="Przejdź do profilu"
                    >
                        <div className="w-9 h-9 bg-gray-300 rounded-full overflow-hidden flex items-center justify-center border border-gray-600">
                            {profile?.avatar_url ? (
                                <img 
                                    src={getAvatarSrc(profile.avatar_url)} 
                                    alt="Avatar" 
                                    className="w-full h-full object-cover"
                                />
                            ) : (
                                <User className="w-5 h-5 text-gray-500" />
                            )}
                        </div>
                        <span className="font-semibold text-sm">
                            {profile?.username || "Użytkownik"}
                        </span>
                    </div>

                    {/* Przyciski Akcji */}
                    <div className="flex items-center gap-1"> 
                        {isAdmin && (
                            <Button variant="ghost" size="sm" onClick={() => navigate('/admin')} className="h-8">
                                <ShieldAlert className="w-4 h-4 mr-2" />
                                <span className="hidden sm:inline">Admin</span>
                            </Button>
                        )}
                        <Button variant="ghost" size="sm" onClick={handleLogout} className="h-8 text-rose-500 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950">
                            <LogOut className="w-4 h-4 sm:mr-2" />
                            <span className="hidden sm:inline">Wyloguj</span>
                        </Button>
                    </div>
                </Card>

                <div className="flex-1 rounded-xl border bg-card p-8 text-center text-muted-foreground">
                    Panel Annotio jest gotowy. Moduły z poprzedniego projektu nie są jeszcze podłączone.
                </div>
            </div>
        </div>
    );
}