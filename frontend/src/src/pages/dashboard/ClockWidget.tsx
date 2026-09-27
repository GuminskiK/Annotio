import { Card, CardContent} from "@/components/ui/card";
import { useState, useEffect} from "react";

export default function ClockWidget() {

    const [time, setTime] = useState(new Date());
    useEffect(() => {
        const timer = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    return (             
        <Card className="text-white border-none shadow-sm shrink-0">
            <CardContent className="p-3 flex flex-col items-center justify-center">
                <div className="text-5xl font-bold tracking-wider">
                    {time.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' })}
                </div>
                <div className="text-xs font-medium mt-1 opacity-80">
                    {time.toLocaleDateString('pl-PL', { weekday: 'long', day: 'numeric', month: 'long' })}
                </div>
            </CardContent>
        </Card>
    );
}