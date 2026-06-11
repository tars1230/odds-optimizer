import { useState, useEffect, useRef } from 'react';
import { MatchList } from './components/MatchList';
import { BudgetInput } from './components/BudgetInput';
import { PlanCard } from './components/PlanCard';
import { fetchMatches, optimizeBudget } from './lib/api';
import type { Match, BetRecommendation } from './lib/api';

function App() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [recommendations, setRecommendations] = useState<BetRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [totalStake, setTotalStake] = useState(0);
  const [maxReturn, setMaxReturn] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const debounceRef = useRef<number | null>(null);

  useEffect(() => {
    loadMatches();
  }, []);

  async function loadMatches(refresh = false) {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchMatches(refresh);
      setMatches(data);
    } catch (err) {
      setError('加载失败，请重试');
      console.error('Failed to load matches:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleOptimize(budget: number, riskLevel: string) {
    setOptimizing(true);
    setError(null);
    try {
      const result = await optimizeBudget(budget, riskLevel);
      setRecommendations(result.recommendations);
      setTotalStake(result.total_stake);
      setMaxReturn(result.max_potential_return);
    } catch (err) {
      setError('计算失败，请重试');
      console.error('Optimization failed:', err);
    } finally {
      setOptimizing(false);
    }
  }

  // Debounced handler for slider - triggers 300ms after user stops dragging
  function handleBudgetChange(budget: number, riskLevel: string) {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    debounceRef.current = window.setTimeout(() => {
      handleOptimize(budget, riskLevel);
    }, 300);
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            竞彩赔率优化器
          </h1>
          <p className="text-sm text-gray-500">
            基于凯利准则的最优盈亏比投注方案 · 数据来源：竞彩官网
          </p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Matches */}
          <div className="lg:col-span-2">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">今日赛事</h2>
              <button
                onClick={() => loadMatches(true)}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? '加载中...' : '刷新数据'}
              </button>
            </div>
            {error && <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">{error}</div>}
            <MatchList matches={matches} loading={loading} />
          </div>

          {/* Right: Budget & Plan */}
          <div className="space-y-6">
            <BudgetInput
              onOptimize={handleOptimize}
              onChange={handleBudgetChange}
              loading={optimizing}
            />
            <PlanCard
              recommendations={recommendations}
              totalStake={totalStake}
              maxReturn={maxReturn}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
