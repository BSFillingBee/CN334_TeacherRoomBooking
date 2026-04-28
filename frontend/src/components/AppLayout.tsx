import { Outlet } from "react-router-dom";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "./AppSidebar";
import { Bell, HelpCircle } from "lucide-react";
import { useAppStore } from "@/store/appStore";

export default function AppLayout() {
  const { role } = useAppStore();

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <AppSidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-16 border-b border-border bg-card/80 backdrop-blur-sm flex items-center justify-between px-4 sticky top-0 z-30">
            <div className="flex items-center gap-3">
              <SidebarTrigger className="text-foreground hover:bg-muted" />
              <div className="hidden md:block">
                <div className="text-xs text-muted-foreground">
                  ปีการศึกษา 2568 · ภาคต้น
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-muted rounded-full text-xs">
                <span className="text-muted-foreground">โหมด:</span>
                <span className="font-semibold text-primary">
                  {role === "admin" ? "ผู้ดูแล" : "เจ้าหน้าที่"}
                </span>
              </div>
              <button className="relative p-2 hover:bg-muted rounded-lg transition-smooth">
                <Bell className="size-5 text-foreground" />
                <span className="absolute top-1.5 right-1.5 size-2 bg-destructive rounded-full" />
              </button>
              <button className="p-2 hover:bg-muted rounded-lg transition-smooth">
                <HelpCircle className="size-5 text-foreground" />
              </button>
            </div>
          </header>
          <main className="flex-1 overflow-auto">
            <Outlet />
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
