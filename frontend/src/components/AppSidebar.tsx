import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Calendar,
  DoorOpen,
  ClipboardList,
  Sparkles,
  Map,
  ShieldCheck,
  BarChart3,
  Settings,
  LogOut,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
  useSidebar,
} from "@/components/ui/sidebar";
import { useAppStore } from "@/store/appStore";
import { currentUser } from "@/data/mockData";
import tseLogo from "@/assets/tse-logo.png";

const staffItems = [
  { title: "แดชบอร์ด", url: "/", icon: LayoutDashboard },
  { title: "ปฏิทินห้องประชุม", url: "/calendar", icon: Calendar },
  { title: "ห้องประชุมทั้งหมด", url: "/rooms", icon: DoorOpen },
  { title: "แผนผังชั้น 4", url: "/map", icon: Map },
  { title: "จองห้องด้วย AI", url: "/ai-booking", icon: Sparkles },
  { title: "การจองของฉัน", url: "/my-bookings", icon: ClipboardList },
];

const adminItems = [
  { title: "อนุมัติการจอง", url: "/admin", icon: ShieldCheck },
  { title: "จัดการห้องประชุม", url: "/admin/rooms", icon: DoorOpen },
  { title: "รายงานการใช้งาน", url: "/admin/reports", icon: BarChart3 },
  { title: "ตั้งค่าระบบ", url: "/admin/settings", icon: Settings },
];

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const { pathname } = useLocation();
  const { role, logout } = useAppStore();

  const isActive = (path: string) =>
    path === "/" ? pathname === "/" : pathname.startsWith(path);

  const items = role === "admin" ? adminItems : staffItems;
  const groupLabel = role === "admin" ? "เมนูผู้ดูแลระบบ" : "เมนูเจ้าหน้าที่";

  return (
    <Sidebar collapsible="icon" className="border-r border-sidebar-border">
      <SidebarHeader className="p-4 border-b border-sidebar-border">
        <NavLink to="/" className="flex items-center gap-3">
          <div className="size-10 rounded-lg bg-white flex items-center justify-center shrink-0 shadow-glow overflow-hidden p-1">
            <img src={tseLogo} alt="TSE" className="size-full object-contain" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <div className="font-display font-bold text-sidebar-foreground text-sm leading-tight">
                ระบบจองห้องประชุม
              </div>
              <div className="text-[11px] text-sidebar-foreground/70 leading-tight">
                คณะวิศวกรรมศาสตร์ มธ.
              </div>
            </div>
          )}
        </NavLink>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          {!collapsed && (
            <SidebarGroupLabel className="text-sidebar-foreground/60 font-medium">
              {groupLabel}
            </SidebarGroupLabel>
          )}
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.url}>
                  <SidebarMenuButton
                    asChild
                    isActive={isActive(item.url)}
                    className="data-[active=true]:bg-sidebar-primary data-[active=true]:text-sidebar-primary-foreground data-[active=true]:font-semibold hover:bg-sidebar-accent transition-smooth"
                  >
                    <NavLink to={item.url}>
                      <item.icon className="size-4 shrink-0" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border p-3">
        {!collapsed ? (
          <div className="flex items-center gap-3">
            <div className="size-9 rounded-full bg-sidebar-primary text-sidebar-primary-foreground flex items-center justify-center text-xs font-bold shrink-0">
              {currentUser.avatar}
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-xs font-semibold text-sidebar-foreground truncate">
                {currentUser.name}
              </div>
              <div className="text-[10px] text-sidebar-foreground/60 truncate">
                {role === "admin" ? "ผู้ดูแลระบบ" : "เจ้าหน้าที่"}
              </div>
            </div>
            <button
              onClick={logout}
              className="text-sidebar-foreground/70 hover:text-sidebar-foreground p-1.5 hover:bg-sidebar-accent rounded-md transition-smooth"
              title="ออกจากระบบ"
            >
              <LogOut className="size-4" />
            </button>
          </div>
        ) : (
          <div className="size-9 rounded-full bg-sidebar-primary text-sidebar-primary-foreground flex items-center justify-center text-xs font-bold mx-auto">
            {currentUser.avatar}
          </div>
        )}
      </SidebarFooter>
    </Sidebar>
  );
}
