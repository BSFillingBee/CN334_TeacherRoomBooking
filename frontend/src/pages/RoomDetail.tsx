import { useParams, Link, useNavigate } from "react-router-dom";
import { rooms, equipmentLabel } from "@/data/mockData";
import { useAppStore } from "@/store/appStore";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Users, MapPin, Calendar, CheckCircle2 } from "lucide-react";
import { Box3D } from "@/components/Box3D";

export default function RoomDetail() {
  const { id } = useParams();
  const nav = useNavigate();
  const { bookings } = useAppStore();
  const room = rooms.find((r) => r.id === id);

  if (!room) return <div className="p-8">ไม่พบห้อง</div>;

  const roomBookings = bookings
    .filter((b) => b.roomId === room.id && b.status !== "cancelled")
    .slice(0, 5);

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto animate-fade-in">
      <Button variant="ghost" onClick={() => nav(-1)} className="mb-4">
        <ArrowLeft className="size-4 mr-2" /> กลับ
      </Button>

      <div className="grid lg:grid-cols-[1.3fr_1fr] gap-6">
        {/* Left — Image + 3D */}
        <div className="space-y-4">
          <div className="aspect-[16/10] rounded-2xl overflow-hidden shadow-elegant bg-muted">
            <img
              src={room.image}
              alt={room.name}
              width={1024}
              height={768}
              className="w-full h-full object-cover"
            />
          </div>

          <Card className="p-6 border-border">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-display font-bold text-lg text-foreground">รูปร่างห้อง (3D)</h3>
                <p className="text-xs text-muted-foreground">มุมมองไอโซเมตริก · ลากเพื่อหมุน</p>
              </div>
              <Badge variant="outline" className="border-secondary bg-secondary/10 text-secondary-foreground">
                Interactive
              </Badge>
            </div>
            <div className="aspect-[16/10] rounded-xl overflow-hidden bg-gradient-to-b from-accent/30 to-muted">
              <Box3D capacity={room.capacity} size={room.size} />
            </div>
          </Card>
        </div>

        {/* Right — Details */}
        <div className="space-y-4">
          <Card className="p-6 border-border">
            <div className="flex items-start justify-between mb-3">
              <Badge className="bg-gradient-warm text-secondary-foreground border-0 font-bold">
                ห้อง {room.code}
              </Badge>
              <Badge variant="outline" className="border-success/30 bg-success/10 text-success">
                <CheckCircle2 className="size-3 mr-1" /> พร้อมใช้งาน
              </Badge>
            </div>
            <h1 className="font-display font-bold text-3xl text-foreground mb-2">{room.name}</h1>
            <p className="text-muted-foreground text-sm leading-relaxed mb-5">{room.description}</p>

            <div className="grid grid-cols-2 gap-3 mb-5">
              <div className="p-4 rounded-lg bg-muted">
                <Users className="size-5 text-primary mb-1.5" />
                <div className="text-xs text-muted-foreground">รองรับ</div>
                <div className="font-display font-bold text-xl text-foreground">{room.capacity} คน</div>
              </div>
              <div className="p-4 rounded-lg bg-muted">
                <MapPin className="size-5 text-primary mb-1.5" />
                <div className="text-xs text-muted-foreground">ตำแหน่ง</div>
                <div className="font-display font-bold text-xl text-foreground">ชั้น {room.floor}</div>
              </div>
            </div>

            <Button asChild className="w-full h-11 bg-gradient-primary text-primary-foreground shadow-elegant">
              <Link to={`/book?roomId=${room.id}`}>
                <Calendar className="size-4 mr-2" /> จองห้องนี้
              </Link>
            </Button>
          </Card>

          <Card className="p-6 border-border">
            <h3 className="font-display font-bold text-lg text-foreground mb-3">อุปกรณ์ภายในห้อง</h3>
            <div className="space-y-2">
              {room.equipment.map((e) => (
                <div key={e} className="flex items-center gap-3 p-3 rounded-lg bg-accent/40 border border-accent">
                  <CheckCircle2 className="size-4 text-primary shrink-0" />
                  <span className="text-sm text-foreground font-medium">{equipmentLabel[e]}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-6 border-border">
            <h3 className="font-display font-bold text-lg text-foreground mb-3">การจองล่าสุด</h3>
            {roomBookings.length === 0 ? (
              <p className="text-sm text-muted-foreground py-4 text-center">ไม่มีการจอง</p>
            ) : (
              <div className="space-y-2">
                {roomBookings.map((b) => (
                  <div key={b.id} className="flex items-center justify-between text-sm py-2 border-b border-border last:border-0">
                    <div>
                      <div className="font-medium text-foreground">{b.date}</div>
                      <div className="text-xs text-muted-foreground">{b.startTime}-{b.endTime} · {b.bookerName}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
