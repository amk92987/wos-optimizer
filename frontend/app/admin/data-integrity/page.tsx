'use client';

import { useEffect, useState } from 'react';
import PageLayout from '@/components/PageLayout';
import { useAuth } from '@/lib/auth';
import { adminApi } from '@/lib/api';

interface IntegrityCheck {
  name: string;
  description: string;
  status: 'pass' | 'warn' | 'fail';
  details: string;
  count?: number;
  affected_ids?: string[];
  fix_action?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
}

export default function AdminDataIntegrityPage() {
  const { token, user } = useAuth();
  const [checks, setChecks] = useState<IntegrityCheck[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastRun, setLastRun] = useState<string | null>(null);
  const [expandedCheck, setExpandedCheck] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
  const [isFixing, setIsFixing] = useState(false);

  useEffect(() => {
    if (token) {
      runChecks();
    }
  }, [token]);

  const runChecks = async () => {
    setIsLoading(true);
    setActionMessage(null);
    try {
      const data = await adminApi.checkDataIntegrity(token!);
      const rawChecks = (data as any).checks || [];
      // Map raw check data to our interface
      setChecks(rawChecks.map ? rawChecks.map((c: any) => ({
        name: c.name || c.file || 'Unknown',
        description: c.description || '',
        status: c.status || (c.exists && c.valid_json ? 'pass' : 'fail'),
        details: c.details || (c.exists ? 'File exists' : 'File missing'),
        count: c.count ?? (c.size_bytes ? 1 : 0),
        affected_ids: c.affected_ids || [],
        fix_action: c.fix_action || null,
        severity: c.severity || (c.status === 'fail' ? 'high' : c.status === 'warn' ? 'medium' : 'low'),
      })) : []);
      setLastRun(new Date().toISOString());
    } catch (error) {
      console.error('Failed to run integrity checks:', error);
      setChecks([]);
      setActionMessage({ type: 'error', text: 'Failed to run integrity checks. The backend may be unavailable.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = async (action: string, label: string) => {
    setIsFixing(true);
    setActionMessage(null);
    try {
      const result = await adminApi.fixIntegrityIssue(token!, action);
      setActionMessage({
        type: 'success',
        text: (result as any).message || `${label} completed successfully. Fixed: ${(result as any).fixed || 0} items.`,
      });
      // Re-run checks after fix
      await runChecks();
    } catch (error: any) {
      setActionMessage({
        type: 'error',
        text: error?.message || `${label} failed. The endpoint may not be implemented yet.`,
      });
    } finally {
      setIsFixing(false);
    }
  };

  const handleFixAllSafe = async () => {
    setIsFixing(true);
    setActionMessage(null);
    const safeChecks = checks.filter(
      (c) => c.status !== 'pass' && c.fix_action && (c.severity === 'low' || c.severity === 'medium')
    );
    if (safeChecks.length === 0) {
      setActionMessage({ type: 'info', text: 'No safe issues to fix. All checks are passing or require manual intervention.' });
      setIsFixing(false);
      return;
    }

    let fixedCount = 0;
    for (const check of safeChecks) {
      try {
        await adminApi.fixIntegrityIssue(token!, check.fix_action!);
        fixedCount++;
      } catch {
        // continue with other fixes
      }
    }
    setActionMessage({
      type: fixedCount > 0 ? 'success' : 'info',
      text: `Fixed ${fixedCount} of ${safeChecks.length} safe issues.`,
    });
    await runChecks();
    setIsFixing(false);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const severityConfig = {
    low: { icon: 'i', color: 'text-frost-muted', bgColor: 'bg-frost-muted/10' },
    medium: { icon: '!', color: 'text-warning', bgColor: 'bg-warning/10' },
    high: { icon: '!!', color: 'text-error', bgColor: 'bg-error/10' },
    critical: { icon: '!!!', color: 'text-error', bgColor: 'bg-error/20' },
  };

  const statusColors = {
    pass: 'border-success/20 bg-success/5',
    warn: 'border-warning/20 bg-warning/5',
    fail: 'border-error/20 bg-error/5',
  };

  const statusTextColors = {
    pass: 'text-success',
    warn: 'text-warning',
    fail: 'text-error',
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

  const passCount = checks.filter((c) => c.status === 'pass').length;
  const warnCount = checks.filter((c) => c.status === 'warn').length;
  const failCount = checks.filter((c) => c.status === 'fail').length;

  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto animate-fadeIn">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-frost">Data Integrity</h1>
            <p className="text-frost-muted mt-1">Validate database and file consistency</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleFixAllSafe}
              disabled={isLoading || isFixing}
              className="btn-secondary"
            >
              {isFixing ? 'Fixing...' : 'Fix All Safe Issues'}
            </button>
            <button onClick={runChecks} disabled={isLoading} className="btn-primary">
              {isLoading ? 'Running...' : 'Run Checks'}
            </button>
          </div>
        </div>

        {/* Action Message */}
        {actionMessage && (
          <div className={`mb-6 p-4 rounded-lg text-sm border ${
            actionMessage.type === 'success'
              ? 'bg-success/10 text-success border-success/30'
              : actionMessage.type === 'error'
                ? 'bg-error/10 text-error border-error/30'
                : 'bg-ice/10 text-ice border-ice/30'
          }`}>
            {actionMessage.text}
          </div>
        )}

        {/* Summary */}
        {!isLoading && checks.length > 0 && (
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="card text-center border-success/30 bg-success/5">
              <p className="text-3xl font-bold text-success">{passCount}</p>
              <p className="text-sm text-frost-muted">Passed</p>
            </div>
            <div className="card text-center border-warning/30 bg-warning/5">
              <p className="text-3xl font-bold text-warning">{warnCount}</p>
              <p className="text-sm text-frost-muted">Warnings</p>
            </div>
            <div className="card text-center border-error/30 bg-error/5">
              <p className="text-3xl font-bold text-error">{failCount}</p>
              <p className="text-sm text-frost-muted">Failed</p>
            </div>
          </div>
        )}

        {/* Checks List */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-header mb-0">Integrity Checks</h2>
            {lastRun && (
              <span className="text-xs text-frost-muted">Last run: {formatDate(lastRun)}</span>
            )}
          </div>

          {isLoading ? (
            <div className="space-y-4">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="p-4 rounded-lg bg-surface animate-pulse">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-surface-hover" />
                    <div className="flex-1">
                      <div className="h-4 bg-surface-hover rounded w-48 mb-2" />
                      <div className="h-3 bg-surface-hover rounded w-64" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {checks.map((check) => {
                const severity = check.severity || 'low';
                const sevConfig = severityConfig[severity];
                const isExpanded = expandedCheck === check.name;

                return (
                  <div key={check.name}>
                    <button
                      onClick={() => setExpandedCheck(isExpanded ? null : check.name)}
                      className={`w-full p-4 rounded-lg border text-left transition-all ${statusColors[check.status]} ${
                        isExpanded ? 'rounded-b-none' : ''
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        {/* Severity icon */}
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${sevConfig.bgColor} ${sevConfig.color}`}>
                          {severity === 'low' && (
                            <span className={statusTextColors[check.status]}>OK</span>
                          )}
                          {severity === 'medium' && (
                            <span className="text-warning">!</span>
                          )}
                          {severity === 'high' && (
                            <span className="text-error">!!</span>
                          )}
                          {severity === 'critical' && (
                            <span className="text-error font-black">!!!</span>
                          )}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h3 className="font-medium text-frost">{check.name}</h3>
                            {check.count !== undefined && (
                              <span className="text-xs bg-surface px-2 py-0.5 rounded text-frost-muted">
                                Found: {check.count}
                              </span>
                            )}
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              severity === 'critical' ? 'bg-error/20 text-error' :
                              severity === 'high' ? 'bg-error/10 text-error' :
                              severity === 'medium' ? 'bg-warning/10 text-warning' :
                              'bg-frost-muted/10 text-frost-muted'
                            }`}>
                              {severity}
                            </span>
                          </div>
                          <p className="text-sm text-frost-muted mt-1">{check.description}</p>
                          <p className="text-sm text-frost mt-2">{check.details}</p>
                        </div>
                        <span className="text-frost-muted text-xs mt-1">
                          {isExpanded ? '[-]' : '[+]'}
                        </span>
                      </div>
                    </button>

                    {/* Expanded Details */}
                    {isExpanded && (
                      <div className={`p-4 rounded-b-lg border border-t-0 ${statusColors[check.status]}`}>
                        {check.affected_ids && check.affected_ids.length > 0 ? (
                          <div>
                            <p className="text-xs text-frost-muted uppercase tracking-wide mb-2">Affected Record IDs</p>
                            <div className="flex flex-wrap gap-2">
                              {check.affected_ids.map((id) => (
                                <span
                                  key={id}
                                  className="text-xs font-mono bg-surface px-2 py-1 rounded text-frost-muted"
                                >
                                  {id}
                                </span>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <p className="text-sm text-frost-muted">
                            {check.status === 'pass'
                              ? 'No issues found. All records are valid.'
                              : 'No specific record IDs available for this check.'}
                          </p>
                        )}

                        {check.fix_action && check.status !== 'pass' && (
                          <div className="mt-3 pt-3 border-t border-surface-border">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleQuickAction(check.fix_action!, check.name);
                              }}
                              disabled={isFixing}
                              className="btn-secondary text-sm"
                            >
                              {isFixing ? 'Fixing...' : `Fix: ${check.name}`}
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

      </div>
    </PageLayout>
  );
}
