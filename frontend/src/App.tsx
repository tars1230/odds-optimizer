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
      setError('计算失败');
    } finally {
      setOptimizing(false);
    }
  }

  function handleBudgetChange(budget: number, riskLevel: string) {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = window.setTimeout(() => {
      handleOptimize(budget, riskLevel);
    }, 400);
  }

  return (
    <div className="min-h-dvh relative overflow-hidden">
      {/* Background gradient orbs */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-indigo-500/8 blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-purple-500/6 blur-[100px]" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {/* Header */}
        <header className="mb-10 sm:mb-14 animate-fade-up">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-xs font-medium text-[var(--text-secondary)] tracking-widest uppercase">Live Data</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-2">
            竞彩赔率<span className="text-indigo-400">优化器</span>
          </h1>
          <p className="text-[var(--text-secondary)] text-sm sm:text-base max-w-lg">
            基于数学模型的投注方案生成 · 数据来源竞彩官网 · 实时更新
          </p>
        </header>

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
          {/* Left: Matches */}
          <div className="lg:col-span-7 xl:col-span-8">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-3">
                <h2 className="text-lg font-bold">今日赛事</h2>
                <span className="text-xs px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 font-medium">
                  {matches.length} 场
                </span>
              </div>
              <button
                onClick={() => loadMatches(true)}
                disabled={loading}
                className="group flex items-center gap-2 px-4 py-2 rounded-full glass text-sm font-medium hover:bg-white/5 transition-all duration-300 active:scale-[0.97]"
              >
                <svg className={`w-4 h-4 transition-transform duration-500 ${loading ? 'animate-spin' : 'group-hover:rotate-180'}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12a9 9 0 11-6.219-8.56" />
                </svg>
                {loading ? '加载中' : '刷新'}
              </button>
            </div>
            {error && (
              <div className="mb-4 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm animate-fade-up">
                {error}
              </div>
            )}
            <MatchList matches={matches} loading={loading} />
          </div>

          {/* Right: Controls & Plan */}
          <div className="lg:col-span-5 xl:col-span-4 space-y-6">
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

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t border-white/5 text-center">
          <p className="text-xs text-[var(--text-secondary)]">
            仅供参考，不构成投注建议 · 彩票有风险，投注需谨慎
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
