import { Link } from "react-router-dom";
import { useAppStore } from "@/store/appStore";
import { rooms, currentUser, statusLabel, statusColor } from "@/data/mockData";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Calendar,
  Sparkles,
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Users,
} from "lucide-react";

export default function Dashboard() {
  const { bookings } = useAppStore();
  const today = new Date().toISOString().split("T")[0];

  const myBookings = bookings.filter((b) => b.bookerEmail === currentUser.email);
  const todayBookings = bookings.filter((b) => b.date === today && b.status === "approved");
  const pending = myBookings.filter((b) => b.status === "pending").length;

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* Hero */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-hero p-8 text-primary-foreground shadow-elegant">
        <div className="absolute -top-24 -right-24 size-72 bg-secondary/20 rounded-full blur-3xl" />
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div>
            <div className="text-primary-foreground/80 text-sm mb-2">
              สวัสดีตอนเช้า ☀️
            </div>
            <h1 className="font-display font-bold text-3xl lg:text-4xl mb-2">
              {currentUser.name}
            </h1>
            <p className="text-primary-foreground/80">
              {currentUser.department} · วันนี้มีห้องประชุม {todayBookings.length} รายการ
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3">
            <Button asChild size="lg" className="bg-secondary text-secondary-foreground hover:bg-secondary/90 font-semibold shadow-glow">
              <Link to="/calendar">
                <Calendar className="size-4 mr-2" />
                จองห้องประชุม
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="bg-primary-foreground/10 border-primary-foreground/30 text-primary-foreground hover:bg-primary-foreground/20">
              <Link to="/ai-booking">
                <Sparkles className="size-4 mr-2" />
                จองด้วย AI
              </Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "การจองของฉัน", value: myBookings.length, icon: Calendar, color: "primary" },
          { label: "รออนุมัติ", value: pending, icon: Clock, color: "warning" },
          { label: "ห้องว่างวันนี้", value: rooms.length - todayBookings.length, icon: CheckCircle2, color: "success" },
          { label: "ใช้งานเดือนนี้", value: 24, icon: TrendingUp, color: "secondary" },
        ].map((s) => (
          <Card key={s.label} className="p-5 tu-card border-border">
            <div className="flex items-start justify-between mb-2">
              <span className="text-sm text-muted-foreground">{s.label}</span>
              <s.icon className="size-4 text-muted-foreground" />
            </div>
            <div className="font-display font-bold text-3xl text-foreground">{s.value}</div>
          </Card>
        ))}
      </div>

      {/* Today + Upcoming */}
      <div className="grid lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 p-6 border-border">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="font-display font-bold text-xl text-foreground">การประชุมวันนี้</h2>
              <p className="text-sm text-muted-foreground">รายการที่ได้รับการอนุมัติแล้ว</p>
            </div>
            <Button asChild variant="ghost" size="sm">
              <Link to="/calendar">
                ดูทั้งหมด <ArrowRight className="size-4 ml-1" />
              </Link>
            </Button>
          </div>

          {todayBookings.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Calendar className="size-12 mx-auto mb-3 opacity-30" />
              <p>ยังไม่มีการประชุมในวันนี้</p>
            </div>
          ) : (
            <div className="space-y-3">
              {todayBookings.map((b) => {
                const room = rooms.find((r) => r.id === b.roomId)!;
                return (
                  <div
                    key={b.id}
                    className="flex items-center gap-4 p-4 rounded-lg bg-muted/50 hover:bg-muted transition-smooth border border-border"
                  >
                    <div className="size-14 rounded-lg bg-gradient-warm flex flex-col items-center justify-center text-secondary-foreground shrink-0">
                      <div className="font-display font-bold text-sm leading-none">{b.startTime}</div>
                      <div className="text-[10px] opacity-70">น.</div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-foreground truncate">{b.purpose}</div>
                      <div className="text-xs text-muted-foreground flex items-center gap-3 mt-1">
                        <span>ห้อง {room.code} · {room.name}</span>
                        <span>·</span>
                        <span className="flex items-center gap-1">
                          <Users className="size-3" /> {b.attendees}
                        </span>
                      </div>
                      <div className="text-xs text-muted-foreground mt-0.5">
                        จองโดย: <span className="font-medium text-foreground">{b.bookerName}</span>
                      </div>
                    </div>
                    <Badge variant="outline" className={statusColor[b.status]}>
                      {statusLabel[b.status]}
                    </Badge>
                  </div>
                );
              })}
            </div>
          )}
        </Card>

        <Card className="p-6 border-border bg-gradient-warm">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="size-5 text-secondary-foreground" />
            <h3 className="font-display font-bold text-secondary-foreground">ประกาศ</h3>
          </div>
          <div className="space-y-3 text-sm text-secondary-foreground">
            <div className="p-3 bg-card/40 rounded-lg backdrop-blur">
              <div className="font-semibold mb-1">ปิดปรับปรุงห้อง 401</div>
              <div className="text-xs opacity-80">15-17 พ.ค. นี้ ขออภัยในความไม่สะดวก</div>
            </div>
            <div className="p-3 bg-card/40 rounded-lg backdrop-blur">
              <div className="font-semibold mb-1">เปิดใช้งาน AI Booking</div>
              <div className="text-xs opacity-80">พิมพ์ข้อความบอก AI เพื่อจองห้องอัตโนมัติ</div>
            </div>
            <div className="p-3 bg-card/40 rounded-lg backdrop-blur">
              <div className="font-semibold mb-1">การแจ้งเตือนผ่าน LINE</div>
              <div className="text-xs opacity-80">เพิ่ม LINE @engr-tu เพื่อรับการแจ้งเตือน</div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
