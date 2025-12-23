import { Link, Outlet, useLocation } from "react-router-dom"
import { Briefcase, Search, Settings } from "lucide-react"
import { cn } from "@/lib/utils"

export default function Layout() {
    const location = useLocation()

    const navItems = [
        { href: "/", label: "Home", icon: Briefcase },
        { href: "/preferences", label: "Preferences", icon: Settings },
        { href: "/dashboard", label: "Dashboard", icon: Search },
    ]

    return (
        <div className="min-h-screen bg-background font-sans antialiased text-foreground flex flex-col">
            <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="container flex h-14 max-w-screen-2xl items-center">
                    <div className="mr-4 hidden md:flex">
                        <Link to="/" className="mr-6 flex items-center space-x-2">
                            <span className="hidden font-bold sm:inline-block">
                                AI Job Hunter
                            </span>
                        </Link>
                        <nav className="flex items-center gap-6 text-sm">
                            {navItems.map((item) => (
                                <Link
                                    key={item.href}
                                    to={item.href}
                                    className={cn(
                                        "transition-colors hover:text-foreground/80",
                                        location.pathname === item.href
                                            ? "text-foreground font-medium"
                                            : "text-foreground/60"
                                    )}
                                >
                                    {item.label}
                                </Link>
                            ))}
                        </nav>
                    </div>
                </div>
            </header>
            <main className="flex-1">
                <div className="container py-6 md:py-10 max-w-screen-2xl">
                    <Outlet />
                </div>
            </main>
            <footer className="py-6 md:px-8 md:py-0">
                <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
                    <p className="text-balance text-center text-sm leading-loose text-muted-foreground md:text-left">
                        Built with ❤️ using Local LLMs.
                    </p>
                </div>
            </footer>
        </div>
    )
}
