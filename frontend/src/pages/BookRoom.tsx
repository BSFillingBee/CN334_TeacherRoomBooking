import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { rooms, currentUser } from "@/data/mockData";
import { useAppStore } from "@/store/appStore";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Calendar, Clock, Users, CheckCircle2, AlertTriangle } from "lucide-react";
import { format } from "date-fns";

const TIME_SLOTS = ["08:00","09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00"];

export default function BookRoom() {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const { bookings, addBooking } = useAppStore();

  const [roomId, setRoomId] = useState(params.get("roomId") || rooms[0].id);
  const [date, setDate] = useState(params.get("date") || format(new Date(), "yyyy-MM-dd"));
  const [start, setStart] = useState("09:00");
  const [end, setEnd] = useState("11:00");
  const [purpose, setPurpose] = useState("");
  const [attendees, setAttendees] = useState(8);

  const room = rooms.find((r) => r.id === roomId)!;

  // conflict check
  const conflicts = bookings.filter(
    (b) =>
      b.roomId === roomId &&
      b.date === date &&
      b.status !== "cancelled" &&
      !(end <= b.startTime || start >= b.endTime)
  );

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (conflicts.length > 0) {
      toast.error("ไม่สามารถจองได้", { description: "มีการจองในช่วงเวลานี้แล้ว" });
      return;
    }
    if (!purpose.trim()) {
      toast.error("กรุณาระบุวัตถุประสงค์");
      return;
    }
    await addBooking({
      roomId, date, startTime: start, endTime: end,
      purpose, attendees,
    });
    toast.success("ส่งคำขอจองสำเร็จ", {
      description: "ระบบส่งอีเมลแจ้งเตือนเรียบร้อย รออนุมัติจากผู้ดูแล",
    });
    nav("/my-bookings");
  };

  return (
    <div className="p-6 lg:p-8 max-w-5xl mx-auto animate-fade-in">
      <div className="mb-6">
        <h1 className="font-display font-bold text-3xl text-foreground">จองห้องประชุม</h1>
        <p className="text-muted-foreground">กรอกข้อมูลให้ครบถ้วน · ระบบจะตรวจสอบการจองซ้ำอัตโนมัติ</p>
      </div>

      <form onSubmit={submit} className="grid lg:grid-cols-[1fr_360px] gap-6">
        <Card className="p-6 border-border space-y-5">
          <div className="space-y-2">
            <Label>เลือกห้องประชุม</Label>
            <div className="grid sm:grid-cols-2 gap-3">
              {rooms.map((r) => (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => setRoomId(r.id)}
                  className={`p-4 rounded-xl border-2 text-left transition-smooth ${
                    roomId === r.id
                      ? "border-primary bg-primary/5 shadow-card"
                      : "border-border hover:border-primary/40"
                  }`}
                >
                  <div className="flex items-start justify-between mb-1">
                    <Badge variant="outline" className="bg-secondary/20 border-secondary/40 text-secondary-foreground text-[10px]">
                      {r.code}
                    </Badge>
                    {roomId === r.id && <CheckCircle2 className="size-4 text-primary" />}
                  </div>
                  <div className="font-semibold text-sm text-foreground">{r.name}</div>
                  <div className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <Users className="size-3" /> {r.capacity} คน
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="grid sm:grid-cols-3 gap-4">
            <div className="space-y-2 sm:col-span-1">
              <Label htmlFor="date">วันที่</Label>
              <Input id="date" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>เริ่ม</Label>
              <select
                value={start}
                onChange={(e) => setStart(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
              >
                {TIME_SLOTS.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="space-y-2">
              <Label>สิ้นสุด</Label>
              <select
                value={end}
                onChange={(e) => setEnd(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
              >
                {TIME_SLOTS.filter((t) => t > start).map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="att">จำนวนผู้เข้าร่วม</Label>
            <Input id="att" type="number" min={1} max={room.capacity}
              value={attendees} onChange={(e) => setAttendees(Number(e.target.value))} />
            {attendees > room.capacity && (
              <p className="text-xs text-destructive">เกินความจุห้อง ({room.capacity} คน)</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="p">วัตถุประสงค์การประชุม</Label>
            <Textarea id="p" rows={3} placeholder="เช่น ประชุมคณะกรรมการบริหารหลักสูตร"
              value={purpose} onChange={(e) => setPurpose(e.target.value)} />
          </div>

          {conflicts.length > 0 && (
            <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/30 flex gap-3">
              <AlertTriangle className="size-5 text-destructive shrink-0 mt-0.5" />
              <div className="text-sm">
                <div className="font-semibold text-destructive mb-1">มีการจองซ้ำในช่วงเวลานี้</div>
                {conflicts.map((c) => (
                  <div key={c.id} className="text-xs text-foreground">
                    · {c.startTime}-{c.endTime} โดย {c.bookerName} ({c.purpose})
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>

        {/* Summary */}
        <Card className="p-6 border-border h-fit sticky top-24 bg-gradient-to-b from-accent/20 to-card">
          <h3 className="font-display font-bold text-lg text-foreground mb-4">สรุปการจอง</h3>
          <div className="space-y-3 text-sm">
            <div>
              <div className="text-xs text-muted-foreground mb-0.5">ห้อง</div>
              <div className="font-semibold text-foreground">{room.code} · {room.name}</div>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="size-4 text-primary" />
              <span className="text-foreground">{date}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="size-4 text-primary" />
              <span className="text-foreground">{start} - {end} น.</span>
            </div>
            <div className="flex items-center gap-2">
              <Users className="size-4 text-primary" />
              <span className="text-foreground">{attendees} คน</span>
            </div>
            <div className="pt-3 border-t border-border">
              <div className="text-xs text-muted-foreground mb-0.5">ผู้จอง</div>
              <div className="font-semibold text-foreground">{currentUser.name}</div>
              <div className="text-xs text-muted-foreground">{currentUser.department}</div>
            </div>
          </div>
          <Button type="submit" className="w-full mt-5 h-11 bg-gradient-primary text-primary-foreground shadow-elegant">
            ส่งคำขอจอง
          </Button>
          <p className="text-[10px] text-muted-foreground text-center mt-2">
            แจ้งเตือนผ่านอีเมล{" "}
            <span className="font-semibold">และ LINE</span> เมื่ออนุมัติ
          </p>
        </Card>
      </form>
    </div>
  );
}
