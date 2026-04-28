import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Settings, Mail, MessageCircle, Lock } from "lucide-react";

export default function AdminSettings() {
  return (
    <div className="p-6 lg:p-8 max-w-3xl mx-auto animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <div className="size-12 rounded-xl bg-gradient-primary flex items-center justify-center">
          <Settings className="size-6 text-primary-foreground" />
        </div>
        <div>
          <h1 className="font-display font-bold text-3xl text-foreground">ตั้งค่าระบบ</h1>
          <p className="text-muted-foreground">การตั้งค่าทั่วไป · การแจ้งเตือน · ความปลอดภัย</p>
        </div>
      </div>

      <div className="space-y-5">
        <Card className="p-6 border-border">
          <h2 className="font-display font-bold text-lg text-foreground mb-4 flex items-center gap-2">
            <Mail className="size-5 text-primary" /> การแจ้งเตือนอีเมล
          </h2>
          <div className="space-y-4">
            {[
              { l: "แจ้งเตือนเมื่อมีคำขอจอง", on: true },
              { l: "แจ้งเตือนเมื่ออนุมัติ/ปฏิเสธ", on: true },
              { l: "แจ้งเตือนเตือนล่วงหน้า 1 ชั่วโมง", on: true },
              { l: "สรุปประจำสัปดาห์", on: false },
            ].map((s) => (
              <div key={s.l} className="flex items-center justify-between py-2">
                <Label className="text-sm">{s.l}</Label>
                <Switch defaultChecked={s.on} />
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6 border-border">
          <h2 className="font-display font-bold text-lg text-foreground mb-4 flex items-center gap-2">
            <MessageCircle className="size-5 text-success" /> LINE Notify
          </h2>
          <div className="space-y-3">
            <div className="space-y-2">
              <Label>LINE Notify Token</Label>
              <Input type="password" defaultValue="xxxxxxxxxxxxxxxxxx" />
            </div>
            <div className="flex items-center justify-between py-2">
              <Label className="text-sm">เปิดใช้งานการแจ้งเตือนผ่าน LINE</Label>
              <Switch defaultChecked />
            </div>
          </div>
        </Card>

        <Card className="p-6 border-border">
          <h2 className="font-display font-bold text-lg text-foreground mb-4 flex items-center gap-2">
            <Lock className="size-5 text-destructive" /> ความปลอดภัย
          </h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2">
              <div>
                <Label className="text-sm">บังคับ HTTPS</Label>
                <p className="text-xs text-muted-foreground">เปลี่ยนเส้นทางทุกการเชื่อมต่อเป็น HTTPS</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between py-2">
              <div>
                <Label className="text-sm">CSRF Protection</Label>
                <p className="text-xs text-muted-foreground">ป้องกัน Cross-Site Request Forgery</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between py-2">
              <div>
                <Label className="text-sm">XSS Protection</Label>
                <p className="text-xs text-muted-foreground">Sanitize input ทุกฟิลด์</p>
              </div>
              <Switch defaultChecked />
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
