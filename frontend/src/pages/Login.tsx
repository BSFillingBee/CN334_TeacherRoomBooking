import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { useAppStore } from "@/store/appStore";
import { Shield, Building2, GraduationCap } from "lucide-react";
import tseLogo from "@/assets/tse-logo.png";

export default function Login() {
  const nav = useNavigate();
  const { login } = useAppStore();
  const [user, setUser] = useState("somchai");
  const [pwd, setPwd] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    await login("staff", user, pwd);
    nav("/");
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-background">
      {/* Left — Brand panel */}
      <div className="hidden lg:flex relative bg-gradient-hero p-12 flex-col justify-between text-primary-foreground overflow-hidden">
        <div className="absolute -top-20 -right-20 size-96 bg-secondary/30 rounded-full blur-3xl" />
        <div className="absolute -bottom-32 -left-20 size-96 bg-primary-glow/40 rounded-full blur-3xl" />

        <div className="relative z-10">
          <div className="flex items-center gap-4">
            <div className="size-16 rounded-xl bg-white flex items-center justify-center shadow-glow overflow-hidden p-1.5">
              <img src={tseLogo} alt="TSE" className="size-full object-contain" />
            </div>
            <div>
              <div className="font-display font-bold text-2xl leading-tight">มหาวิทยาลัยธรรมศาสตร์</div>
              <div className="text-primary-foreground/80 text-sm">Thammasat University</div>
            </div>
          </div>
        </div>

        <div className="relative z-10 space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-secondary/20 backdrop-blur rounded-full text-xs font-medium border border-secondary/30">
            <span className="size-1.5 bg-secondary rounded-full animate-pulse" />
            คณะวิศวกรรมศาสตร์
          </div>
          <h1 className="font-display font-extrabold text-5xl leading-tight">
            ระบบจอง<br />ห้องประชุมออนไลน์
          </h1>
          <p className="text-primary-foreground/80 text-lg max-w-md leading-relaxed">
              ดูปฏิทินห้องว่าง และจัดการการจองของคุณในที่เดียว พร้อมระบบ AI ช่วยจอง
          </p>
          <div className="grid grid-cols-3 gap-4 pt-4">
            {[
              { icon: Building2, label: "6 ห้องประชุม" },
              { icon: GraduationCap, label: "8 ภาควิชา" },
              { icon: Shield, label: "TU Login" },
            ].map((f) => (
              <div key={f.label} className="space-y-2">
                <f.icon className="size-5 text-secondary" />
                <div className="text-xs text-primary-foreground/80">{f.label}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 text-xs text-primary-foreground/60">
          © 2568 คณะวิศวกรรมศาสตร์ มหาวิทยาลัยธรรมศาสตร์
        </div>
      </div>

      {/* Right — Login form */}
      <div className="flex items-center justify-center p-6 lg:p-12">
        <Card className="w-full max-w-md p-8 border-border shadow-elegant animate-scale-in">
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="size-12 rounded-lg bg-white flex items-center justify-center overflow-hidden p-1">
              <img src={tseLogo} alt="TSE" className="size-full object-contain" />
            </div>
            <div className="font-display font-bold">ระบบจองห้องประชุม</div>
          </div>

          <div className="space-y-2 mb-8">
            <h2 className="font-display font-bold text-3xl text-foreground">เข้าสู่ระบบ</h2>
            <p className="text-muted-foreground text-sm">
              เข้าสู่ระบบด้วยบัญชี <span className="font-semibold text-primary">TU Account</span> ของคุณ
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="user">TU Account</Label>
              <Input
                id="user"
                value={user}
                onChange={(e) => setUser(e.target.value)}
                placeholder="example.tu"
                className="h-11"
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="pwd">รหัสผ่าน</Label>
                <button type="button" className="text-xs text-primary hover:underline">
                  ลืมรหัสผ่าน?
                </button>
              </div>
              <Input
                id="pwd"
                type="password"
                value={pwd}
                onChange={(e) => setPwd(e.target.value)}
                className="h-11"
              />
            </div>

            <Button type="submit" className="w-full h-11 bg-gradient-primary hover:opacity-95 text-primary-foreground font-semibold shadow-elegant">
              เข้าสู่ระบบด้วย TU REST API
            </Button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-card px-2 text-muted-foreground">หรือ</span>
              </div>
            </div>

            <p className="text-xs text-muted-foreground text-center pt-2">
              เฉพาะเจ้าหน้าที่คณะวิศวกรรมศาสตร์เท่านั้น
            </p>
          </form>
        </Card>
      </div>
    </div>
  );
}
