'use client';

import { useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { api, API_BASE } from '@/lib/api';

interface ExportOption {
  id: string;
  name: string;
  description: string;
  icon: string;
  formats: string[];
}

const exportOptions: ExportOption[] = [
  {
    id: 'users',
    name: 'Users',
    description: 'All user accounts with profiles and settings',
    icon: '👥',
    formats: ['CSV', 'Excel', 'JSON'],
  },
  {
    id: 'heroes',
    name: 'User Heroes',
    description: 'All tracked heroes with levels, skills, and gear',
    icon: '🦸',
    formats: ['CSV', 'Excel', 'JSON'],
  },
  {
    id: 'ai_conversations',
    name: 'AI Conversations',
    description: 'AI chat history for training data',
    icon: '💬',
    formats: ['CSV', 'JSONL', 'JSON'],
  },
  {
    id: 'feedback',
    name: 'Feedback',
    description: 'User feedback and bug reports',
    icon: '📝',
    formats: ['CSV', 'Excel', 'JSON'],
  },
  {
    id: 'audit_log',
    name: 'Audit Log',
    description: 'User actions and system events',
    icon: '📋',
    formats: ['CSV', 'Excel', 'JSON'],
  },
  {
    id: 'game_data',
    name: 'Game Data',
    description: 'All game data JSON files as ZIP',
    icon: '🎮',
    formats: ['ZIP'],
  },
];

export default function AdminExportPage() {
  const { token, user } = useAuth();
  const [selectedExport, setSelectedExport] = useState<string | null>(null);
  const [selectedFormat, setSelectedFormat] = useState<string>('');
  const [isExporting, setIsExporting] = useState(false);
  const [exportResult, setExportResult] = useState<{ success: boolean; message: string } | null>(null);

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
          <div className="text-6xl mb-6">🔒</div>
          <h1 className="text-2xl font-bold text-frost mb-4">Access Denied</h1>
        </div>
      </PageLayout>
    );
  }

  const currentOption = exportOptions.find((o) => o.id === selectedExport);

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-frost">Export Data</h1>
          <p className="text-frost-muted mt-1">Download data in various formats</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Export Options */}
          <div className="card">
            <h2 className="section-header">Select Data to Export</h2>
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
                <div className="text-4xl mb-4">📤</div>
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
            Bulk exports may take longer to generate. You'll receive a download link when ready.
          </p>
        </div>

        {/* Warning */}
        <div className="card mt-6 border-warning/30 bg-warning/5">
          <div className="flex gap-3">
            <span className="text-2xl">⚠️</span>
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
