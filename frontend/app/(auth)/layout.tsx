// Auth pages layout (landing, login, register)
// Landing page is full-width, login/register are centered

'use client';

import { usePathname } from 'next/navigation';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isLanding = pathname === '/landing';

  // Landing page gets full control of its layout
  if (isLanding) {
    return <>{children}</>;
  }

  // Login/Register pages are centered
  return (
    <div className="min-h-screen min-h-[100dvh] flex flex-col items-center justify-center p-4 safe-top safe-bottom">
      <div className="w-full max-w-md">
        {children}
      </div>
    </div>
  );
}
