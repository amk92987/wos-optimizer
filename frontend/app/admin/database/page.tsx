'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi } from '@/lib/api';

interface EntityInfo {
  id: string;
  label: string;
  table: string;
  row_count: number;
  columns: string[];
}

export default function AdminDatabasePage() {
  const { token, user } = useAuth();
  const [entities, setEntities] = useState<EntityInfo[]>([]);
  const [selectedEntity, setSelectedEntity] = useState<string | null>(null);
  const [entityData, setEntityData] = useState<any[]>([]);
  const [entityColumns, setEntityColumns] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingData, setIsLoadingData] = useState(false);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(25);

  useEffect(() => {
    if (token) {
      fetchEntities();
    }
  }, [token]);

  const fetchEntities = async () => {
    try {
      const data = await adminApi.listEntities(token!);
      setEntities(data.entities || []);
    } catch (error) {
      console.error('Failed to fetch entities:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchEntityData = async (entityId: string) => {
    setIsLoadingData(true);
    setSelectedEntity(entityId);
    setCurrentPage(1);
    try {
      const data = await adminApi.browseEntity(token!, entityId, 500);
      setEntityData(data.items || []);
      setEntityColumns(data.columns || []);
    } catch (error) {
      console.error('Failed to fetch entity data:', error);
    } finally {
      setIsLoadingData(false);
    }
  };

  const handleExportCSV = () => {
    if (!selectedEntity || entityData.length === 0) return;

    const headers = entityColumns;
    const csvRows = [
      headers.join(','),
      ...entityData.map((row) =>
        headers.map((h) => {
          const val = row[h];
          if (val === null || val === undefined) return '';
          const str = typeof val === 'object' ? JSON.stringify(val) : String(val);
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
    a.download = `${selectedEntity}_export.csv`;
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

  const totalEntities = entities.length;
  const totalItems = entities.reduce((sum, e) => sum + (e.row_count >= 0 ? e.row_count : 0), 0);
  const selectedEntityInfo = entities.find((e) => e.id === selectedEntity);

  // Pagination
  const totalPages = Math.max(1, Math.ceil(entityData.length / rowsPerPage));
  const startIdx = (currentPage - 1) * rowsPerPage;
  const endIdx = Math.min(startIdx + rowsPerPage, entityData.length);
  const paginatedData = entityData.slice(startIdx, endIdx);

  // Format column header for display
  const formatColHeader = (col: string) =>
    col.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <PageLayout>
      <div className="max-w-6xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Data Browser</h1>
          <p className="text-frost-muted mt-1">Browse application data by entity type</p>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="card text-center">
            <p className="text-2xl font-bold text-ice">{totalEntities}</p>
            <p className="text-xs text-frost-muted">Entity Types</p>
          </div>
          <div className="card text-center">
            <p className="text-2xl font-bold text-frost">{totalItems.toLocaleString()}</p>
            <p className="text-xs text-frost-muted">Total Records</p>
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-6">
          {/* Entity List */}
          <div className="card md:col-span-1">
            <h2 className="section-header">Entities</h2>
            {isLoading ? (
              <div className="space-y-2">
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="h-10 bg-surface-hover rounded animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="space-y-1">
                {entities.map((entity) => (
                  <button
                    key={entity.id}
                    onClick={() => fetchEntityData(entity.id)}
                    className={`w-full flex items-center justify-between p-3 rounded-lg text-left transition-colors ${
                      selectedEntity === entity.id
                        ? 'bg-ice/20 text-ice'
                        : 'hover:bg-surface text-frost-muted hover:text-frost'
                    }`}
                  >
                    <div>
                      <span className="font-medium text-sm">{entity.label}</span>
                      <span className="block text-xs text-frost-muted">{entity.table}</span>
                    </div>
                    <span className="text-xs bg-surface px-2 py-0.5 rounded">
                      {entity.row_count >= 0 ? entity.row_count : '?'}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Data Table */}
          <div className="card md:col-span-3">
            {!selectedEntity ? (
              <div className="text-center py-16">
                <div className="text-4xl mb-4">&#x1F5C4;&#xFE0F;</div>
                <p className="text-frost-muted">Select an entity type to browse its data</p>
              </div>
            ) : isLoadingData ? (
              <div className="space-y-4">
                <div className="h-8 bg-surface-hover rounded w-48 animate-pulse" />
                <div className="h-64 bg-surface-hover rounded animate-pulse" />
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-bold text-frost">{selectedEntityInfo?.label}</h2>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-frost-muted">
                      {entityData.length > 0
                        ? `Showing ${startIdx + 1}-${endIdx} of ${entityData.length} rows`
                        : 'No rows'}
                    </span>
                    <button onClick={handleExportCSV} className="btn-secondary text-sm" disabled={entityData.length === 0}>
                      Export CSV
                    </button>
                  </div>
                </div>

                {entityData.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-frost-muted">No data for this entity type</p>
                  </div>
                ) : (
                  <>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-surface-border">
                            {entityColumns.map((col) => (
                              <th key={col} className="text-left p-2 text-frost-muted font-medium whitespace-nowrap">
                                {formatColHeader(col)}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {paginatedData.map((row, i) => (
                            <tr key={i} className="border-b border-surface-border/50 hover:bg-surface/50">
                              {entityColumns.map((col) => {
                                const val = row[col];
                                return (
                                  <td key={col} className="p-2 text-frost max-w-[250px] truncate">
                                    {val === null || val === undefined ? (
                                      <span className="text-frost-muted italic">--</span>
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
                                );
                              })}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Pagination */}
                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-surface-border">
                      <div className="flex items-center gap-2">
                        <label className="text-xs text-frost-muted">Rows per page:</label>
                        <select
                          value={rowsPerPage}
                          onChange={(e) => {
                            setRowsPerPage(Number(e.target.value));
                            setCurrentPage(1);
                          }}
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
                          onClick={() => setCurrentPage(1)}
                          disabled={currentPage <= 1}
                          className="px-2 py-1 rounded text-sm text-frost-muted hover:text-frost hover:bg-surface disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                          First
                        </button>
                        <button
                          onClick={() => setCurrentPage(currentPage - 1)}
                          disabled={currentPage <= 1}
                          className="px-2 py-1 rounded text-sm text-frost-muted hover:text-frost hover:bg-surface disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                          Prev
                        </button>
                        <span className="px-3 py-1 text-sm text-frost">
                          Page {currentPage} of {totalPages}
                        </span>
                        <button
                          onClick={() => setCurrentPage(currentPage + 1)}
                          disabled={currentPage >= totalPages}
                          className="px-2 py-1 rounded text-sm text-frost-muted hover:text-frost hover:bg-surface disabled:opacity-30 disabled:cursor-not-allowed"
                        >
                          Next
                        </button>
                        <button
                          onClick={() => setCurrentPage(totalPages)}
                          disabled={currentPage >= totalPages}
                          className="px-2 py-1 rounded text-sm text-frost-muted hover:text-frost hover:bg-surface disabled:opacity-30 disabled:cursor-not-allowed"
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
      </div>
    </PageLayout>
  );
}
