import { Button } from "@/components/ui/button.tsx"

export default function Hello() {

    return (
        <div className="flex flex-col justify-center items-center min-h-screen ">
            <div className="text-5xl font-bold text-center">Welcome to Annotio</div>
            <div className="flex flex-row gap-4 mt-8">            
                <Button className="px-4 py-5" onClick={() => window.location.href = '/login'}>
                Go to Login
                </Button>
                <Button className="px-4 py-5" onClick={() => window.location.href = '/register'}>
                    Go to Register
                </Button>
            </div>

        </div>
    )
}