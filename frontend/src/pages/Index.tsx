import { useAppStore } from "@/store/appStore";
import Login from "./Login";
import AppLayout from "@/components/AppLayout";
import { Navigate, Route, Routes } from "react-router-dom";
import Dashboard from "./Dashboard";
import CalendarPage from "./CalendarPage";
import Rooms from "./Rooms";
import RoomDetail from "./RoomDetail";
import FloorMap from "./FloorMap";
import BookRoom from "./BookRoom";
import AIBooking from "./AIBooking";
import MyBookings from "./MyBookings";
import AdminApproval from "./AdminApproval";
import AdminRooms from "./AdminRooms";
import AdminReports from "./AdminReports";
import AdminSettings from "./AdminSettings";

const Index = () => {
  const { isAuthenticated, role } = useAppStore();
  if (!isAuthenticated) return <Login />;

  return (
    <Routes>
      <Route element={<AppLayout />}>
        {role === "admin" ? (
          <>
            <Route path="/" element={<Navigate to="/admin" replace />} />
            <Route path="/admin" element={<AdminApproval />} />
            <Route path="/admin/rooms" element={<AdminRooms />} />
            <Route path="/admin/reports" element={<AdminReports />} />
            <Route path="/admin/settings" element={<AdminSettings />} />
            <Route path="*" element={<Navigate to="/admin" replace />} />
          </>
        ) : (
          <>
            <Route path="/" element={<Dashboard />} />
            <Route path="/calendar" element={<CalendarPage />} />
            <Route path="/rooms" element={<Rooms />} />
            <Route path="/rooms/:id" element={<RoomDetail />} />
            <Route path="/map" element={<FloorMap />} />
            <Route path="/book" element={<BookRoom />} />
            <Route path="/ai-booking" element={<AIBooking />} />
            <Route path="/my-bookings" element={<MyBookings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </>
        )}
      </Route>
    </Routes>
  );
};

export default Index;
