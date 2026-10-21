import { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import { http } from '../services/httpClient'; // ← NUEVO: Usamos el interceptor

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

interface DashboardStats {
  total_obras: number;
  obras_por_estado: Record<string, number>;
  valor_inventario: number;
  total_vendido: number;
  top_tecnicas: Array<{ nombre: string; cantidad: number }>;
}

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(value);

export default function DashboardCharts() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null); // ← NUEVO: Manejo de errores

  useEffect(() => {
    // Usamos http.get en lugar de fetch nativo para que adjunte el token automáticamente
    http.get<DashboardStats>('/dashboard/stats')
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error al cargar dashboard:', err);
        setError(err.message || 'No se pudieron cargar las métricas');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="text-center py-12 text-text-secondary">Cargando métricas...</div>;
  }

  if (error || !stats) {
    return (
      <div className="text-center py-12 text-red-600">
        <p>{error || 'Error al cargar el dashboard.'}</p>
        <p className="text-sm text-text-secondary mt-2">Asegúrate de haber iniciado sesión.</p>
      </div>
    );
  }

  const estadoLabels: Record<string, string> = {
    disponible: 'Disponible',
    vendida: 'Vendida',
    en_exposicion: 'En exposición',
    en_prestamo: 'En préstamo',
  };

  const pieData = {
    labels: Object.keys(stats.obras_por_estado).map((k) => estadoLabels[k] || k),
    datasets: [
      {
        data: Object.values(stats.obras_por_estado),
        backgroundColor: ['#10b981', '#f59e0b', '#3b82f6', '#8b5cf6'],
        borderWidth: 0,
      },
    ],
  };

  const barData = {
    labels: stats.top_tecnicas.map((t) => t.nombre),
    datasets: [
      {
        label: 'Cantidad de obras',
        data: stats.top_tecnicas.map((t) => t.cantidad),
        backgroundColor: '#1f2937',
        borderRadius: 6,
      },
    ],
  };

  return (
    <div className="space-y-8">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
          <p className="text-sm text-text-secondary mb-1">Total de obras</p>
          <p className="text-3xl font-bold text-text-primary">{stats.total_obras}</p>
        </div>
        <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
          <p className="text-sm text-text-secondary mb-1">Valor inventario</p>
          <p className="text-2xl font-bold text-accent">{formatCurrency(stats.valor_inventario)}</p>
        </div>
        <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
          <p className="text-sm text-text-secondary mb-1">Total vendido</p>
          <p className="text-2xl font-bold text-green-600">{formatCurrency(stats.total_vendido)}</p>
        </div>
        <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
          <p className="text-sm text-text-secondary mb-1">Obras disponibles</p>
          <p className="text-3xl font-bold text-text-primary">{stats.obras_por_estado.disponible || 0}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
          <h3 className="font-serif text-xl font-bold text-text-primary mb-4">Obras por estado</h3>
          <div className="max-w-sm mx-auto">
            <Pie data={pieData} options={{ plugins: { legend: { position: 'bottom' } } }} />
          </div>
        </div>
        <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
          <h3 className="font-serif text-xl font-bold text-text-primary mb-4">Top 5 técnicas</h3>
          <Bar
            data={barData}
            options={{
              plugins: { legend: { display: false } },
              scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
            }}
          />
        </div>
      </div>
    </div>
  );
}