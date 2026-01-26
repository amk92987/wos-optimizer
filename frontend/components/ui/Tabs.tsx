'use client';

import { useState, useEffect } from 'react';

interface Tab {
  id: string;
  label: string;
  icon?: string;
  badge?: number;
}

interface TabsProps {
  tabs: Tab[];
  activeTab?: string;
  onChange?: (tabId: string) => void;
  children?: React.ReactNode;
  className?: string;
}

export default function Tabs({
  tabs,
  activeTab,
  onChange,
  children,
  className = '',
}: TabsProps) {
  const [selected, setSelected] = useState(activeTab || tabs[0]?.id);

  useEffect(() => {
    if (activeTab) {
      setSelected(activeTab);
    }
  }, [activeTab]);

  const handleTabClick = (tabId: string) => {
    setSelected(tabId);
    onChange?.(tabId);
  };

  return (
    <div className={className}>
      {/* Tab list */}
      <div className="tabs mb-4 scrollbar-hide">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabClick(tab.id)}
            className={selected === tab.id ? 'tab-active' : 'tab'}
          >
            {tab.icon && <span className="mr-2">{tab.icon}</span>}
            {tab.label}
            {tab.badge !== undefined && tab.badge > 0 && (
              <span className="ml-2 px-1.5 py-0.5 text-xs bg-fire/20 text-fire rounded-full">
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {children && (
        <div className="animate-fade-in">
          {children}
        </div>
      )}
    </div>
  );
}

// Tab panel component for controlled content
interface TabPanelProps {
  id: string;
  activeTab: string;
  children: React.ReactNode;
}

export function TabPanel({ id, activeTab, children }: TabPanelProps) {
  if (id !== activeTab) return null;
  return <div className="animate-fade-in">{children}</div>;
}
