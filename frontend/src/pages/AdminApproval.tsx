import { useAppStore } from "@/store/appStore";
import { rooms, statusLabel, statusColor } from "@/data/mockData";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, X, Clock, ShieldCheck, Mail } from "lucide-react";
import { toast } from "sonner";

export default function AdminApproval() {
  const { bookings, approveBooking, rejectBooking } = useAppStore();
  const pending = bookings.filter((b) => b.status === "pending");
  const recent = bookings.filter((b) => b.status !== "pending").slice(0, 8);

  const stats = {
    pending: bookings.filter((b) => b.status === "pending").length,
    approved: bookings.filter((b) => b.status === "approved").length,
    rejected: bookings.filter((b) => b.status === "rejected").length,
    total: bookings.length,
  };

  return (
    <div className="p-6 lg:p-8 max-w-6xl mx-auto animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <div className="size-12 rounded-xl bg-gradient-primary flex items-center justify-center">
          <ShieldCheck className="size-6 text-primary-foreground" />
        </div>
        <div>
          <h1 className="font-display font-bold text-3xl text-foreground">อนุมัติการจอง</h1>
          <p className="text-muted-foreground">โหมดผู้ดูแลระบบ · จัดการคำขอจองห้องประชุม</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[
          { l: "รออนุมัติ", v: stats.pending, c: "warning" },
          { l: "อนุมัติแล้ว", v: stats.approved, c: "success" },
          { l: "ไม่อนุมัติ", v: stats.rejected, c: "destructive" },
          { l: "ทั้งหมด", v: stats.total, c: "primary" },
        ].map((s) => (
          <Card key={s.l} className="p-5 border-border tu-card">
            <div className="text-sm text-muted-foreground">{s.l}</div>
            <div className="font-display font-bold text-3xl text-foreground mt-1">{s.v}</div>
          </Card>
        ))}
      </div>

      <Card className="p-6 border-border mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display font-bold text-xl text-foreground flex items-center gap-2">
            <Clock className="size-5 text-warning" /> รออนุมัติ
            <Badge className="bg-warning/15 text-warning border-warning/30 ml-1">{pending.length}</Badge>
          </h2>
        </div>
        {pending.length === 0 ? (
          <p className="text-center py-8 text-muted-foreground">ไม่มีคำขอที่รออนุมัติ ✨</p>
        ) : (
          <div className="space-y-3">
            {pending.map((b) => {
              const room = rooms.find((r) => r.id === b.roomId)!;
              return (
                <div key={b.id} className="p-4 rounded-xl border-2 border-warning/30 bg-warning/5">
                  <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className="font-mono">{room.code}</Badge>
                        <span className="font-semibold text-foreground">{room.name}</span>
                      </div>
                      <div className="font-medium text-foreground">{b.purpose}</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        👤 {b.bookerName} · {b.department}
                      </div>
                      <div className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                        <Mail className="size-3" /> {b.bookerEmail}
                      </div>
                      <div className="text-xs text-foreground mt-1.5">
                        📅 {b.date} · ⏰ {b.startTime}-{b.endTime} · 👥 {b.attendees} คน
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={async () => { await rejectBooking(b.id); toast.error("ปฏิเสธการจอง", { description: "ส่งอีเมลแจ้งผู้จอง" }); }}
                        variant="outline"
                        className="border-destructive/30 text-destructive hover:bg-destructive hover:text-destructive-foreground"
                      >
                        <X className="size-4 mr-1" /> ไม่อนุมัติ
                      </Button>
                      <Button
                        size="sm"
                        onClick={async () => { await approveBooking(b.id); toast.success("อนุมัติการจอง", { description: "ส่งอีเมลแจ้งผู้จอง" }); }}
                        className="bg-success hover:bg-success/90 text-success-foreground"
                      >
                        <Check className="size-4 mr-1" /> อนุมัติ
                      </Button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      <Card className="p-6 border-border">
        <h2 className="font-display font-bold text-xl text-foreground mb-4">ประวัติล่าสุด</h2>
        <div className="space-y-2">
          {recent.map((b) => {
            const room = rooms.find((r) => r.id === b.roomId)!;
            return (
              <div key={b.id} className="flex items-center gap-4 p-3 rounded-lg hover:bg-muted/50 transition-smooth">
                <Badge variant="outline" className="font-mono shrink-0">{room.code}</Badge>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-foreground truncate">{b.purpose}</div>
                  <div className="text-xs text-muted-foreground">{b.bookerName} · {b.date} {b.startTime}-{b.endTime}</div>
                </div>
                <Badge variant="outline" className={statusColor[b.status]}>{statusLabel[b.status]}</Badge>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
