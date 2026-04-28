import { useAppStore } from "@/store/appStore";
import { rooms } from "@/data/mockData";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, BarChart3, Download } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function AdminReports() {
  const { bookings } = useAppStore();

  const usageByRoom = rooms.map((r) => ({
    room: r,
    count: bookings.filter((b) => b.roomId === r.id && b.status === "approved").length,
  })).sort((a, b) => b.count - a.count);

  const max = Math.max(...usageByRoom.map((u) => u.count), 1);

  const byDept = bookings.reduce<Record<string, number>>((acc, b) => {
    acc[b.department] = (acc[b.department] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="p-6 lg:p-8 max-w-6xl mx-auto animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="size-12 rounded-xl bg-gradient-warm flex items-center justify-center">
            <BarChart3 className="size-6 text-secondary-foreground" />
          </div>
          <div>
            <h1 className="font-display font-bold text-3xl text-foreground">รายงานการใช้งาน</h1>
            <p className="text-muted-foreground">สถิติการจองห้องประชุม</p>
          </div>
        </div>
        <Button variant="outline">
          <Download className="size-4 mr-2" /> Export CSV
        </Button>
      </div>

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        {[
          { l: "การจองทั้งหมด", v: bookings.length, sub: "+12% จากเดือนก่อน" },
          { l: "อัตราการใช้งาน", v: "73%", sub: "เฉลี่ยต่อห้อง/สัปดาห์" },
          { l: "ผู้ใช้งานหลัก", v: "8", sub: "ภาควิชา" },
        ].map((s) => (
          <Card key={s.l} className="p-5 border-border tu-card">
            <div className="text-sm text-muted-foreground">{s.l}</div>
            <div className="font-display font-bold text-3xl text-foreground mt-1">{s.v}</div>
            <div className="text-xs text-success flex items-center gap-1 mt-1">
              <TrendingUp className="size-3" /> {s.sub}
            </div>
          </Card>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <Card className="p-6 border-border">
          <h2 className="font-display font-bold text-lg text-foreground mb-4">ห้องที่จองมากที่สุด</h2>
          <div className="space-y-3">
            {usageByRoom.map((u) => (
              <div key={u.room.id}>
                <div className="flex items-center justify-between mb-1.5 text-sm">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="font-mono text-[10px]">{u.room.code}</Badge>
                    <span className="text-foreground">{u.room.name}</span>
                  </div>
                  <span className="font-bold text-primary">{u.count}</span>
                </div>
                <div className="h-2 rounded-full bg-muted overflow-hidden">
                  <div
                    className="h-full bg-gradient-primary rounded-full transition-all"
                    style={{ width: `${(u.count / max) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6 border-border">
          <h2 className="font-display font-bold text-lg text-foreground mb-4">การใช้งานตามภาควิชา</h2>
          <div className="space-y-2">
            {Object.entries(byDept).map(([dept, n]) => (
              <div key={dept} className="flex items-center justify-between p-3 rounded-lg bg-muted/40 border border-border">
                <span className="text-sm text-foreground">{dept}</span>
                <Badge className="bg-secondary text-secondary-foreground border-0">{n} ครั้ง</Badge>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
