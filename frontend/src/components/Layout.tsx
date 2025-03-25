import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { usePsuu } from '@/contexts/PsuuContext';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const { state } = usePsuu();
  
  // Navigation items
  const navItems = [
    { 
      name: 'Model Connection', 
      path: '/', 
      step: 'connection', 
      enabled: true 
    },
    { 
      name: 'Parameters', 
      path: '/parameters', 
      step: 'parameters', 
      enabled: state.isConnected 
    },
    { 
      name: 'KPIs', 
      path: '/kpis', 
      step: 'kpis', 
      enabled: state.isConnected && state.parameters.length > 0 
    },
    { 
      name: 'Optimization', 
      path: '/optimization', 
      step: 'optimization', 
      enabled: state.isConnected && state.parameters.length > 0 && state.kpis.length > 0
    },
    { 
      name: 'Results', 
      path: '/results', 
      step: 'results', 
      enabled: state.optimizationResults !== null
    },
    {
      name: 'API Docs',
      path: '/api-docs',
      step: 'docs',
      enabled: true
    }
  ];
  
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-slate-800 text-white shadow-md">
        <div className="container mx-auto py-4 px-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold">PSUU</h1>
              <span className="text-sm text-slate-300">Parameter Selection Under Uncertainty</span>
            </div>
          </div>
        </div>
      </header>
      
      <nav className="bg-slate-700 text-white shadow-md">
        <div className="container mx-auto px-6">
          <div className="flex space-x-4">
            {navItems.map((item) => (
              <Link 
                key={item.path} 
                href={item.enabled ? item.path : '#'}
                className={`
                  py-3 px-4 
                  ${item.enabled ? 'cursor-pointer' : 'cursor-not-allowed opacity-50'} 
                  ${router.pathname === item.path ? 'bg-slate-600 font-medium' : 'hover:bg-slate-600'}
                  transition-colors duration-150
                  ${item.path === '/api-docs' ? 'ml-auto' : ''}
                `}
              >
                {item.name}
              </Link>
            ))}
          </div>
        </div>
      </nav>
      
      <main className="flex-grow bg-slate-50">
        <div className="container mx-auto py-6 px-6">
          {children}
        </div>
      </main>
      
      <footer className="bg-slate-800 text-white py-4">
        <div className="container mx-auto px-6">
          <div className="text-sm text-center">
            <p>PSUU Frontend v0.1.0</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
