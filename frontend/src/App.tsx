import { useState } from 'react';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { CompaniesPage } from './pages/CompaniesPage';
import { AdminCompaniesPage } from './pages/AdminCompaniesPage';
import { LeadsPage } from './pages/LeadsPage';
import { ConfigPage } from './pages/ConfigPage';
import { AuthProvider, useAuth } from './contexts/AuthContext';

function MainApp() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const [currentRoute, setCurrentRoute] = useState<'dashboard' | 'empresas' | 'leads' | 'config'>('dashboard');

  if (isLoading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-[#FAF6F0]">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#B75828] border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const handleNavigate = (path: string) => {
    setCurrentRoute(path as typeof currentRoute);
  };

  const isAdmin = user?.role === 'admin';

  switch (currentRoute) {
    case 'config':
      return <ConfigPage onNavigate={handleNavigate} isAdmin={isAdmin} />;
    case 'leads':
      return <LeadsPage onNavigate={handleNavigate} />;
    case 'empresas':
      return isAdmin 
        ? <AdminCompaniesPage onNavigate={handleNavigate} />
        : <CompaniesPage onNavigate={handleNavigate} />;
    case 'dashboard':
    default:
      return <DashboardPage onNavigate={handleNavigate} />;
  }
}

function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}

export default App;

