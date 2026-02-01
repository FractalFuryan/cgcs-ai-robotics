/**
 * Safety Dashboard - Real-time monitoring for Linear C Enterprise Platform
 * 
 * This React component provides a comprehensive dashboard for monitoring
 * robot fleet safety in real-time.
 */
import React, { useState, useEffect } from 'react';

const SafetyDashboard = () => {
  const [fleetStatus, setFleetStatus] = useState(null);
  const [robots, setRobots] = useState([]);
  const [selectedRobot, setSelectedRobot] = useState(null);
  const [realTimeData, setRealTimeData] = useState([]);
  const [safetyAlerts, setSafetyAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [ws, setWs] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  // API base URL
  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Safety score colors
  const getSafetyScoreColor = (score) => {
    if (score >= 90) return '#10B981'; // Green
    if (score >= 80) return '#F59E0B'; // Yellow
    if (score >= 70) return '#F97316'; // Orange
    return '#EF4444'; // Red
  };

  // Load fleet data
  useEffect(() => {
    loadFleetData();
    const interval = setInterval(loadFleetData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  // WebSocket for real-time updates
  useEffect(() => {
    if (selectedRobot) {
      const websocket = new WebSocket(
        `${API_BASE.replace('http', 'ws')}/api/v1/ws/safety-monitor/${selectedRobot}`
      );
      
      websocket.onopen = () => {
        console.log('WebSocket connected for', selectedRobot);
      };
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'heartbeat') return;
        
        if (data.type === 'validation') {
          const validation = data.data;
          
          setRealTimeData(prev => {
            const newData = [...prev, {
              timestamp: new Date(validation.timestamp).getTime(),
              is_valid: validation.is_valid === 'true',
              validation_time_ms: parseFloat(validation.validation_time_ns) / 1e6,
              linear_c: validation.linear_c,
              message: validation.message
            }];
            
            // Keep last 50 data points
            return newData.slice(-50);
          });
          
          // Show alert for violations
          if (validation.is_valid === 'false') {
            setSafetyAlerts(prev => [{
              id: Date.now(),
              robot_id: selectedRobot,
              timestamp: validation.timestamp,
              message: validation.message,
              linear_c: validation.linear_c,
              severity: 'high'
            }, ...prev.slice(0, 9)]); // Keep last 10 alerts
          }
        }
      };
      
      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      websocket.onclose = () => {
        console.log('WebSocket closed');
      };
      
      setWs(websocket);
      
      return () => {
        if (websocket.readyState === WebSocket.OPEN) {
          websocket.close();
        }
      };
    }
  }, [selectedRobot, API_BASE]);

  const loadFleetData = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/fleet/status`, {
        headers: {
          'Authorization': 'Bearer demo-token'
        }
      });
      
      const data = await response.json();
      setFleetStatus(data);
      setRobots(data.robots || []);
    } catch (error) {
      console.error('Error loading fleet data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRobotSelect = (robotId) => {
    setSelectedRobot(robotId);
    setRealTimeData([]);
  };

  const handleSafetyOverride = async (robotId, durationSeconds, reason) => {
    try {
      await fetch(`${API_BASE}/api/v1/safety/override`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer demo-token'
        },
        body: JSON.stringify({
          robot_id: robotId,
          override_type: 'temporary',
          duration_seconds: durationSeconds,
          reason: reason,
          operator_id: 'dashboard_user'
        })
      });
      
      alert(`Safety override granted for ${robotId}`);
    } catch (error) {
      alert(`Override failed: ${error.message}`);
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading Linear C Safety Dashboard...</div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>🛡️ Linear C Safety Dashboard</h1>
          <p style={styles.subtitle}>Real-time safety monitoring for robot fleet</p>
        </div>
        <div style={styles.badges}>
          <div style={styles.badge}>
            {fleetStatus?.active_robots || 0} Active Robots
          </div>
          <div style={styles.badge}>
            Avg Safety: {fleetStatus?.avg_safety_score?.toFixed(1) || 100}%
          </div>
        </div>
      </div>

      {/* Safety Alerts */}
      {safetyAlerts.length > 0 && (
        <div style={styles.alertBanner}>
          <div style={styles.alertContent}>
            <span>⚠️ {safetyAlerts.length} active safety alert(s)</span>
            <button 
              style={styles.dismissButton}
              onClick={() => setSafetyAlerts([])}
            >
              Dismiss All
            </button>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div style={styles.tabs}>
        <button
          style={{...styles.tab, ...(activeTab === 'overview' ? styles.activeTab : {})}}
          onClick={() => setActiveTab('overview')}
        >
          Fleet Overview
        </button>
        <button
          style={{...styles.tab, ...(activeTab === 'robot' ? styles.activeTab : {})}}
          onClick={() => setActiveTab('robot')}
        >
          Robot Details
        </button>
        <button
          style={{...styles.tab, ...(activeTab === 'alerts' ? styles.activeTab : {})}}
          onClick={() => setActiveTab('alerts')}
        >
          Safety Alerts
        </button>
      </div>

      {/* Fleet Overview Tab */}
      {activeTab === 'overview' && (
        <div>
          {/* Fleet Health Cards */}
          <div style={styles.cardGrid}>
            <div style={styles.card}>
              <h3 style={styles.cardTitle}>Fleet Summary</h3>
              <div style={styles.cardContent}>
                <div style={styles.stat}>
                  <div style={styles.statValue}>{fleetStatus?.total_robots || 0}</div>
                  <div style={styles.statLabel}>Total Robots</div>
                </div>
                <div style={styles.stat}>
                  <div style={styles.statValue}>{fleetStatus?.active_robots || 0}</div>
                  <div style={styles.statLabel}>Active</div>
                </div>
                <div style={styles.stat}>
                  <div style={styles.statValue}>{fleetStatus?.safety_violations_24h || 0}</div>
                  <div style={styles.statLabel}>Violations (24h)</div>
                </div>
              </div>
            </div>

            <div style={styles.card}>
              <h3 style={styles.cardTitle}>Average Safety Score</h3>
              <div style={styles.cardContent}>
                <div style={styles.scoreCircle}>
                  <div 
                    style={{
                      ...styles.scoreValue,
                      color: getSafetyScoreColor(fleetStatus?.avg_safety_score || 100)
                    }}
                  >
                    {fleetStatus?.avg_safety_score?.toFixed(1) || 100}%
                  </div>
                </div>
              </div>
            </div>

            <div style={styles.card}>
              <h3 style={styles.cardTitle}>System Status</h3>
              <div style={styles.cardContent}>
                <div style={styles.statusItem}>
                  <span style={styles.statusDot} />
                  <span>Control Plane: Online</span>
                </div>
                <div style={styles.statusItem}>
                  <span style={styles.statusDot} />
                  <span>Analytics: Running</span>
                </div>
                <div style={styles.statusItem}>
                  <span style={styles.statusDot} />
                  <span>Hardware Safety: Active</span>
                </div>
              </div>
            </div>
          </div>

          {/* Robot Table */}
          <div style={styles.card}>
            <h3 style={styles.cardTitle}>Robot Fleet</h3>
            <div style={styles.tableWrapper}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Robot ID</th>
                    <th style={styles.th}>Type</th>
                    <th style={styles.th}>Status</th>
                    <th style={styles.th}>Safety Score</th>
                    <th style={styles.th}>Violations (24h)</th>
                    <th style={styles.th}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {robots.map(robot => (
                    <tr 
                      key={robot.robot_id}
                      style={{
                        ...styles.tr,
                        backgroundColor: selectedRobot === robot.robot_id ? '#EFF6FF' : 'white'
                      }}
                      onClick={() => handleRobotSelect(robot.robot_id)}
                    >
                      <td style={styles.td}>{robot.robot_id}</td>
                      <td style={styles.td}>{robot.robot_type}</td>
                      <td style={styles.td}>
                        <span style={{
                          ...styles.statusBadge,
                          backgroundColor: robot.is_active ? '#10B981' : '#6B7280',
                          color: 'white'
                        }}>
                          {robot.is_active ? 'Active' : 'Offline'}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <div style={styles.scoreBar}>
                          <div 
                            style={{
                              width: `${robot.safety_score}%`,
                              height: '100%',
                              backgroundColor: getSafetyScoreColor(robot.safety_score),
                              borderRadius: '4px'
                            }}
                          />
                        </div>
                        <span>{parseFloat(robot.safety_score).toFixed(1)}%</span>
                      </td>
                      <td style={styles.td}>
                        <span style={{
                          ...styles.statusBadge,
                          backgroundColor: robot.violations_24h > 0 ? '#EF4444' : '#E5E7EB',
                          color: robot.violations_24h > 0 ? 'white' : '#6B7280'
                        }}>
                          {robot.violations_24h}
                        </span>
                      </td>
                      <td style={styles.td}>
                        <button
                          style={styles.actionButton}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRobotSelect(robot.robot_id);
                            setActiveTab('robot');
                          }}
                        >
                          Monitor
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Robot Details Tab */}
      {activeTab === 'robot' && (
        <div>
          {selectedRobot ? (
            <>
              <div style={styles.card}>
                <h3 style={styles.cardTitle}>Real-time Monitoring: {selectedRobot}</h3>
                <div style={styles.cardContent}>
                  <h4>Recent Validations</h4>
                  <div style={styles.validationList}>
                    {realTimeData.slice(-10).reverse().map((item, index) => (
                      <div 
                        key={index}
                        style={{
                          ...styles.validationItem,
                          borderLeft: `4px solid ${item.is_valid ? '#10B981' : '#EF4444'}`
                        }}
                      >
                        <div style={styles.validationHeader}>
                          <code style={styles.linearCCode}>{item.linear_c}</code>
                          <span style={{
                            ...styles.statusBadge,
                            backgroundColor: item.is_valid ? '#10B981' : '#EF4444',
                            color: 'white'
                          }}>
                            {item.is_valid ? 'Valid' : 'Blocked'}
                          </span>
                        </div>
                        <div style={styles.validationFooter}>
                          <span style={styles.timestamp}>
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </span>
                          <span style={styles.responseTime}>
                            Response: {item.validation_time_ms.toFixed(2)}ms
                          </span>
                        </div>
                        {item.message && (
                          <div style={styles.validationMessage}>{item.message}</div>
                        )}
                      </div>
                    ))}
                    {realTimeData.length === 0 && (
                      <div style={styles.emptyState}>
                        Waiting for validation data...
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div style={styles.card}>
              <div style={styles.emptyState}>
                Select a robot from the fleet overview to monitor its real-time safety data.
              </div>
            </div>
          )}
        </div>
      )}

      {/* Safety Alerts Tab */}
      {activeTab === 'alerts' && (
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>Safety Alerts</h3>
          <div style={styles.cardContent}>
            {safetyAlerts.length > 0 ? (
              <div style={styles.alertList}>
                {safetyAlerts.map(alert => (
                  <div key={alert.id} style={styles.alertItem}>
                    <div style={styles.alertHeader}>
                      <strong>Safety Violation: {alert.robot_id}</strong>
                      <span style={styles.alertTime}>
                        {new Date(alert.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div style={styles.alertBody}>
                      <p>{alert.message}</p>
                      <code style={styles.linearCCode}>{alert.linear_c}</code>
                    </div>
                    <div style={{
                      ...styles.statusBadge,
                      backgroundColor: '#EF4444',
                      color: 'white',
                      marginTop: '8px',
                      display: 'inline-block'
                    }}>
                      High Severity
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={styles.emptyState}>
                ✅ No active safety alerts. Fleet is operating safely.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Styles
const styles = {
  container: {
    padding: '24px',
    backgroundColor: '#F9FAFB',
    minHeight: '100vh',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
  },
  loading: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    fontSize: '18px',
    color: '#6B7280'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px'
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#111827',
    margin: 0
  },
  subtitle: {
    fontSize: '16px',
    color: '#6B7280',
    margin: '4px 0 0 0'
  },
  badges: {
    display: 'flex',
    gap: '12px'
  },
  badge: {
    padding: '8px 16px',
    backgroundColor: '#EFF6FF',
    border: '1px solid #DBEAFE',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#1E40AF'
  },
  alertBanner: {
    backgroundColor: '#FEE2E2',
    border: '1px solid #FCA5A5',
    borderRadius: '8px',
    padding: '16px',
    marginBottom: '24px'
  },
  alertContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    color: '#991B1B'
  },
  dismissButton: {
    padding: '6px 12px',
    backgroundColor: 'white',
    border: '1px solid #DC2626',
    borderRadius: '6px',
    color: '#DC2626',
    cursor: 'pointer',
    fontSize: '14px'
  },
  tabs: {
    display: 'flex',
    gap: '8px',
    marginBottom: '24px',
    borderBottom: '1px solid #E5E7EB'
  },
  tab: {
    padding: '12px 24px',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: '2px solid transparent',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    color: '#6B7280',
    transition: 'all 0.2s'
  },
  activeTab: {
    color: '#2563EB',
    borderBottom: '2px solid #2563EB'
  },
  cardGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '24px',
    marginBottom: '24px'
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
    padding: '24px',
    marginBottom: '24px'
  },
  cardTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#111827',
    marginTop: 0,
    marginBottom: '16px'
  },
  cardContent: {
    display: 'flex',
    gap: '24px',
    flexWrap: 'wrap'
  },
  stat: {
    flex: 1,
    minWidth: '100px'
  },
  statValue: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: '4px'
  },
  statLabel: {
    fontSize: '14px',
    color: '#6B7280'
  },
  scoreCircle: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '120px',
    height: '120px',
    borderRadius: '50%',
    backgroundColor: '#F9FAFB',
    border: '4px solid #E5E7EB'
  },
  scoreValue: {
    fontSize: '28px',
    fontWeight: 'bold'
  },
  statusItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '12px',
    fontSize: '14px',
    color: '#374151'
  },
  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: '#10B981'
  },
  tableWrapper: {
    overflowX: 'auto'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '14px'
  },
  th: {
    textAlign: 'left',
    padding: '12px',
    borderBottom: '2px solid #E5E7EB',
    fontWeight: '600',
    color: '#374151',
    backgroundColor: '#F9FAFB'
  },
  tr: {
    cursor: 'pointer',
    transition: 'background-color 0.2s'
  },
  td: {
    padding: '12px',
    borderBottom: '1px solid #E5E7EB'
  },
  statusBadge: {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500',
    display: 'inline-block'
  },
  scoreBar: {
    width: '60px',
    height: '8px',
    backgroundColor: '#E5E7EB',
    borderRadius: '4px',
    overflow: 'hidden',
    display: 'inline-block',
    marginRight: '8px'
  },
  actionButton: {
    padding: '6px 16px',
    backgroundColor: '#2563EB',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500'
  },
  validationList: {
    maxHeight: '500px',
    overflowY: 'auto'
  },
  validationItem: {
    padding: '16px',
    marginBottom: '12px',
    backgroundColor: '#F9FAFB',
    borderRadius: '8px'
  },
  validationHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px'
  },
  linearCCode: {
    fontFamily: 'monospace',
    fontSize: '14px',
    padding: '4px 8px',
    backgroundColor: '#F3F4F6',
    borderRadius: '4px'
  },
  validationFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '12px',
    color: '#6B7280'
  },
  timestamp: {
    fontStyle: 'italic'
  },
  responseTime: {
    fontWeight: '500'
  },
  validationMessage: {
    marginTop: '8px',
    fontSize: '13px',
    color: '#374151',
    fontStyle: 'italic'
  },
  alertList: {
    maxHeight: '600px',
    overflowY: 'auto'
  },
  alertItem: {
    padding: '16px',
    marginBottom: '16px',
    backgroundColor: '#FEF2F2',
    border: '1px solid #FCA5A5',
    borderRadius: '8px',
    borderLeft: '4px solid #DC2626'
  },
  alertHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '8px',
    color: '#991B1B'
  },
  alertTime: {
    fontSize: '12px',
    color: '#6B7280'
  },
  alertBody: {
    color: '#374151'
  },
  emptyState: {
    padding: '48px',
    textAlign: 'center',
    color: '#6B7280',
    fontSize: '16px'
  }
};

export default SafetyDashboard;
