import roomLarge from "@/assets/room-large.jpg";
import roomMedium from "@/assets/room-medium.jpg";
import roomSmall from "@/assets/room-small.jpg";

const bootstrap = window.__ROOM_BOOKING_BOOTSTRAP__;

export type RoomEquipment = "projector" | "whiteboard" | "marker" | "tv" | "microphone" | "videocon";

export interface Room {
  id: string;
  code: string;
  name: string;
  floor: number;
  capacity: number;
  size: "small" | "medium" | "large";
  image: string;
  equipment: RoomEquipment[];
  description: string;
  // grid position on floor map (0-100 percent)
  mapX: number;
  mapY: number;
}

const fallbackRooms: Room[] = [
  {
    id: "r401",
    code: "401",
    name: "ห้องประชุมสภาคณะ",
    floor: 4,
    capacity: 24,
    size: "large",
    image: roomLarge,
    equipment: ["projector", "whiteboard", "marker", "microphone", "videocon"],
    description: "ห้องประชุมขนาดใหญ่ สำหรับประชุมสภาคณะและกรรมการบริหาร",
    mapX: 12,
    mapY: 30,
  },
  {
    id: "r402",
    code: "402",
    name: "ห้องสัมมนา A",
    floor: 4,
    capacity: 20,
    size: "medium",
    image: roomMedium,
    equipment: ["projector", "whiteboard", "marker", "microphone"],
    description: "ห้องสัมมนาขนาดกลาง โต๊ะ U-shape เหมาะสำหรับการอภิปราย",
    mapX: 32,
    mapY: 30,
  },
  {
    id: "r403",
    code: "403",
    name: "ห้องสัมมนา B",
    floor: 4,
    capacity: 16,
    size: "medium",
    image: roomMedium,
    equipment: ["projector", "whiteboard", "marker"],
    description: "ห้องสัมมนาขนาดกลาง พร้อมระบบมัลติมีเดียครบครัน",
    mapX: 50,
    mapY: 30,
  },
  {
    id: "r404",
    code: "404",
    name: "ห้องประชุมย่อย 1",
    floor: 4,
    capacity: 6,
    size: "small",
    image: roomSmall,
    equipment: ["tv", "whiteboard", "marker"],
    description: "ห้องประชุมย่อย เหมาะสำหรับการประชุมกลุ่มเล็ก",
    mapX: 68,
    mapY: 35,
  },
  {
    id: "r405",
    code: "405",
    name: "ห้องประชุมย่อย 2",
    floor: 4,
    capacity: 8,
    size: "small",
    image: roomSmall,
    equipment: ["tv", "whiteboard", "marker"],
    description: "ห้องประชุมย่อย พร้อมจอ TV สำหรับนำเสนอ",
    mapX: 82,
    mapY: 35,
  },
  {
    id: "r406",
    code: "406",
    name: "ห้อง Co-Working",
    floor: 4,
    capacity: 12,
    size: "medium",
    image: roomMedium,
    equipment: ["projector", "whiteboard", "marker", "tv"],
    description: "พื้นที่ทำงานร่วมแบบยืดหยุ่น เหมาะกับ workshop",
    mapX: 50,
    mapY: 70,
  },
];

export const rooms: Room[] = Array.isArray(bootstrap?.rooms)
  ? (bootstrap.rooms as Room[])
  : fallbackRooms;

export const equipmentLabel: Record<RoomEquipment, string> = {
  projector: "โปรเจคเตอร์",
  whiteboard: "กระดานไวท์บอร์ด",
  marker: "ปากกามาร์คเกอร์",
  tv: "จอ TV",
  microphone: "ไมโครโฟน",
  videocon: "ระบบ Video Conference",
};

export type BookingStatus = "pending" | "approved" | "rejected" | "cancelled";

export interface Booking {
  id: string;
  roomId: string;
  bookerName: string;
  bookerEmail: string;
  department: string;
  purpose: string;
  date: string; // YYYY-MM-DD
  startTime: string; // HH:mm
  endTime: string;
  attendees: number;
  status: BookingStatus;
  createdAt: string;
}

const today = new Date();
const fmt = (d: Date) => d.toISOString().split("T")[0];
const addDays = (n: number) => {
  const d = new Date(today);
  d.setDate(d.getDate() + n);
  return fmt(d);
};

const fallbackBookings: Booking[] = [
  {
    id: "b001",
    roomId: "r401",
    bookerName: "ผศ.ดร. สมชาย ใจดี",
    bookerEmail: "somchai@engr.tu.ac.th",
    department: "ภาควิชาวิศวกรรมไฟฟ้า",
    purpose: "ประชุมคณะกรรมการบริหารหลักสูตร",
    date: addDays(0),
    startTime: "09:00",
    endTime: "12:00",
    attendees: 18,
    status: "approved",
    createdAt: addDays(-3),
  },
  {
    id: "b002",
    roomId: "r402",
    bookerName: "อ. วราภรณ์ สุขใส",
    bookerEmail: "waraporn@engr.tu.ac.th",
    department: "ภาควิชาวิศวกรรมโยธา",
    purpose: "Workshop การออกแบบโครงสร้าง",
    date: addDays(0),
    startTime: "13:00",
    endTime: "16:00",
    attendees: 15,
    status: "approved",
    createdAt: addDays(-2),
  },
  {
    id: "b003",
    roomId: "r404",
    bookerName: "นายพีระ มั่นคง",
    bookerEmail: "peera@engr.tu.ac.th",
    department: "งานบริการการศึกษา",
    purpose: "นัดสัมภาษณ์นักศึกษา",
    date: addDays(1),
    startTime: "10:00",
    endTime: "11:30",
    attendees: 4,
    status: "pending",
    createdAt: addDays(-1),
  },
  {
    id: "b004",
    roomId: "r403",
    bookerName: "รศ.ดร. นภัส ทองคำ",
    bookerEmail: "napas@engr.tu.ac.th",
    department: "ภาควิชาวิศวกรรมเคมี",
    purpose: "สัมมนาวิทยานิพนธ์ ป.โท",
    date: addDays(2),
    startTime: "14:00",
    endTime: "17:00",
    attendees: 12,
    status: "pending",
    createdAt: addDays(0),
  },
  {
    id: "b005",
    roomId: "r405",
    bookerName: "นางสาวอรุณี แสงทอง",
    bookerEmail: "arunee@engr.tu.ac.th",
    department: "งานวิจัยและบริการวิชาการ",
    purpose: "ประชุมทีมโครงการวิจัย",
    date: addDays(3),
    startTime: "09:00",
    endTime: "11:00",
    attendees: 6,
    status: "approved",
    createdAt: addDays(-5),
  },
  {
    id: "b006",
    roomId: "r406",
    bookerName: "อ.ดร. ธนพล แก้วใส",
    bookerEmail: "thanapol@engr.tu.ac.th",
    department: "ภาควิชาวิศวกรรมคอมพิวเตอร์",
    purpose: "Hackathon เตรียมการแข่งขัน",
    date: addDays(5),
    startTime: "09:00",
    endTime: "17:00",
    attendees: 10,
    status: "approved",
    createdAt: addDays(-4),
  },
];

const fallbackUser = {
  name: "ผศ.ดร. สมชาย ใจดี",
  email: "somchai@engr.tu.ac.th",
  department: "ภาควิชาวิศวกรรมไฟฟ้า",
  role: "staff" as "staff" | "admin",
  avatar: "สช",
};

export const currentUser = (bootstrap?.currentUser as typeof fallbackUser | null) || fallbackUser;
export const initialBookings: Booking[] = Array.isArray(bootstrap?.bookings)
  ? bootstrap.bookings
  : fallbackBookings;

export const statusLabel: Record<BookingStatus, string> = {
  pending: "รออนุมัติ",
  approved: "อนุมัติแล้ว",
  rejected: "ไม่อนุมัติ",
  cancelled: "ยกเลิกแล้ว",
};

export const statusColor: Record<BookingStatus, string> = {
  pending: "bg-warning/15 text-warning border-warning/30",
  approved: "bg-success/15 text-success border-success/30",
  rejected: "bg-destructive/15 text-destructive border-destructive/30",
  cancelled: "bg-muted text-muted-foreground border-border",
};
