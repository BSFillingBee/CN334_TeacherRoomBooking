import { rooms, equipmentLabel } from "@/data/mockData";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Edit, Plus, Users } from "lucide-react";

export default function AdminRooms() {
  return (
    <div className="p-6 lg:p-8 max-w-6xl mx-auto animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display font-bold text-3xl text-foreground">จัดการห้องประชุม</h1>
          <p className="text-muted-foreground">เพิ่ม/แก้ไข ข้อมูลห้องประชุม</p>
        </div>
        <Button className="bg-gradient-primary text-primary-foreground shadow-elegant">
          <Plus className="size-4 mr-2" /> เพิ่มห้อง
        </Button>
      </div>

      <Card className="border-border overflow-hidden">
        <table className="w-full">
          <thead className="bg-muted">
            <tr className="text-left text-xs uppercase tracking-wider text-muted-foreground">
              <th className="px-4 py-3">รหัส</th>
              <th className="px-4 py-3">ห้อง</th>
              <th className="px-4 py-3">ความจุ</th>
              <th className="px-4 py-3">อุปกรณ์</th>
              <th className="px-4 py-3">สถานะ</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {rooms.map((r) => (
              <tr key={r.id} className="hover:bg-muted/30 transition-smooth">
                <td className="px-4 py-4 font-mono font-bold text-primary">{r.code}</td>
                <td className="px-4 py-4">
                  <div className="flex items-center gap-3">
                    <img src={r.image} alt="" className="size-10 rounded object-cover" loading="lazy" />
                    <div>
                      <div className="font-semibold text-foreground text-sm">{r.name}</div>
                      <div className="text-xs text-muted-foreground">ชั้น {r.floor}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-4">
                  <span className="flex items-center gap-1 text-sm text-foreground">
                    <Users className="size-3.5" /> {r.capacity}
                  </span>
                </td>
                <td className="px-4 py-4">
                  <div className="flex flex-wrap gap-1">
                    {r.equipment.slice(0, 2).map((e) => (
                      <span key={e} className="text-[10px] px-2 py-0.5 rounded bg-accent text-accent-foreground">
                        {equipmentLabel[e]}
                      </span>
                    ))}
                    {r.equipment.length > 2 && (
                      <span className="text-[10px] text-muted-foreground">+{r.equipment.length - 2}</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-4">
                  <Badge variant="outline" className="bg-success/10 text-success border-success/30">
                    เปิดใช้งาน
                  </Badge>
                </td>
                <td className="px-4 py-4 text-right">
                  <Button variant="ghost" size="sm">
                    <Edit className="size-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
