import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';

export default function FeedbackDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchReport();
  }, [id]);

  const fetchReport = async () => {
    try {
      const res = await fetch(`http://localhost:8000/feedback/${id}`);
      const data = await res.json();
      setReport(data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleStatusChange = async (e) => {
    const newStatus = e.target.value;
    setUpdating(true);
    try {
      const res = await fetch(`http://localhost:8000/feedback/${id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      const updated = await res.json();
      setReport(updated);
    } catch (err) {
      console.error(err);
      alert('Failed to update status');
    }
    setUpdating(false);
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (!report) return <div className="p-8">Report not found</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <button onClick={() => navigate('/feedback')} className="text-sm text-muted-foreground hover:text-foreground mb-2 flex items-center">
            ← Back to Reports
          </button>
          <h1 className="text-3xl font-bold tracking-tight">{report.id}</h1>
          <p className="text-muted-foreground mt-1">Submitted on {new Date(report.created_at).toLocaleString()}</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-1">Status</label>
          <select 
            value={report.status} 
            onChange={handleStatusChange}
            disabled={updating}
            className="border rounded px-3 py-2 bg-background font-medium"
          >
            <option value="Submitted">Submitted</option>
            <option value="Under Review">Under Review</option>
            <option value="Investigating">Investigating</option>
            <option value="Resolved">Resolved</option>
            <option value="Closed">Closed</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Description</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-wrap">{report.description}</p>
            </CardContent>
          </Card>
          
          {report.rating && (
            <Card>
              <CardHeader>
                <CardTitle>Session Rating</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="font-medium text-lg">{report.rating}</p>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Category</p>
                <p className="font-medium">{report.category}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Severity</p>
                <span className={`px-2 py-1 inline-block mt-1 rounded text-xs font-medium ${report.severity === 'Critical' ? 'bg-red-100 text-red-800' : report.severity === 'High' ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800'}`}>
                  {report.severity}
                </span>
              </div>
              {report.session_id && (
                <div>
                  <p className="text-sm text-muted-foreground">Session</p>
                  <a href={`/sessions/${report.session_id}`} className="text-primary hover:underline font-medium break-all">
                    {report.session_id}
                  </a>
                </div>
              )}
            </CardContent>
          </Card>

          {report.technical_context && (
            <Card>
              <CardHeader>
                <CardTitle>Technical Context</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  {Object.entries(report.technical_context).map(([key, value]) => (
                    <div key={key}>
                      <span className="text-muted-foreground capitalize">{key.replace('_', ' ')}: </span>
                      <span className="font-medium">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
