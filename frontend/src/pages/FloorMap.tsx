import { useState } from "react";
import { Link } from "react-router-dom";
import { rooms, equipmentLabel } from "@/data/mockData";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import floorMap from "@/assets/floor-map-isometric.png";
import { Users, ArrowRight } from "lucide-react";

export default function FloorMap() {
  const [hovered, setHovered] = useState<string | null>(null);
  const selected = rooms.find((r) => r.id === hovered);

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto animate-fade-in">
      <div className="mb-6">
        <h1 className="font-display font-bold text-3xl text-foreground">แผนผังชั้น 4</h1>
        <p className="text-muted-foreground">อาคารวิศวกรรมศาสตร์ · คลิกที่ห้องเพื่อดูรายละเอียด</p>
      </div>

      <div className="grid lg:grid-cols-[1fr_340px] gap-6">
        <Card className="p-4 lg:p-6 border-border bg-gradient-to-br from-accent/20 to-background relative overflow-hidden">
          <div className="absolute top-4 left-4 z-10 flex flex-col gap-1 text-xs">
            <span className="px-2 py-1 bg-card/90 backdrop-blur rounded font-mono font-semibold text-foreground">N ↑</span>
          </div>
          <div className="absolute top-4 right-4 z-10 flex items-center gap-3 text-xs bg-card/90 backdrop-blur rounded-lg px-3 py-2 border border-border">
            <div className="flex items-center gap-1.5">
              <span className="size-3 rounded-full bg-success" /> ว่าง
            </div>
            <div className="flex items-center gap-1.5">
              <span className="size-3 rounded-full bg-warning" /> ใช้งาน
            </div>
          </div>

          <div className="relative aspect-[16/9] w-full">
            <img
              src={floorMap}
              alt="แผนผังชั้น 4 isometric"
              loading="lazy"
              width={1920}
              height={1080}
              className="w-full h-full object-contain"
            />
            {/* Hot-spots */}
            {rooms.map((r) => (
              <button
                key={r.id}
                onMouseEnter={() => setHovered(r.id)}
                onMouseLeave={() => setHovered(null)}
                style={{ left: `${r.mapX}%`, top: `${r.mapY}%` }}
                className="absolute -translate-x-1/2 -translate-y-1/2 group"
              >
                <span className="relative flex">
                  <span className="animate-ping absolute inline-flex size-full rounded-full bg-primary opacity-30" />
                  <span className={`relative inline-flex size-8 rounded-full items-center justify-center font-display font-bold text-xs shadow-elegant transition-smooth ${
                    hovered === r.id ? "bg-secondary text-secondary-foreground scale-125" : "bg-primary text-primary-foreground"
                  }`}>
                    {r.code}
                  </span>
                </span>
                {hovered === r.id && (
                  <div className="absolute left-1/2 -translate-x-1/2 top-10 whitespace-nowrap bg-card border border-border rounded-lg shadow-elegant px-3 py-1.5 text-xs z-20">
                    <div className="font-semibold text-foreground">{r.name}</div>
                    <div className="text-muted-foreground">{r.capacity} คน</div>
                  </div>
                )}
              </button>
            ))}
          </div>
        </Card>

        {/* Right panel */}
        <Card className="p-6 border-border h-fit sticky top-24">
          {selected ? (
            <div className="animate-fade-in">
              <Badge className="bg-gradient-warm text-secondary-foreground border-0 mb-3">
                ห้อง {selected.code}
              </Badge>
              <h3 className="font-display font-bold text-xl text-foreground mb-1">{selected.name}</h3>
              <div className="flex items-center gap-1 text-sm text-muted-foreground mb-4">
                <Users className="size-3.5" /> {selected.capacity} คน
              </div>
              <div className="aspect-video rounded-lg overflow-hidden mb-4">
                <img src={selected.image} alt="" className="w-full h-full object-cover" loading="lazy" />
              </div>
              <p className="text-sm text-muted-foreground mb-4">{selected.description}</p>
              <div className="flex flex-wrap gap-1.5 mb-4">
                {selected.equipment.map((e) => (
                  <span key={e} className="text-[10px] px-2 py-1 rounded-full bg-accent text-accent-foreground font-medium">
                    {equipmentLabel[e]}
                  </span>
                ))}
              </div>
              <Button asChild className="w-full bg-gradient-primary text-primary-foreground">
                <Link to={`/rooms/${selected.id}`}>
                  ดูรายละเอียด <ArrowRight className="size-4 ml-1" />
                </Link>
              </Button>
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="size-16 mx-auto rounded-full bg-muted flex items-center justify-center mb-3">
                <span className="text-2xl">🏛️</span>
              </div>
              <h3 className="font-display font-bold text-foreground mb-1">เลือกห้อง</h3>
              <p className="text-sm text-muted-foreground">
                วางเมาส์บนเลขห้องเพื่อดูข้อมูล
              </p>
              <div className="mt-6 space-y-2 text-left">
                {rooms.map((r) => (
                  <Link
                    key={r.id}
                    to={`/rooms/${r.id}`}
                    className="flex items-center justify-between p-2 rounded-lg hover:bg-muted transition-smooth"
                  >
                    <span className="text-sm">
                      <span className="font-mono font-bold text-primary">{r.code}</span>
                      <span className="text-foreground ml-2">{r.name}</span>
                    </span>
                    <ArrowRight className="size-3.5 text-muted-foreground" />
                  </Link>
                ))}
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
