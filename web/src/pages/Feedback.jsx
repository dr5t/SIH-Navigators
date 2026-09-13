import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function Feedback() {
  const [reports, setReports] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('All');
  const [filterSeverity, setFilterSeverity] = useState('All');

  useEffect(() => {
    fetchData();
  }, [filterStatus, filterSeverity]);

  const fetchData = async () => {
    setLoading(true);
    try {
      let url = '/feedback?';
      if (filterStatus !== 'All') url += `status=${filterStatus}&`;
      if (filterSeverity !== 'All') url += `severity=${filterSeverity}&`;
      
      const [reportsRes, analyticsRes] = await Promise.all([
        fetch('http://localhost:8000' + url),
        fetch('http://localhost:8000/feedback/analytics')
      ]);
      const reportsData = await reportsRes.json();
      const analyticsData = await analyticsRes.json();
      
      setReports(reportsData);
      setAnalytics(analyticsData);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Feedback & Support</h1>
          <p className="text-muted-foreground mt-2">Manage bug reports and feature requests.</p>
        </div>
      </div>

      {analytics && (
        <div className="grid gap-6 grid-cols-1 md:grid-cols-3 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Open Reports</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{analytics.open_reports}</div>
              <p className="text-xs text-muted-foreground mt-1">out of {analytics.total_reports} total</p>
            </CardContent>
          </Card>
          <Card className="md:col-span-2">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Reports by Severity</CardTitle>
            </CardHeader>
            <CardContent className="h-[120px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics.by_severity}>
                  <XAxis dataKey="severity" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Recent Feedback</CardTitle>
            <div className="flex gap-4">
              <select className="border rounded px-2 py-1" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
                <option value="All">All Statuses</option>
                <option value="Submitted">Submitted</option>
                <option value="Under Review">Under Review</option>
                <option value="Investigating">Investigating</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
              </select>
              <select className="border rounded px-2 py-1" value={filterSeverity} onChange={e => setFilterSeverity(e.target.value)}>
                <option value="All">All Severities</option>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Critical">Critical</option>
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>Loading...</p>
          ) : reports.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">No reports found matching filters.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-muted-foreground uppercase bg-muted/50">
                  <tr>
                    <th className="px-6 py-3">ID / Date</th>
                    <th className="px-6 py-3">Category</th>
                    <th className="px-6 py-3">Severity</th>
                    <th className="px-6 py-3">Status</th>
                    <th className="px-6 py-3">Description</th>
                    <th className="px-6 py-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {reports.map((report) => (
                    <tr key={report.id} className="border-b last:border-0 hover:bg-muted/50">
                      <td className="px-6 py-4">
                        <div className="font-medium text-foreground">{report.id}</div>
                        <div className="text-xs text-muted-foreground">{new Date(report.created_at).toLocaleDateString()}</div>
                      </td>
                      <td className="px-6 py-4">{report.category}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded text-xs ${report.severity === 'Critical' ? 'bg-red-100 text-red-800' : report.severity === 'High' ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800'}`}>
                          {report.severity}
                        </span>
                      </td>
                      <td className="px-6 py-4">{report.status}</td>
                      <td className="px-6 py-4 max-w-xs truncate">{report.description}</td>
                      <td className="px-6 py-4">
                        <a href={`/feedback/${report.id}`} className="text-primary hover:underline font-medium">View</a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
