'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi } from '@/lib/api';

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

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalRowCount, setTotalRowCount] = useState(0);

  useEffect(() => {
    if (token) {
      fetchTables();
      fetchBackups();
    }
  }, [token]);

  const fetchTables = async () => {
    try {
      const data = await adminApi.listTables(token!);
      setTables(Array.isArray(data.tables) ? data.tables as unknown as TableInfo[] : Array.isArray(data) ? data as unknown as TableInfo[] : []);
    } catch (error) {
      console.error('Failed to fetch tables:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchBackups = async () => {
    try {
      const data = await adminApi.getBackups(token!);
      setBackups(Array.isArray(data.backups) ? data.backups : Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch backups:', error);
    }
  };

  const fetchTableData = async (tableName: string, limit?: number) => {
    setIsLoadingData(true);
    setSelectedTable(tableName);
    setCurrentPage(1);
    const fetchLimit = limit || rowsPerPage;
    try {
      const data = await adminApi.scanTable(token!, tableName, 1000); // fetch all, paginate client-side
      const items = Array.isArray(data.items) ? data.items : Array.isArray(data) ? data : [];
      setTableData(items);
      const tableInfo = tables.find((t) => t.name === tableName);
      setTotalRowCount(tableInfo?.row_count || items.length);
    } catch (error) {
      console.error('Failed to fetch table data:', error);
    } finally {
      setIsLoadingData(false);
    }
  };

  const handleExportCSV = () => {
    if (!selectedTable || tableData.length === 0) return;

    const pageData = paginatedData;
    const headers = Object.keys(pageData[0]);
    const csvRows = [
      headers.join(','),
      ...pageData.map((row) =>
        headers.map((h) => {
          const val = row[h];
          if (val === null || val === undefined) return '';
          const str = typeof val === 'object' ? JSON.stringify(val) : String(val);
          // Escape commas and quotes
          return str.includes(',') || str.includes('"') || str.includes('\n')
            ? `"${str.replace(/"/g, '""')}"`
            : str;
        }).join(',')
      ),
    ];
    const csv = csvRows.join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedTable}_export.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  // Redirect non-admins
  if (user && user.role !== 'admin') {
    return (
      <PageLayout>
        <div className="max-w-2xl mx-auto text-center py-16">
          <div className="text-6xl mb-6">&#x1F512;</div>
          <h1 className="text-2xl font-bold text-frost mb-4">Access Denied</h1>
        </div>
      </PageLayout>
    );
  }

  const selectedTableInfo = tables.find((t) => t.name === selectedTable);
  const totalTableCount = tables.length;
  const totalItems = tables.reduce((sum, t) => sum + (t.row_count || 0), 0);

  // Pagination calculations
  const totalPages = Math.max(1, Math.ceil(tableData.length / rowsPerPage));
  const startIdx = (currentPage - 1) * rowsPerPage;
  const endIdx = startIdx + rowsPerPage;
  const paginatedData = tableData.slice(startIdx, endIdx);

  return (
    <PageLayout>
      <div className="max-w-6xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Database Browser</h1>
          <p className="text-frost-muted mt-1">View tables, manage backups, and run maintenance</p>
        </div>

        {/* DB Info Metrics */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="card text-center">
            <p className="text-2xl font-bold text-ice">{totalTableCount}</p>
            <p className="text-xs text-frost-muted">Tables</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-bold text-frost">{totalItems.toLocaleString()}</p>
            <p className="text-xs text-frost-muted">Total Items</p>
          </div>
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
            tableData={paginatedData}
            allTableData={tableData}
            selectedTableInfo={selectedTableInfo}
            isLoading={isLoading}
            isLoadingData={isLoadingData}
            onSelectTable={fetchTableData}
            onExportCSV={handleExportCSV}
            currentPage={currentPage}
            totalPages={totalPages}
            rowsPerPage={rowsPerPage}
            totalRowCount={tableData.length}
            startIdx={startIdx}
            endIdx={Math.min(endIdx, tableData.length)}
            onPageChange={setCurrentPage}
            onRowsPerPageChange={(val) => {
              setRowsPerPage(val);
              setCurrentPage(1);
            }}
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
  allTableData,
  selectedTableInfo,
  isLoading,
  isLoadingData,
  onSelectTable,
  onExportCSV,
  currentPage,
  totalPages,
  rowsPerPage,
  totalRowCount,
  startIdx,
  endIdx,
  onPageChange,
  onRowsPerPageChange,
}: {
  tables: TableInfo[];
  selectedTable: string | null;
  tableData: any[];
  allTableData: any[];
  selectedTableInfo: TableInfo | undefined;
  isLoading: boolean;
  isLoadingData: boolean;
  onSelectTable: (name: string) => void;
  onExportCSV: () => void;
  currentPage: number;
  totalPages: number;
  rowsPerPage: number;
  totalRowCount: number;
  startIdx: number;
  endIdx: number;
  onPageChange: (page: number) => void;
  onRowsPerPageChange: (val: number) => void;
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
            <div className="text-4xl mb-4">&#x1F5C4;&#xFE0F;</div>
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
              <div className="flex items-center gap-3">
                <span className="text-sm text-frost-muted">
                  {totalRowCount > 0
                    ? `Showing ${startIdx + 1}-${endIdx} of ${totalRowCount} rows`
                    : 'No rows'}
                </span>
                <button onClick={onExportCSV} className="btn-secondary text-sm" disabled={allTableData.length === 0}>
                  Export CSV
                </button>
              </div>
            </div>

            {tableData.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-frost-muted">No data in this table</p>
              </div>
            ) : (
              <>
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

                {/* Pagination Controls */}
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-surface-border">
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-frost-muted">Rows per page:</label>
                    <select
                      value={rowsPerPage}
                      onChange={(e) => onRowsPerPageChange(Number(e.target.value))}
                      className="input text-sm py-1 w-20"
                    >
                      <option value={10}>10</option>
                      <option value={25}>25</option>
                      <option value={50}>50</option>
                      <option value={100}>100</option>
                    </select>
                  </div>

                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => onPageChange(1)}
                      disabled={currentPage <= 1}
                      className="px-2 py-1 rounded text-sm text-frost-muted hover:text-frost hover:bg-surface disabled:opacity-30 disabled:cursor-not-allowed"
                      title="First page"
                    >
                      First
                    </button>
                    <button
                      onClick={() => onPageChange(currentPage - 1)}
                      disabled={currentPage <= 1}
                      className="px-2 py-1 rounded text-sm text-frost-muted hover:text-frost hover:bg-surface disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Previous page"
                    >
                      Prev
                    </button>
                    <span className="px-3 py-1 text-sm text-frost">
                      Page {currentPage} of {totalPages}
                    </span>
                    <button
                      onClick={() => onPageChange(currentPage + 1)}
                      disabled={currentPage >= totalPages}
                      className="px-2 py-1 rounded text-sm text-frost-muted hover:text-frost hover:bg-surface disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Next page"
                    >
                      Next
                    </button>
                    <button
                      onClick={() => onPageChange(totalPages)}
                      disabled={currentPage >= totalPages}
                      className="px-2 py-1 rounded text-sm text-frost-muted hover:text-frost hover:bg-surface disabled:opacity-30 disabled:cursor-not-allowed"
                      title="Last page"
                    >
                      Last
                    </button>
                  </div>
                </div>
              </>
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
      await adminApi.createBackup(token);
      setMessage({ type: 'success', text: 'Backup created successfully!' });
      onRefresh();
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
            <div className="text-4xl mb-4">&#x1F4E6;</div>
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
                    {formatDate(backup.created_at)} &middot; {formatSize(backup.size_bytes)}
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

  const [confirmDangerous, setConfirmDangerous] = useState<string | null>(null);

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
    {
      id: 'clear_feedback',
      name: 'Clear All Feedback',
      description: 'Delete all feedback entries from the database',
      dangerous: true,
    },
  ];

  const handleCleanup = async (actionId: string) => {
    setIsRunning(true);
    setMessage(null);
    setConfirmDangerous(null);
    try {
      let data: any;
      if (actionId === 'clear_feedback') {
        data = await adminApi.bulkFeedbackAction(token, 'delete_all');
      } else {
        data = await adminApi.databaseCleanup(token, actionId);
      }
      setMessage({ type: 'success', text: data?.message || 'Cleanup completed!' });
      onRefresh();
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
            {confirmDangerous === action.id ? (
              <div>
                <p className="text-sm text-warning mb-3">Are you sure? This action cannot be undone.</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleCleanup(action.id)}
                    disabled={isRunning}
                    className="btn-primary bg-error hover:bg-error/80"
                  >
                    {isRunning ? 'Running...' : 'Confirm'}
                  </button>
                  <button
                    onClick={() => setConfirmDangerous(null)}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => action.dangerous ? setConfirmDangerous(action.id) : handleCleanup(action.id)}
                disabled={isRunning}
                className={action.dangerous ? 'btn-primary bg-error hover:bg-error/80' : 'btn-secondary'}
              >
                {isRunning ? 'Running...' : 'Run'}
              </button>
            )}
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
            <p className="text-2xl font-bold text-success">&mdash;</p>
            <p className="text-xs text-frost-muted">Database Size</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-warning">&mdash;</p>
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
  const [showDestructiveWarning, setShowDestructiveWarning] = useState(false);

  const DESTRUCTIVE_KEYWORDS = /\b(drop|delete|update|truncate|alter|insert)\b/i;

  const isDestructiveQuery = (q: string): boolean => {
    return DESTRUCTIVE_KEYWORDS.test(q);
  };

  const handleRunQuery = async () => {
    // Check for destructive keywords
    if (isDestructiveQuery(query) && !showDestructiveWarning) {
      setShowDestructiveWarning(true);
      return;
    }

    setShowDestructiveWarning(false);
    setIsRunning(true);
    setError(null);
    setResults(null);
    try {
      const data: any = await adminApi.databaseQuery(token, query);
      if (data.error) {
        setError(data.error);
      } else {
        setResults(data.results || []);
      }
    } catch (err) {
      setError('Failed to execute query');
    } finally {
      setIsRunning(false);
    }
  };

  const handleQueryChange = (value: string) => {
    setQuery(value);
    // Reset the warning when the query changes
    if (showDestructiveWarning) {
      setShowDestructiveWarning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="card border-warning/30 bg-warning/5">
        <div className="flex gap-3">
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
            onChange={(e) => handleQueryChange(e.target.value)}
            className="input font-mono text-sm"
            rows={5}
            placeholder="SELECT * FROM users LIMIT 10;"
          />
        </div>

        {/* Destructive query warning */}
        {showDestructiveWarning && (
          <div className="mb-4 p-4 rounded-lg border border-error/30 bg-error/5">
            <p className="text-warning font-medium mb-2">Destructive Query Detected</p>
            <p className="text-sm text-frost-muted mb-3">
              This query contains potentially destructive keywords (DROP, DELETE, UPDATE, TRUNCATE, ALTER, INSERT).
              Are you sure you want to execute it?
            </p>
            <div className="flex gap-2">
              <button
                onClick={handleRunQuery}
                disabled={isRunning}
                className="btn-primary bg-error hover:bg-error/80"
              >
                {isRunning ? 'Running...' : 'Confirm Execute'}
              </button>
              <button
                onClick={() => setShowDestructiveWarning(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {!showDestructiveWarning && (
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
        )}
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
