import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAppStore } from "@/store/appStore";
import { rooms, statusColor, statusLabel } from "@/data/mockData";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChevronLeft, ChevronRight, Plus } from "lucide-react";
import {
  format,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  addDays,
  addMonths,
  isSameMonth,
  isSameDay,
  isToday,
} from "date-fns";
import { th } from "date-fns/locale";

export default function CalendarPage() {
  const nav = useNavigate();
  const { bookings } = useAppStore();
  const [current, setCurrent] = useState(new Date());
  const [selected, setSelected] = useState<Date | null>(new Date());

  const monthStart = startOfMonth(current);
  const monthEnd = endOfMonth(current);
  const startDate = startOfWeek(monthStart, { weekStartsOn: 0 });
  const endDate = endOfWeek(monthEnd, { weekStartsOn: 0 });

  const days: Date[] = [];
  let day = startDate;
  while (day <= endDate) {
    days.push(day);
    day = addDays(day, 1);
  }

  const getBookingsForDay = (d: Date) =>
    bookings.filter((b) => b.date === format(d, "yyyy-MM-dd") && b.status !== "cancelled");

  const selectedBookings = selected ? getBookingsForDay(selected) : [];

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="font-display font-bold text-3xl text-foreground">ปฏิทินห้องประชุม</h1>
          <p className="text-muted-foreground">ดูห้องว่างและคลิกวันที่เพื่อจอง</p>
        </div>
        <Button
          onClick={() => nav("/book")}
          className="bg-gradient-primary hover:opacity-95 text-primary-foreground font-semibold shadow-elegant"
        >
          <Plus className="size-4 mr-2" /> จองห้องใหม่
        </Button>
      </div>

      <div className="grid lg:grid-cols-[1fr_360px] gap-6">
        <Card className="p-6 border-border">
          {/* Header */}
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-display font-bold text-2xl text-foreground">
              {format(current, "MMMM yyyy", { locale: th })}
            </h2>
            <div className="flex items-center gap-2">
              <Button
                size="icon"
                variant="outline"
                onClick={() => setCurrent(addMonths(current, -1))}
                className="border-2 border-primary/30 hover:bg-primary hover:text-primary-foreground hover:border-primary transition-smooth"
                aria-label="เดือนก่อนหน้า"
              >
                <ChevronLeft className="size-5" />
              </Button>
              <Button
                variant="outline"
                onClick={() => { setCurrent(new Date()); setSelected(new Date()); }}
                className="border-2"
              >
                วันนี้
              </Button>
              <Button
                size="icon"
                variant="outline"
                onClick={() => setCurrent(addMonths(current, 1))}
                className="border-2 border-primary/30 hover:bg-primary hover:text-primary-foreground hover:border-primary transition-smooth"
                aria-label="เดือนถัดไป"
              >
                <ChevronRight className="size-5" />
              </Button>
            </div>
          </div>

          {/* Day labels */}
          <div className="grid grid-cols-7 gap-2 mb-2">
            {["อา", "จ", "อ", "พ", "พฤ", "ศ", "ส"].map((d, i) => (
              <div
                key={d}
                className={`text-center text-xs font-semibold py-2 ${
                  i === 0 ? "text-destructive" : "text-muted-foreground"
                }`}
              >
                {d}
              </div>
            ))}
          </div>

          {/* Days */}
          <div className="grid grid-cols-7 gap-2">
            {days.map((d) => {
              const dayBookings = getBookingsForDay(d);
              const isSel = selected && isSameDay(d, selected);
              const inMonth = isSameMonth(d, current);
              const today = isToday(d);

              return (
                <button
                  key={d.toISOString()}
                  onClick={() => setSelected(d)}
                  className={`
                    aspect-square min-h-[70px] p-2 rounded-lg border-2 text-left transition-smooth relative
                    ${isSel ? "border-primary bg-primary/5 shadow-card" : "border-transparent hover:border-border"}
                    ${!inMonth ? "opacity-30" : ""}
                    ${today && !isSel ? "bg-secondary/20 border-secondary" : ""}
                  `}
                >
                  <div className={`text-sm font-semibold ${today ? "text-primary" : "text-foreground"}`}>
                    {format(d, "d")}
                  </div>
                  {dayBookings.length > 0 && (
                    <div className="absolute bottom-1.5 left-1.5 right-1.5 space-y-0.5">
                      {dayBookings.slice(0, 2).map((b) => {
                        const room = rooms.find((r) => r.id === b.roomId)!;
                        return (
                          <div
                            key={b.id}
                            className={`text-[9px] truncate px-1 py-0.5 rounded ${
                              b.status === "approved"
                                ? "bg-success/20 text-success"
                                : "bg-warning/20 text-warning"
                            }`}
                          >
                            {b.startTime} {room.code}
                          </div>
                        );
                      })}
                      {dayBookings.length > 2 && (
                        <div className="text-[9px] text-muted-foreground font-medium">
                          +{dayBookings.length - 2} เพิ่มเติม
                        </div>
                      )}
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Legend */}
          <div className="flex items-center gap-4 mt-5 pt-5 border-t border-border text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <span className="size-3 rounded bg-success/30 border border-success" />
              อนุมัติแล้ว
            </div>
            <div className="flex items-center gap-1.5">
              <span className="size-3 rounded bg-warning/30 border border-warning" />
              รออนุมัติ
            </div>
            <div className="flex items-center gap-1.5">
              <span className="size-3 rounded bg-secondary/40 border border-secondary" />
              วันนี้
            </div>
          </div>
        </Card>

        {/* Right panel — selected day details */}
        <Card className="p-6 border-border h-fit sticky top-24">
          <div className="mb-4">
            <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
              วันที่เลือก
            </div>
            <h3 className="font-display font-bold text-xl text-foreground">
              {selected ? format(selected, "EEEE d MMMM", { locale: th }) : "เลือกวันที่"}
            </h3>
          </div>

          <Button
            onClick={() => nav(`/book?date=${selected ? format(selected, "yyyy-MM-dd") : ""}`)}
            className="w-full mb-5 bg-gradient-primary text-primary-foreground"
          >
            <Plus className="size-4 mr-2" /> จองวันนี้
          </Button>

          <div className="space-y-2">
            <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              การจอง ({selectedBookings.length})
            </div>
            {selectedBookings.length === 0 ? (
              <p className="text-sm text-muted-foreground py-6 text-center">
                ห้องประชุมว่างทั้งหมด ✨
              </p>
            ) : (
              selectedBookings.map((b) => {
                const room = rooms.find((r) => r.id === b.roomId)!;
                return (
                  <div key={b.id} className="p-3 rounded-lg border border-border bg-muted/30">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-mono font-semibold text-primary">
                        {b.startTime} - {b.endTime}
                      </span>
                      <Badge variant="outline" className={`${statusColor[b.status]} text-[10px]`}>
                        {statusLabel[b.status]}
                      </Badge>
                    </div>
                    <div className="text-sm font-semibold text-foreground">{room.code} · {room.name}</div>
                    <div className="text-xs text-muted-foreground mt-0.5 truncate">{b.purpose}</div>
                    <div className="text-[11px] text-muted-foreground mt-1">โดย {b.bookerName}</div>
                  </div>
                );
              })
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
