import { Button } from "@/components/ui/button"
import { Card, CardTitle, CardContent } from "@/components/ui/card"
import { useState, useRef } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { getUserProfile, uploadAvatarFile } from "@/api/auth/users"; 
import { useAuth } from '@/context/AuthContext'

export default function Profile() {
    const { user: profile, updateUser } = useAuth();
    const [isUploading, setIsUploading] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const navigate = useNavigate();
    const location = useLocation();
    const isActive = (path: string) => location.pathname.includes(path);

    const handleAvatarClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setIsUploading(true);
        try {
            const data = await uploadAvatarFile(file);
            console.log("Wgrywanie zakończone sukcesem:", data);
            
            const get_data = await getUserProfile("me");
            updateUser(get_data)

        } catch (error) {
            console.error("Błąd podczas wgrywania:", error);
        } finally {
            setIsUploading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    }

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
                            className={`w-32 h-32 bg-gray-300 mt-10 rounded-full overflow-hidden cursor-pointer hover:opacity-80 transition-opacity flex items-center justify-center relative ${isUploading ? 'opacity-50' : ''}`}
                            onClick={handleAvatarClick}
                            title="Kliknij, aby zmienić awatar"
                        >
                            {isUploading ? (
                                <span className="text-gray-700 text-sm font-semibold z-10 absolute">Wgrywanie...</span>
                            ) : null}

                            {profile?.avatar_url ? (
                                <img 
                                    src={getAvatarSrc(profile.avatar_url)} 
                                    alt={`${profile.username} avatar`} 
                                    className="w-full h-full object-cover"
                                />
                            ) : (
                                !isUploading && <span className="text-gray-500 text-sm">Brak zdjęcia</span>
                            )}
                        </div>
                        
                        <input 
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileChange}
                            accept="image/*"
                            className="hidden"
                        />

                        {/* Nazwa użytkownika */}
                        
                        <CardTitle className="text-lg font-semibold mt-5 mb-5">
                            {profile?.username || "Nieznany"}
                        </CardTitle>
                    </div>

                    <CardContent className="flex flex-col gap-2 w-full border-t border-gray-600 p-4">
                        <Button 
                            variant={isActive('settings') ? 'default' : 'outline'} 
                            onClick={() => navigate('/profile/settings')}
                        >
                            Settings
                        </Button>
                        <Button 
                            variant={isActive('security') ? 'default' : 'outline'} 
                            onClick={() => navigate('/profile/security')}
                        >
                            Security
                        </Button>
                        <Button 
                            variant={isActive('apikeys') ? 'default' : 'outline'} 
                            onClick={() => navigate('/profile/apikeys')}
                        >
                            APIKeys
                        </Button>
                        <Button 
                            variant={isActive('preferences') ? 'default' : 'outline'} 
                            onClick={() => navigate('/profile/preferences')}
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