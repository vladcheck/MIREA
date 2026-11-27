import { Routes, Route, Navigate, useParams } from 'react-router-dom';
import LandingPage from './pages/LandingPage.jsx';
import PopupPage from './pages/PopupPage.jsx';

function VariantGuard({ children }) {
  const { variant } = useParams();
  if (variant !== 'wireframe' && variant !== 'full') {
    return <Navigate to="/wireframe" replace />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/wireframe" replace />} />
      <Route
        path="/:variant"
        element={
          <VariantGuard>
            <LandingPage />
          </VariantGuard>
        }
      />
      <Route
        path="/:variant/popups/:popupId"
        element={
          <VariantGuard>
            <PopupPage />
          </VariantGuard>
        }
      />
      <Route path="*" element={<Navigate to="/wireframe" replace />} />
    </Routes>
  );
}
