import { Button } from "@/components/ui/button.tsx"

export default function Hello() {

    return (
        <div className="flex flex-col justify-center items-center min-h-screen ">
            <div className="text-5xl font-bold text-center">Welcome to HomeOS</div>
            <Button className="mt-10 px-4 py-5" onClick={() => window.location.href = '/login'}>
                Go to Login
            </Button>
        </div>
    )
}