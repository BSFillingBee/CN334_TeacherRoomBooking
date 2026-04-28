import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Sparkles, Send, Bot, User, Calendar, Users, Clock, MapPin, CheckCircle2 } from "lucide-react";
import { rooms } from "@/data/mockData";
import { useAppStore } from "@/store/appStore";
import { apiRequest } from "@/lib/api";
import { toast } from "sonner";

interface Msg {
  role: "user" | "ai";
  text: string;
  parsed?: { roomId: string; date: string; start: string; end: string; attendees: number; purpose: string };
}

interface AIBookingResponse {
  message: string;
  parsed: NonNullable<Msg["parsed"]>;
}

const SUGGESTIONS = [
  "จองห้อง 401 พรุ่งนี้บ่าย 2-4 โมง สำหรับ 15 คน ประชุมหลักสูตร",
  "ขอห้องประชุมเล็กวันศุกร์เช้า workshop 6 คน",
  "ห้องไหนว่างวันจันทร์หน้า 13:00-15:00 บ้าง",
];

export default function AIBooking() {
  const nav = useNavigate();
  const { addBooking } = useAppStore();
  const [input, setInput] = useState("");
  const [msgs, setMsgs] = useState<Msg[]>([
    { role: "ai", text: "สวัสดีครับ! ผมเป็น AI ช่วยจองห้องประชุม 🤖\nลองพิมพ์ความต้องการเป็นภาษาไทยธรรมดาได้เลย เช่น \"จองห้อง 401 พรุ่งนี้บ่าย 2 โมง 15 คน\"" },
  ]);
  const [thinking, setThinking] = useState(false);

  const send = async (text: string) => {
    if (!text.trim()) return;
    setMsgs((m) => [...m, { role: "user", text }]);
    setInput("");
    setThinking(true);

    try {
      const data = await apiRequest<AIBookingResponse>("/api/ai-booking/", {
        method: "POST",
        body: { message: text },
      });
      const room = rooms.find((r) => r.id === data.parsed.roomId)!;
      setMsgs((m) => [
        ...m,
        {
          role: "ai",
          text: `${data.message}\n\nห้อง ${room.name} (${room.code})\nวันที่ ${data.parsed.date}\nเวลา ${data.parsed.start} - ${data.parsed.end} น.\nจำนวน ${data.parsed.attendees} คน\n\nกดยืนยันเพื่อส่งคำขอจองได้เลย`,
          parsed: data.parsed,
        },
      ]);
    } catch (error) {
      const message = error instanceof Error ? error.message : "AI ยังประมวลผลไม่ได้";
      toast.error(message);
      setMsgs((m) => [...m, { role: "ai", text: message }]);
    } finally {
      setThinking(false);
    }
  };

  const confirm = async (parsed: NonNullable<Msg["parsed"]>) => {
    await addBooking({
      roomId: parsed.roomId,
      date: parsed.date,
      startTime: parsed.start,
      endTime: parsed.end,
      purpose: parsed.purpose,
      attendees: parsed.attendees,
    });
    toast.success("AI จองห้องสำเร็จ", { description: "ส่งอีเมลแจ้งเตือนเรียบร้อย" });
    nav("/my-bookings");
  };

  return (
    <div className="p-6 lg:p-8 max-w-4xl mx-auto animate-fade-in">
      <div className="mb-6 flex items-center gap-4">
        <div className="size-12 rounded-xl bg-gradient-warm flex items-center justify-center shadow-glow">
          <Sparkles className="size-6 text-secondary-foreground" />
        </div>
        <div>
          <h1 className="font-display font-bold text-3xl text-foreground">จองห้องด้วย AI</h1>
          <p className="text-muted-foreground">บอกความต้องการเป็นภาษาธรรมดา · AI จะจัดการให้</p>
        </div>
        <span className="ml-auto text-[10px] px-2 py-1 rounded-full bg-warning/15 text-warning font-bold border border-warning/30">
          DEMO
        </span>
      </div>

      <Card className="border-border overflow-hidden">
        <div className="h-[480px] overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-accent/10 to-card">
          {msgs.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""} animate-fade-in`}>
              <div className={`size-9 rounded-full flex items-center justify-center shrink-0 ${
                m.role === "ai" ? "bg-gradient-warm text-secondary-foreground" : "bg-gradient-primary text-primary-foreground"
              }`}>
                {m.role === "ai" ? <Bot className="size-4" /> : <User className="size-4" />}
              </div>
              <div className={`max-w-[80%] ${m.role === "user" ? "items-end" : ""}`}>
                <div className={`px-4 py-3 rounded-2xl whitespace-pre-line text-sm ${
                  m.role === "ai"
                    ? "bg-card border border-border text-foreground rounded-tl-sm"
                    : "bg-gradient-primary text-primary-foreground rounded-tr-sm"
                }`}>
                  {m.text}
                </div>
                {m.parsed && (
                  <Card className="mt-3 p-4 border-2 border-primary/30 bg-card">
                    <div className="grid grid-cols-2 gap-3 text-xs mb-3">
                      <div className="flex items-center gap-2"><MapPin className="size-3.5 text-primary" /> {rooms.find((r) => r.id === m.parsed!.roomId)?.code}</div>
                      <div className="flex items-center gap-2"><Calendar className="size-3.5 text-primary" /> {m.parsed.date}</div>
                      <div className="flex items-center gap-2"><Clock className="size-3.5 text-primary" /> {m.parsed.start}-{m.parsed.end}</div>
                      <div className="flex items-center gap-2"><Users className="size-3.5 text-primary" /> {m.parsed.attendees} คน</div>
                    </div>
                    <Button onClick={() => confirm(m.parsed!)} className="w-full bg-gradient-primary text-primary-foreground" size="sm">
                      <CheckCircle2 className="size-4 mr-1.5" /> ยืนยันการจอง
                    </Button>
                  </Card>
                )}
              </div>
            </div>
          ))}
          {thinking && (
            <div className="flex gap-3">
              <div className="size-9 rounded-full bg-gradient-warm flex items-center justify-center">
                <Bot className="size-4 text-secondary-foreground" />
              </div>
              <div className="px-4 py-3 rounded-2xl bg-card border border-border">
                <div className="flex gap-1">
                  {[0, 1, 2].map((i) => (
                    <span key={i} className="size-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: `${i * 100}ms` }} />
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-border bg-card p-4">
          <div className="flex flex-wrap gap-2 mb-3">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => void send(s)}
                className="text-[11px] px-3 py-1.5 rounded-full bg-accent text-accent-foreground hover:bg-accent/80 transition-smooth border border-accent"
              >
                {s}
              </button>
            ))}
          </div>
          <form onSubmit={(e) => { e.preventDefault(); void send(input); }} className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="พิมพ์บอก AI ได้เลย..."
              className="flex-1 h-12 px-4 rounded-xl border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <Button type="submit" size="icon" className="h-12 w-12 bg-gradient-primary text-primary-foreground shadow-elegant">
              <Send className="size-4" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}
