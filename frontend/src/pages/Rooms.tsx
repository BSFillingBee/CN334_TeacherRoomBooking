import { Link } from "react-router-dom";
import { rooms, equipmentLabel } from "@/data/mockData";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Users, MapPin, Search, ArrowRight } from "lucide-react";
import { useState } from "react";

export default function Rooms() {
  const [q, setQ] = useState("");
  const [size, setSize] = useState<string>("all");

  const filtered = rooms.filter((r) => {
    const matchQ = !q || r.name.includes(q) || r.code.includes(q);
    const matchSize = size === "all" || r.size === size;
    return matchQ && matchSize;
  });

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto animate-fade-in">
      <div className="mb-6">
        <h1 className="font-display font-bold text-3xl text-foreground">ห้องประชุมทั้งหมด</h1>
        <p className="text-muted-foreground">{rooms.length} ห้องประชุม · ชั้น 4 อาคารวิศวกรรมศาสตร์</p>
      </div>

      <div className="flex flex-col md:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="size-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="ค้นหาห้องตามชื่อหรือเลขห้อง..."
            className="pl-10 h-11 bg-card"
          />
        </div>
        <div className="flex gap-2">
          {[
            { v: "all", l: "ทั้งหมด" },
            { v: "small", l: "เล็ก" },
            { v: "medium", l: "กลาง" },
            { v: "large", l: "ใหญ่" },
          ].map((o) => (
            <Button
              key={o.v}
              variant={size === o.v ? "default" : "outline"}
              onClick={() => setSize(o.v)}
              className={size === o.v ? "bg-gradient-primary text-primary-foreground" : ""}
            >
              {o.l}
            </Button>
          ))}
        </div>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((r) => (
          <Card key={r.id} className="overflow-hidden border-border tu-card group">
            <div className="aspect-[16/10] overflow-hidden bg-muted relative">
              <img
                src={r.image}
                alt={r.name}
                loading="lazy"
                width={1024}
                height={768}
                className="w-full h-full object-cover group-hover:scale-105 transition-smooth duration-500"
              />
              <Badge className="absolute top-3 left-3 bg-card text-foreground border-border shadow-card">
                ห้อง {r.code}
              </Badge>
              <Badge className="absolute top-3 right-3 bg-secondary text-secondary-foreground border-0">
                ขนาด{r.size === "small" ? "เล็ก" : r.size === "medium" ? "กลาง" : "ใหญ่"}
              </Badge>
            </div>
            <div className="p-5">
              <h3 className="font-display font-bold text-lg text-foreground mb-1">{r.name}</h3>
              <div className="flex items-center gap-3 text-sm text-muted-foreground mb-3">
                <span className="flex items-center gap-1">
                  <Users className="size-3.5" /> {r.capacity} คน
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="size-3.5" /> ชั้น {r.floor}
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5 mb-4">
                {r.equipment.slice(0, 3).map((e) => (
                  <span key={e} className="text-[10px] px-2 py-1 rounded-full bg-accent text-accent-foreground font-medium">
                    {equipmentLabel[e]}
                  </span>
                ))}
                {r.equipment.length > 3 && (
                  <span className="text-[10px] px-2 py-1 rounded-full bg-muted text-muted-foreground">
                    +{r.equipment.length - 3}
                  </span>
                )}
              </div>
              <Button asChild className="w-full bg-gradient-primary text-primary-foreground hover:opacity-95">
                <Link to={`/rooms/${r.id}`}>
                  ดูรายละเอียด <ArrowRight className="size-4 ml-1" />
                </Link>
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
