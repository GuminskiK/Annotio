import { Button } from "@/components/ui/button"
import { Card, CardTitle, CardContent } from "@/components/ui/card"
import { useState, useEffect } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { getUserProfile } from "@/api/auth/users";
import { useParams } from 'react-router-dom';
export default function Profile() {

    const { id } = useParams();

    const navigate = useNavigate();
    const location = useLocation();
    const isActive = (path: string) => location.pathname.includes(path);
    const [ profile, setProfile] = useState<any>(null);

    const getAvatarSrc = (url: string) => {
        return `${url}?t=${Date.now()}`;
    };
    
    useEffect(() => {
            fetchSessions()
    }, [id]);

    const fetchSessions = async () => {
        if (!id) {
            return; 
        }

        try {
            const response = await getUserProfile(id);
            setProfile(response);
        } catch (error) {
            console.error(error);
        }
    };

    return(
        <div className="w-full max-w-7xl mx-auto h-screen flex justify-center items-center gap-8 p-8 box-border">
            
            <div className="w-[300px] shrink-0 flex flex-col gap-6 h-full py-10">
                <Card className="flex flex-col items-center h-full">
                    <div className="flex flex-col items-center w-full">
                        {profile?.avatar_url ? (
                            <img 
                                src={getAvatarSrc(profile.avatar_url)} 
                                alt={`${profile.username} avatar`} 
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <span className="text-gray-500 text-sm">Brak zdjęcia</span>
                        )}
                        <CardTitle className="text-lg font-semibold mt-5 mb-5">
                            {profile?.username || "Nieznany"}
                        </CardTitle>
                    </div>

                    <CardContent className="flex flex-col gap-2 w-full border-t border-gray-600 p-4">
                        <Button 
                            variant={isActive('settings') ? 'default' : 'outline'} 
                            onClick={() => navigate(`/user/settings/${id}`)}
                        >
                            Settings
                        </Button>
                        <Button 
                            variant={isActive('security') ? 'default' : 'outline'} 
                            onClick={() => navigate(`/user/security/${id}`)}
                        >
                            Security
                        </Button>
                        <Button 
                            variant={isActive('apikeys') ? 'default' : 'outline'} 
                            onClick={() => navigate(`/user/apikeys/${id}`)}
                        >
                            APIKeys
                        </Button>
                        <Button 
                            variant={isActive('preferences') ? 'default' : 'outline'} 
                            onClick={() => navigate(`/user/preferences/${id}`)}
                        >
                            Preferences
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