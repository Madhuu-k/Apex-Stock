import { useState, useEffect } from 'react';
import { inventoryAPI, reportAPI } from '../services/api';
import { Package, DollarSign, AlertTriangle, TrendingUp } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import './Dashboard.css';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, activitiesRes] = await Promise.all([
        inventoryAPI.getStats(),
        reportAPI.getActivityLogs(10),
      ]);
      setStats(statsRes.data);
      setActivities(activitiesRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="page-container"><div className="loading">Loading...</div></div>;
  }

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

   return (
    <div className="page-container">
      <h1 className="page-title">Dashboard</h1>

      {/* Stats Cards */}
      <div className="stats-grid">
        <StatCard
          icon={Package}
          label="Total Items"
          value={stats?.total_items || 0}
          color="blue"
        />
        <StatCard
          icon={DollarSign}
          label="Total Value"
          value={`$${stats?.total_value?.toFixed(2) || 0}`}
          color="green"
        />
        <StatCard
          icon={AlertTriangle}
          label="Low Stock Items"
          value={stats?.low_stock_count || 0}
          color="red"
        />
        <StatCard
          icon={TrendingUp}
          label="Categories"
          value={stats?.categories?.length || 0}
          color="purple"
        />
      </div>

      {/* Charts & Activity */}
      <div className="dashboard-grid">
        {/* Category Distribution */}
        <div className="dashboard-card">
          <h2 className="card-title">Category Distribution</h2>
          {stats?.categories?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats.categories}
                  dataKey="count"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {stats.categories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">No data available</p>
          )}
        </div>

        {/* Recent Activity */}
        <div className="dashboard-card">
          <h2 className="card-title">Recent Activity</h2>
          <div className="activity-list">
            {activities.length > 0 ? (
              activities.map((activity) => (
                <div key={activity.id} className="activity-item">
                  <div className="activity-content">
                    <p className="activity-title">
                      {activity.user} {activity.action} {activity.resource_type}
                    </p>
                    <p className="activity-details">{activity.details}</p>
                    <p className="activity-time">
                      {new Date(activity.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-data">No recent activity</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// eslint-disable-next-line no-unused-vars
function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon stat-icon-${color}`}>
        <Icon size={32} />
      </div>
      <div className="stat-content">
        <p className="stat-label">{label}</p>
        <p className="stat-value">{value}</p>
      </div>
    </div>
  );
}