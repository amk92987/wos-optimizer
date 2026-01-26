import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/lib/auth';
import { ServiceWorkerProvider } from '@/components/ServiceWorkerProvider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: "Bear's Den - Whiteout Survival Companion",
  description: 'Your Whiteout Survival companion app for hero tracking, AI recommendations, lineups, and strategy guides',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: "Bear's Den",
  },
  formatDetection: {
    telephone: false,
  },
  icons: {
    icon: '/icons/bear_paw.png',
    apple: '/icons/bear_paw.png',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: 'cover',
  themeColor: '#4A90D9',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="antialiased">
      <head>
        {/* PWA meta tags */}
        <meta name="application-name" content="Bear's Den" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="Bear's Den" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="msapplication-TileColor" content="#0A1628" />
        <meta name="msapplication-tap-highlight" content="no" />

        {/* Preconnect to API */}
        <link rel="preconnect" href="http://localhost:8000" />
      </head>
      <body className={`${inter.className} safe-top`}>
        <AuthProvider>
          <ServiceWorkerProvider>
            {children}
          </ServiceWorkerProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
