'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi, API_BASE } from '@/lib/api';

interface ExportOption {
  id: string;
  name: string;
  description: string;
  icon: string;
  formats: string[];
}

interface ReportType {
  id: string;
  name: string;
  description: string;
  columns: string[];
}

const reportTypes: ReportType[] = [
  {
    id: 'user_summary',
    name: 'User Summary',
    description: 'Users with their profiles, states, and hero counts',
    columns: ['Username', 'Email', 'Role', 'State', 'Is Active', 'Created', 'Last Login', 'Profile Name', 'Heroes Tracked'],
  },
  {
    id: 'activity',
    name: 'Activity Report',
    description: 'User login activity and engagement status',
    columns: ['Username', 'Status', 'Last Login', 'Days Since Login', 'Account Created'],
  },
  {
    id: 'content_stats',
    name: 'Content Statistics',
    description: 'Profile details with game progression data',
    columns: ['Profile Name', 'Username', 'State', 'Server Age', 'Furnace Level', 'Spending Profile', 'Alliance Role', 'Heroes Tracked', 'Inventory Items'],
  },
  {
    id: 'hero_usage',
    name: 'Hero Usage',
    description: 'Which heroes are tracked by the most users',
    columns: ['Hero', 'Class', 'Rarity', 'Generation', 'Users Tracking'],
  },
  {
    id: 'growth',
    name: 'Growth Metrics',
    description: 'Daily snapshots of user and content growth',
    columns: ['Date', 'Total Users', 'New Users', 'Active Users', 'Total Profiles', 'Heroes Tracked', 'Inventory Items'],
  },
];

const exportOptions: ExportOption[] = [
  {
    id: 'users',
    name: 'Users',
    description: 'All user accounts with profiles and settings',
    icon: '\uD83D\uDC65',
    formats: ['CSV', 'Excel', 'JSON'],
  },
  {
    id: 'heroes',
    name: 'User Heroes',
    description: 'All tracked heroes with levels, skills, and gear',
    icon: '\uD83E\uDDB8',
    formats: ['CSV', 'Excel', 'JSON'],
  },
  {
    id: 'ai_conversations',
    name: 'AI Conversations',
    description: 'AI chat history for training data',
    icon: '\uD83D\uDCAC',
    formats: ['CSV', 'JSONL', 'JSON'],
  },
  {
    id: 'feedback',
    name: 'Feedback',
    description: 'User feedback and bug reports',
    icon: '\uD83D\uDCDD',
    formats: ['CSV', 'Excel', 'JSON'],
  },
  {
    id: 'audit_log',
    name: 'Audit Log',
    description: 'User actions and system events',
    icon: '\uD83D\uDCCB',
    formats: ['CSV', 'Excel', 'JSON'],
  },
  {
    id: 'game_data',
    name: 'Game Data',
    description: 'All game data JSON files as ZIP',
    icon: '\uD83C\uDFAE',
    formats: ['ZIP'],
  },
];

function getDefaultDateRange(): { start: string; end: string } {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 30);
  return {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0],
  };
}

export default function AdminExportPage() {
  const { token, user } = useAuth();

  // Report state
  const [selectedReport, setSelectedReport] = useState<string>(reportTypes[0].id);
  const [startDate, setStartDate] = useState<string>(getDefaultDateRange().start);
  const [endDate, setEndDate] = useState<string>(getDefaultDateRange().end);
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportRows, setReportRows] = useState<Record<string, any>[] | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);

  // Export state
  const [selectedExport, setSelectedExport] = useState<string | null>(null);
  const [selectedFormat, setSelectedFormat] = useState<string>('');
  const [isExporting, setIsExporting] = useState(false);
  const [exportResult, setExportResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleGenerateReport = async () => {
    if (!token) return;
    setIsGenerating(true);
    setReportError(null);
    setReportRows(null);

    try {
      const result = await adminApi.generateReport(token, selectedReport, startDate, endDate);
      setReportRows(result.rows);
      if (result.rows.length === 0) {
        setReportError('No data found for the selected date range.');
      }
    } catch (error: any) {
      setReportError(error.message || 'Failed to generate report');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadCsv = async () => {
    if (!token || !reportRows || reportRows.length === 0) return;
    try {
      const result = await adminApi.downloadReportCsv(token, selectedReport, startDate, endDate);
      if (result.csv) {
        const blob = new Blob([result.csv], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = result.filename || `${selectedReport}_report.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('CSV download failed:', error);
    }
  };

  const handleDownloadExcel = async () => {
    // Excel download: use the same CSV data but with .xlsx extension hint
    // Since Lambda doesn't have openpyxl, we download CSV and let the user open in Excel
    if (!token || !reportRows || reportRows.length === 0) return;
    try {
      const result = await adminApi.downloadReportCsv(token, selectedReport, startDate, endDate);
      if (result.csv) {
        const blob = new Blob([result.csv], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        // Use .csv extension - Excel opens CSV natively
        a.download = result.filename || `${selectedReport}_report.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Excel download failed:', error);
    }
  };

  const handleExport = async () => {
    if (!selectedExport || !selectedFormat) return;

    setIsExporting(true);
    setExportResult(null);

    try {
      const res = await fetch(
        `${API_BASE}/api/admin/export/${selectedFormat.toLowerCase()}?table=${selectedExport}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedExport}_export.${selectedFormat.toLowerCase()}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        setExportResult({ success: true, message: 'Export downloaded successfully!' });
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      console.error('Export failed:', error);
      setExportResult({ success: false, message: 'Export failed. Please try again.' });
    } finally {
      setIsExporting(false);
    }
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

  const currentOption = exportOptions.find((o) => o.id === selectedExport);
  const currentReport = reportTypes.find((r) => r.id === selectedReport);
  const previewRows = reportRows ? reportRows.slice(0, 10) : [];
  const columns = reportRows && reportRows.length > 0 ? Object.keys(reportRows[0]) : (currentReport?.columns || []);

  return (
    <PageLayout>
      <div className="max-w-5xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Export Data</h1>
          <p className="text-frost-muted mt-1">Generate reports and download data in various formats</p>
        </div>

        {/* Reports Section */}
        <div className="card mb-6">
          <h2 className="section-header">Reports</h2>
          <p className="text-sm text-frost-muted mb-4">Generate custom reports with aggregated data from across the platform.</p>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Report Configuration */}
            <div className="space-y-4">
              {/* Report Type */}
              <div>
                <label className="block text-sm font-medium text-frost-muted mb-2">
                  Report Type
                </label>
                <select
                  value={selectedReport}
                  onChange={(e) => {
                    setSelectedReport(e.target.value);
                    setReportRows(null);
                    setReportError(null);
                  }}
                  className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-frost focus:outline-none focus:border-ice"
                >
                  {reportTypes.map((rt) => (
                    <option key={rt.id} value={rt.id}>
                      {rt.name}
                    </option>
                  ))}
                </select>
                {currentReport && (
                  <p className="text-xs text-frost-muted mt-1">{currentReport.description}</p>
                )}
              </div>

              {/* Date Range */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-frost-muted mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-frost focus:outline-none focus:border-ice"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-frost-muted mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface border border-border text-frost focus:outline-none focus:border-ice"
                  />
                </div>
              </div>

              {/* Generate Button */}
              <button
                onClick={handleGenerateReport}
                disabled={isGenerating}
                className="btn-primary w-full py-3"
              >
                {isGenerating ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Generating...
                  </span>
                ) : (
                  'Generate Report'
                )}
              </button>

              {/* Download Buttons */}
              {reportRows && reportRows.length > 0 && (
                <div className="flex gap-2">
                  <button
                    onClick={handleDownloadCsv}
                    className="btn-secondary flex-1 text-sm"
                  >
                    Download CSV
                  </button>
                  <button
                    onClick={handleDownloadExcel}
                    className="btn-secondary flex-1 text-sm"
                  >
                    Download Excel
                  </button>
                </div>
              )}

              {/* Error */}
              {reportError && (
                <div className="p-3 rounded-lg bg-error/20 border border-error/30 text-error text-sm">
                  {reportError}
                </div>
              )}
            </div>

            {/* Report Preview */}
            <div>
              <label className="block text-sm font-medium text-frost-muted mb-2">
                Preview {reportRows ? `(${reportRows.length} rows${reportRows.length > 10 ? ', showing first 10' : ''})` : ''}
              </label>
              <div className="rounded-lg border border-border bg-surface overflow-hidden" style={{ maxHeight: '360px' }}>
                {!reportRows ? (
                  <div className="flex items-center justify-center h-48 text-frost-muted text-sm">
                    Click "Generate Report" to preview data
                  </div>
                ) : reportRows.length === 0 ? (
                  <div className="flex items-center justify-center h-48 text-frost-muted text-sm">
                    No data found
                  </div>
                ) : (
                  <div className="overflow-auto" style={{ maxHeight: '360px' }}>
                    <table className="w-full text-xs">
                      <thead className="sticky top-0 bg-surface-hover">
                        <tr>
                          {columns.map((col) => (
                            <th
                              key={col}
                              className="px-2 py-1.5 text-left text-frost-muted font-medium whitespace-nowrap border-b border-border"
                            >
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {previewRows.map((row, i) => (
                          <tr key={i} className="border-b border-border/50 hover:bg-surface-hover/50">
                            {columns.map((col) => (
                              <td
                                key={col}
                                className="px-2 py-1.5 text-frost whitespace-nowrap max-w-[200px] truncate"
                                title={String(row[col] ?? '')}
                              >
                                {String(row[col] ?? '')}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
              {/* Columns info */}
              {currentReport && !reportRows && (
                <p className="text-xs text-frost-muted mt-2">
                  Columns: {currentReport.columns.join(', ')}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Raw Data Export Section */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Export Options */}
          <div className="card">
            <h2 className="section-header">Raw Data Export</h2>
            <div className="space-y-2">
              {exportOptions.map((option) => (
                <button
                  key={option.id}
                  onClick={() => {
                    setSelectedExport(option.id);
                    setSelectedFormat(option.formats[0]);
                    setExportResult(null);
                  }}
                  className={`w-full p-4 rounded-lg text-left transition-colors ${
                    selectedExport === option.id
                      ? 'bg-ice/20 border-2 border-ice'
                      : 'bg-surface hover:bg-surface-hover border-2 border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{option.icon}</span>
                    <div>
                      <p className="font-medium text-frost">{option.name}</p>
                      <p className="text-sm text-frost-muted">{option.description}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Export Settings */}
          <div className="card">
            <h2 className="section-header">Export Settings</h2>

            {!selectedExport ? (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">&#x1F4E4;</div>
                <p className="text-frost-muted">Select a data type to export</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Format Selection */}
                <div>
                  <label className="block text-sm font-medium text-frost-muted mb-3">
                    Export Format
                  </label>
                  <div className="flex gap-2">
                    {currentOption?.formats.map((format) => (
                      <button
                        key={format}
                        onClick={() => setSelectedFormat(format)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          selectedFormat === format
                            ? 'bg-ice text-background'
                            : 'bg-surface text-frost-muted hover:text-frost hover:bg-surface-hover'
                        }`}
                      >
                        {format}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Format Info */}
                <div className="p-4 rounded-lg bg-surface">
                  <h3 className="font-medium text-frost mb-2">Format Details</h3>
                  <p className="text-sm text-frost-muted">
                    {selectedFormat === 'CSV' && 'Comma-separated values, compatible with Excel and Google Sheets.'}
                    {selectedFormat === 'Excel' && 'Native Excel format (.xlsx) with formatted headers.'}
                    {selectedFormat === 'JSON' && 'JSON format, ideal for programmatic access and backups.'}
                    {selectedFormat === 'JSONL' && 'JSON Lines format, one record per line. Ideal for AI training.'}
                    {selectedFormat === 'ZIP' && 'Compressed archive containing all files.'}
                  </p>
                </div>

                {/* Export Button */}
                <button
                  onClick={handleExport}
                  disabled={isExporting || !selectedFormat}
                  className="btn-primary w-full py-3"
                >
                  {isExporting ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Exporting...
                    </span>
                  ) : (
                    `Export ${currentOption?.name} as ${selectedFormat}`
                  )}
                </button>

                {/* Result Message */}
                {exportResult && (
                  <div
                    className={`p-4 rounded-lg ${
                      exportResult.success
                        ? 'bg-success/20 border border-success/30 text-success'
                        : 'bg-error/20 border border-error/30 text-error'
                    }`}
                  >
                    {exportResult.message}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Bulk Export */}
        <div className="card mt-6">
          <h2 className="section-header">Bulk Export</h2>
          <div className="flex flex-wrap gap-4">
            <button className="btn-secondary">
              Export All User Data (ZIP)
            </button>
            <button className="btn-secondary">
              Full Database Backup
            </button>
            <button className="btn-secondary">
              Export AI Training Data (JSONL)
            </button>
          </div>
          <p className="text-xs text-frost-muted mt-4">
            Bulk exports may take longer to generate. You will receive a download link when ready.
          </p>
        </div>

        {/* Warning */}
        <div className="card mt-6 border-warning/30 bg-warning/5">
          <div className="flex gap-3">
            <span className="text-2xl">&#x26A0;&#xFE0F;</span>
            <div>
              <h3 className="font-medium text-frost">Data Privacy</h3>
              <p className="text-sm text-frost-muted mt-1">
                Exported data may contain personal information. Handle with care and ensure
                compliance with data protection regulations.
              </p>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
