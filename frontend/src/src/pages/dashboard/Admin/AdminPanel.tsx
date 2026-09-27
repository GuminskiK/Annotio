import { Button } from "@/components/ui/button.tsx"
import { Card, CardTitle, CardContent} from "@/components/ui/card"
import { useAuth } from "@/context/AuthContext";
import { Outlet, useNavigate, useLocation } from "react-router-dom";

export default function AdminPanel() {
    const { user: profile } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const isActive = (path: string) => location.pathname.includes(path);


    const getAvatarSrc = (url: string) => {
        return `${url}?t=${Date.now()}`;
    };

    return(
        <div className="w-full max-w-7xl mx-auto h-screen flex justify-center items-center gap-8 p-8 box-border">
            
            {/* LEWY PANEL - SZTYWNA SZEROKOŚĆ (np. 300px) */}
            {/* shrink-0 zapobiega zgniataniu panelu przez sąsiednie elementy */}
            <div className="w-[300px] shrink-0 flex flex-col gap-6 h-full py-10">
                <Card className="flex flex-col items-center h-full">
                    <div className="flex flex-col items-center w-full">
                                                <div 
                            className={`w-32 h-32 bg-gray-300 mt-10 rounded-full overflow-hidden cursor-pointer hover:opacity-80 transition-opacity flex items-center justify-center relative`}
                        >

                            {profile?.avatar_url ? (
                                <img 
                                    src={getAvatarSrc(profile.avatar_url)} 
                                    alt={`${profile.username} avatar`} 
                                    className="w-full h-full object-cover"
                                />
                            ) : (
                                <span className="text-gray-500 text-sm">Brak zdjęcia</span>
                            )}
                        </div>

                        {/* Nazwa użytkownika */}
                        
                        <CardTitle className="text-lg font-semibold mt-5 mb-5">
                            {profile?.username || "Nieznany"}
                        </CardTitle>
                    </div>

                    <CardContent className="flex flex-col gap-2 w-full border-t border-gray-600 p-4">
                        <Button 
                            variant={isActive('manage_users') ? 'default' : 'outline'} 
                            onClick={() => navigate('/admin/manage_users')}
                        >
                            Manage Users
                        </Button>
                        <Button 
                            variant={isActive('logs') ? 'default' : 'outline'} 
                            onClick={() => navigate('/admin/logs')}
                        >
                            Logs
                        </Button>
                    </CardContent>
                </Card>
            </div>
            
            <div className="flex-1 min-w-0 flex flex-col gap-6 h-full py-10">
                <Card className="flex flex-col h-full p-6 overflow-hidden">
                    <Outlet />
                </Card> 
            </div>
        </div>
    )
}