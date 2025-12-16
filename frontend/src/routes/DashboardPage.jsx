import { useAuth } from "../contexts/AuthContext";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <div className="dashboard-welcome">
        <p>Welcome, {user?.full_name || user?.email}!</p>
        {(user?.is_superuser ?? false) && (
          <div className="badge badge-superuser">Superuser</div>
        )}
      </div>
      <div className="dashboard-stats">
        <div className="stat-card">
          <h3>Quick Actions</h3>
          <ul>
            <li>View and manage your items</li>
            <li>Update your profile</li>
            {(user?.is_superuser ?? false) && <li>Manage users</li>}
          </ul>
        </div>
      </div>
    </div>
  );
}

