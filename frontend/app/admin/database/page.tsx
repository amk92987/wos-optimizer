'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';

interface TableInfo {
  name: string;
  row_count: number;
  columns: string[];
}

interface BackupInfo {
  filename: string;
  created_at: string;
  size_bytes: number;
}

type TabType = 'tables' | 'backup' | 'cleanup' | 'query';

export default function AdminDatabasePage() {
  const { token, user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('tables');
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [tableData, setTableData] = useState<any[]>([]);
  const [backups, setBackups] = useState<BackupInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingData, setIsLoadingData] = useState(false);

  useEffect(() => {
    if (token) {
      fetchTables();
      fetchBackups();
    }
  }, [token]);

  const fetchTables = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/admin/database/tables', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setTables(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch tables:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchBackups = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/admin/database/backups', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setBackups(Array.isArray(data) ? data : []);
      }
    } catch (error) {
      console.error('Failed to fetch backups:', error);
    }
  };

  const fetchTableData = async (tableName: string) => {
    setIsLoadingData(true);
    setSelectedTable(tableName);
    try {
      const res = await fetch(`http://localhost:8000/api/admin/database/tables/${tableName}?limit=50`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setTableData(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch table data:', error);
    } finally {
      setIsLoadingData(false);
    }
  };

  // Redirect non-admins
  if (user && user.role !== 'admin') {
    return (
      <PageLayout>
        <div className="max-w-2xl mx-auto text-center py-16">
          <div className="text-6xl mb-6">🔒</div>
          <h1 className="text-2xl font-bold text-frost mb-4">Access Denied</h1>
        </div>
      </PageLayout>
    );
  }

  const selectedTableInfo = tables.find((t) => t.name === selectedTable);

  return (
    <PageLayout>
      <div className="max-w-6xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Database Browser</h1>
          <p className="text-frost-muted mt-1">View tables, manage backups, and run maintenance</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-surface-border pb-2">
          {[
            { id: 'tables' as const, label: 'Tables' },
            { id: 'backup' as const, label: 'Backup' },
            { id: 'cleanup' as const, label: 'Cleanup' },
            { id: 'query' as const, label: 'Query' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-ice/20 text-ice'
                  : 'text-frost-muted hover:text-frost hover:bg-surface'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'tables' && (
          <TablesTab
            tables={tables}
            selectedTable={selectedTable}
            tableData={tableData}
            selectedTableInfo={selectedTableInfo}
            isLoading={isLoading}
            isLoadingData={isLoadingData}
            onSelectTable={fetchTableData}
          />
        )}
        {activeTab === 'backup' && (
          <BackupTab token={token!} backups={backups} onRefresh={fetchBackups} />
        )}
        {activeTab === 'cleanup' && (
          <CleanupTab token={token!} tables={tables} onRefresh={fetchTables} />
        )}
        {activeTab === 'query' && <QueryTab token={token!} tables={tables} />}
      </div>
    </PageLayout>
  );
}

function TablesTab({
  tables,
  selectedTable,
  tableData,
  selectedTableInfo,
  isLoading,
  isLoadingData,
  onSelectTable,
}: {
  tables: TableInfo[];
  selectedTable: string | null;
  tableData: any[];
  selectedTableInfo: TableInfo | undefined;
  isLoading: boolean;
  isLoadingData: boolean;
  onSelectTable: (name: string) => void;
}) {
  return (
    <div className="grid md:grid-cols-4 gap-6">
      {/* Tables List */}
      <div className="card md:col-span-1">
        <h2 className="section-header">Tables</h2>
        {isLoading ? (
          <div className="space-y-2">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-10 bg-surface-hover rounded animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-1">
            {tables.map((table) => (
              <button
                key={table.name}
                onClick={() => onSelectTable(table.name)}
                className={`w-full flex items-center justify-between p-3 rounded-lg text-left transition-colors ${
                  selectedTable === table.name
                    ? 'bg-ice/20 text-ice'
                    : 'hover:bg-surface text-frost-muted hover:text-frost'
                }`}
              >
                <span className="font-medium">{table.name}</span>
                <span className="text-xs bg-surface px-2 py-0.5 rounded">{table.row_count}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Table Data */}
      <div className="card md:col-span-3">
        {!selectedTable ? (
          <div className="text-center py-16">
            <div className="text-4xl mb-4">🗄️</div>
            <p className="text-frost-muted">Select a table to view its data</p>
          </div>
        ) : isLoadingData ? (
          <div className="space-y-4">
            <div className="h-8 bg-surface-hover rounded w-48 animate-pulse" />
            <div className="h-64 bg-surface-hover rounded animate-pulse" />
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-frost">{selectedTable}</h2>
              <span className="text-sm text-frost-muted">
                Showing {tableData.length} of {selectedTableInfo?.row_count} rows
              </span>
            </div>

            {tableData.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-frost-muted">No data in this table</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-surface-border">
                      {Object.keys(tableData[0]).map((col) => (
                        <th key={col} className="text-left p-2 text-frost-muted font-medium whitespace-nowrap">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tableData.map((row, i) => (
                      <tr key={i} className="border-b border-surface-border/50 hover:bg-surface/50">
                        {Object.values(row).map((val: any, j) => (
                          <td key={j} className="p-2 text-frost max-w-[200px] truncate">
                            {val === null ? (
                              <span className="text-frost-muted italic">null</span>
                            ) : typeof val === 'boolean' ? (
                              <span className={val ? 'text-success' : 'text-error'}>
                                {val.toString()}
                              </span>
                            ) : typeof val === 'object' ? (
                              <span className="text-frost-muted">{JSON.stringify(val)}</span>
                            ) : (
                              String(val)
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function BackupTab({
  token,
  backups,
  onRefresh,
}: {
  token: string;
  backups: BackupInfo[];
  onRefresh: () => void;
}) {
  const [isCreating, setIsCreating] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleCreateBackup = async () => {
    setIsCreating(true);
    setMessage(null);
    try {
      const res = await fetch('http://localhost:8000/api/admin/database/backup', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setMessage({ type: 'success', text: 'Backup created successfully!' });
        onRefresh();
      } else {
        setMessage({ type: 'error', text: 'Failed to create backup' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to create backup' });
    } finally {
      setIsCreating(false);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="section-header">Create Backup</h2>
        <p className="text-sm text-frost-muted mb-4">
          Create a backup of the current database state. Backups are stored on the server.
        </p>
        <button
          onClick={handleCreateBackup}
          disabled={isCreating}
          className="btn-primary"
        >
          {isCreating ? 'Creating...' : 'Create Backup Now'}
        </button>
        {message && (
          <p className={`mt-4 text-sm ${message.type === 'success' ? 'text-success' : 'text-error'}`}>
            {message.text}
          </p>
        )}
      </div>

      <div className="card">
        <h2 className="section-header">Existing Backups</h2>
        {backups.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">📦</div>
            <p className="text-frost-muted">No backups found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {backups.map((backup) => (
              <div
                key={backup.filename}
                className="p-4 rounded-lg bg-surface flex items-center justify-between"
              >
                <div>
                  <p className="font-medium text-frost">{backup.filename}</p>
                  <p className="text-xs text-frost-muted mt-1">
                    {formatDate(backup.created_at)} · {formatSize(backup.size_bytes)}
                  </p>
                </div>
                <button className="text-sm text-ice hover:underline">Download</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function CleanupTab({
  token,
  tables,
  onRefresh,
}: {
  token: string;
  tables: TableInfo[];
  onRefresh: () => void;
}) {
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const cleanupActions = [
    {
      id: 'orphaned_sessions',
      name: 'Clean Expired Sessions',
      description: 'Remove sessions older than 30 days',
      dangerous: false,
    },
    {
      id: 'old_logs',
      name: 'Clean Old Audit Logs',
      description: 'Remove audit logs older than 90 days',
      dangerous: false,
    },
    {
      id: 'unused_profiles',
      name: 'Clean Unused Profiles',
      description: 'Remove profiles with no activity in 6 months',
      dangerous: true,
    },
    {
      id: 'vacuum',
      name: 'Vacuum Database',
      description: 'Reclaim disk space and optimize database',
      dangerous: false,
    },
  ];

  const handleCleanup = async (actionId: string) => {
    setIsRunning(true);
    setMessage(null);
    try {
      const res = await fetch(`http://localhost:8000/api/admin/database/cleanup/${actionId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setMessage({ type: 'success', text: data.message || 'Cleanup completed!' });
        onRefresh();
      } else {
        setMessage({ type: 'error', text: 'Cleanup failed' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Cleanup failed' });
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="section-header">Database Cleanup</h2>
        <p className="text-sm text-frost-muted mb-4">
          Run maintenance tasks to keep the database clean and optimized.
        </p>
        {message && (
          <p className={`mb-4 text-sm ${message.type === 'success' ? 'text-success' : 'text-error'}`}>
            {message.text}
          </p>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {cleanupActions.map((action) => (
          <div
            key={action.id}
            className={`card ${action.dangerous ? 'border-error/30 bg-error/5' : ''}`}
          >
            <h3 className="font-medium text-frost mb-2">{action.name}</h3>
            <p className="text-sm text-frost-muted mb-4">{action.description}</p>
            <button
              onClick={() => handleCleanup(action.id)}
              disabled={isRunning}
              className={action.dangerous ? 'btn-primary bg-error hover:bg-error/80' : 'btn-secondary'}
            >
              {isRunning ? 'Running...' : 'Run'}
            </button>
          </div>
        ))}
      </div>

      {/* Database Stats */}
      <div className="card">
        <h2 className="section-header">Database Statistics</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-ice">{tables.length}</p>
            <p className="text-xs text-frost-muted">Tables</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-frost">
              {tables.reduce((sum, t) => sum + t.row_count, 0).toLocaleString()}
            </p>
            <p className="text-xs text-frost-muted">Total Rows</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-success">—</p>
            <p className="text-xs text-frost-muted">Database Size</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-warning">—</p>
            <p className="text-xs text-frost-muted">Last Vacuum</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function QueryTab({ token, tables }: { token: string; tables: TableInfo[] }) {
  const [query, setQuery] = useState('SELECT * FROM users LIMIT 10;');
  const [results, setResults] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const handleRunQuery = async () => {
    setIsRunning(true);
    setError(null);
    setResults(null);
    try {
      const res = await fetch('http://localhost:8000/api/admin/database/query', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      if (res.ok) {
        setResults(data.results || []);
      } else {
        setError(data.error || 'Query failed');
      }
    } catch (err) {
      setError('Failed to execute query');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="card border-warning/30 bg-warning/5">
        <div className="flex gap-3">
          <span className="text-2xl">⚠️</span>
          <div>
            <h3 className="font-medium text-frost">Read-Only Queries</h3>
            <p className="text-sm text-frost-muted mt-1">
              Only SELECT queries are allowed. Modifications must be done through the API.
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="section-header">SQL Query</h2>
        <div className="mb-4">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="input font-mono text-sm"
            rows={5}
            placeholder="SELECT * FROM users LIMIT 10;"
          />
        </div>
        <div className="flex gap-4">
          <button
            onClick={handleRunQuery}
            disabled={isRunning || !query.trim()}
            className="btn-primary"
          >
            {isRunning ? 'Running...' : 'Run Query'}
          </button>
          <div className="flex-1">
            <p className="text-xs text-frost-muted">
              Available tables: {tables.map((t) => t.name).join(', ')}
            </p>
          </div>
        </div>
      </div>

      {/* Results */}
      {error && (
        <div className="card border-error/30 bg-error/5">
          <p className="text-error">{error}</p>
        </div>
      )}

      {results && (
        <div className="card">
          <h2 className="section-header">Results ({results.length} rows)</h2>
          {results.length === 0 ? (
            <p className="text-frost-muted text-center py-8">No results</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-surface-border">
                    {Object.keys(results[0]).map((col) => (
                      <th key={col} className="text-left p-2 text-frost-muted font-medium">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {results.map((row, i) => (
                    <tr key={i} className="border-b border-surface-border/50">
                      {Object.values(row).map((val: any, j) => (
                        <td key={j} className="p-2 text-frost">
                          {val === null ? (
                            <span className="text-frost-muted italic">null</span>
                          ) : (
                            String(val)
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
