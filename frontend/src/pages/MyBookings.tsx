import { useState } from "react";
import { useAppStore } from "@/store/appStore";
import { rooms, currentUser, statusLabel, statusColor } from "@/data/mockData";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Calendar, Clock, Users, X, FileText } from "lucide-react";
import { toast } from "sonner";
import { Link } from "react-router-dom";

export default function MyBookings() {
  const { bookings, cancelBooking } = useAppStore();
  const [filter, setFilter] = useState<"all" | "pending" | "approved" | "cancelled">("all");
  const [cancelId, setCancelId] = useState<string | null>(null);

  const my = bookings.filter((b) => b.bookerEmail === currentUser.email);
  const filtered = filter === "all" ? my : my.filter((b) => b.status === filter);

  const handleCancel = async () => {
    if (!cancelId) return;
    await cancelBooking(cancelId);
    toast.success("ยกเลิกการจองสำเร็จ", { description: "ส่งอีเมลแจ้งเตือนเรียบร้อย" });
    setCancelId(null);
  };

  const counts = {
    all: my.length,
    pending: my.filter((b) => b.status === "pending").length,
    approved: my.filter((b) => b.status === "approved").length,
    cancelled: my.filter((b) => b.status === "cancelled").length,
  };

  return (
    <div className="p-6 lg:p-8 max-w-6xl mx-auto animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="font-display font-bold text-3xl text-foreground">การจองของฉัน</h1>
          <p className="text-muted-foreground">{my.length} รายการทั้งหมด</p>
        </div>
        <Button asChild className="bg-gradient-primary text-primary-foreground shadow-elegant">
          <Link to="/book">+ จองห้องใหม่</Link>
        </Button>
      </div>

      <div className="flex gap-2 mb-5 overflow-x-auto pb-1">
        {([
          { v: "all", l: "ทั้งหมด" },
          { v: "pending", l: "รออนุมัติ" },
          { v: "approved", l: "อนุมัติแล้ว" },
          { v: "cancelled", l: "ยกเลิก" },
        ] as const).map((o) => (
          <Button
            key={o.v}
            variant={filter === o.v ? "default" : "outline"}
            onClick={() => setFilter(o.v)}
            className={filter === o.v ? "bg-gradient-primary text-primary-foreground" : ""}
            size="sm"
          >
            {o.l} <Badge variant="secondary" className="ml-2">{counts[o.v]}</Badge>
          </Button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <Card className="p-12 text-center border-border">
          <FileText className="size-12 mx-auto text-muted-foreground/50 mb-3" />
          <p className="text-muted-foreground">ยังไม่มีการจองในหมวดนี้</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {filtered.map((b) => {
            const room = rooms.find((r) => r.id === b.roomId)!;
            return (
              <Card key={b.id} className="p-5 border-border tu-card">
                <div className="flex flex-col md:flex-row md:items-center gap-4">
                  <img
                    src={room.image}
                    alt={room.name}
                    className="size-20 md:size-16 rounded-lg object-cover shrink-0"
                    loading="lazy"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge className="bg-secondary/20 text-secondary-foreground border-secondary/40 font-mono text-[10px]">
                        {room.code}
                      </Badge>
                      <Badge variant="outline" className={statusColor[b.status]}>
                        {statusLabel[b.status]}
                      </Badge>
                    </div>
                    <h3 className="font-semibold text-foreground">{b.purpose}</h3>
                    <div className="text-xs text-muted-foreground mt-0.5">{room.name}</div>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground mt-2">
                      <span className="flex items-center gap-1"><Calendar className="size-3" /> {b.date}</span>
                      <span className="flex items-center gap-1"><Clock className="size-3" /> {b.startTime}-{b.endTime}</span>
                      <span className="flex items-center gap-1"><Users className="size-3" /> {b.attendees} คน</span>
                    </div>
                  </div>
                  {(b.status === "pending" || b.status === "approved") && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCancelId(b.id)}
                      className="border-destructive/30 text-destructive hover:bg-destructive hover:text-destructive-foreground transition-smooth"
                    >
                      <X className="size-4 mr-1" /> ยกเลิกการจอง
                    </Button>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}

      <AlertDialog open={!!cancelId} onOpenChange={(o) => !o && setCancelId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>ยืนยันการยกเลิก?</AlertDialogTitle>
            <AlertDialogDescription>
              การยกเลิกจะส่งอีเมลแจ้งเตือนผู้ดูแลระบบ และไม่สามารถกู้คืนได้
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>ไม่ใช่</AlertDialogCancel>
            <AlertDialogAction onClick={handleCancel} className="bg-destructive hover:bg-destructive/90">
              ยืนยันยกเลิก
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
