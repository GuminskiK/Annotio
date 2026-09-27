
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from "./pages/auth/Login.tsx"
import Hello from "./pages/auth/Hello.tsx"
import Dashboard from "./pages/dashboard/Dahsborad.tsx"
import AdminPanel from "./pages/dashboard/Admin/AdminPanel.tsx"
import Profile from "./pages/dashboard/Profile/Profile.tsx"
import { ProtectedRoute } from './components/ProtectedRoute.tsx';
import {AuthProvider} from './context/AuthContext.tsx';
import ProfileAPIKeys from './pages/dashboard/Profile/ProfileAPIKeys.tsx';
import ProfileSecurity from './pages/dashboard/Profile/ProfileSecurity.tsx';
import ProfileSettings from './pages/dashboard/Profile/ProfileSettings.tsx';
import ManageUsers from './pages/dashboard/Admin/ManageUsers.tsx';
import UserProfile from './pages/dashboard/Admin/UserProfile.tsx';
import UserSettings from './pages/dashboard/Admin/UserSettings.tsx';
import UserSecurity from './pages/dashboard/Admin/UserSecurity.tsx';
import UserAPIKeys from './pages/dashboard/Admin/UserAPIKeys.tsx';
import { Toaster } from "sonner";
const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>

          <Route path="/" element={<Hello />} />
          <Route path="/login" element={<Login />} />
          
          <Route element={<ProtectedRoute />}>
            
            <Route path="/dashboard" element={<Dashboard />} />

            <Route path="/admin" element={<AdminPanel />} />
 
            <Route path="/profile" element={<Profile />}>
              <Route index element={<Navigate to="settings" replace />} />
              <Route path="settings" element={<ProfileSettings />} />
              <Route path="security" element={<ProfileSecurity />} />
              <Route path="apikeys" element={<ProfileAPIKeys />} />
              <Route path="preferences" element={
                <div>
                  <h2 className="text-2xl font-bold mb-4">Preferences</h2>
                  <p className="text-gray-600">TODO - Future implementation</p>
                </div>
              } />
            </Route>

            <Route path="/admin" element={<AdminPanel />}>
              <Route index element={<Navigate to="manage_users" replace />} />
              <Route path="manage_users" element={<ManageUsers />} />
            </Route>

            <Route path="/user" element={<UserProfile />}>
              <Route index element={<Navigate to="settings" replace />} />
              <Route path="settings/:id" element={<UserSettings />} />
              <Route path="security/:id" element={<UserSecurity />} />
              <Route path="apikeys/:id" element={<UserAPIKeys />} />
              <Route path="preferences/:id" element={
                <div>
                  <h2 className="text-2xl font-bold mb-4">Preferences</h2>
                  <p className="text-gray-600">TODO - Future implementation</p>
                </div>
              } />
            </Route>
            
          </Route>

          <Route path="*" element={<Navigate to="/login" replace />} />

        </Routes>
        <Toaster />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
