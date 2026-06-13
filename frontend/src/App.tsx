import { useState, useEffect } from 'react';
import { fetchMasters, getMasterRecommendation, compareMasters, type Master, type MasterRecommendation, type MasterComparison } from './lib/api';
import { useAutoTheme, getThemeIcon } from './lib/theme';
import { MasterCard } from './components/MasterCard';

function App() {
  const [masters, setMasters] = useState<Master[]>([]);
  const [selectedMaster, setSelectedMaster] = useState<Master | null>(null);
  const [budget, setBudget] = useState(100);
  const [recommendation, setRecommendation] = useState<MasterRecommendation | null>(null);
  const [comparisons, setComparisons] = useState<MasterComparison[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState<'select' | 'recommendation' | 'compare'>('select');

  // 自动主题切换
  useAutoTheme();

  useEffect(() => {
    loadMasters();
  }, []);

  async function loadMasters() {
    try {
      const data = await fetchMasters();
      setMasters(data);
    } catch (err) {
      console.error('Failed to load masters:', err);
    }
  }

  async function handleSelectMaster(master: Master) {
    setSelectedMaster(master);
    setLoading(true);
    setView('recommendation');

    try {
      const data = await getMasterRecommendation(master.id, budget);
      setRecommendation(data);
    } catch (err) {
      console.error('Failed to get recommendation:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCompare() {
    setLoading(true);
    setView('compare');

    try {
      const data = await compareMasters(budget);
      setComparisons(data.comparisons);
    } catch (err) {
      console.error('Failed to compare:', err);
    } finally {
      setLoading(false);
    }
  }

  function handleBack() {
    setView('select');
    setSelectedMaster(null);
    setRecommendation(null);
    setComparisons(null);
  }

  return (
    <div className="min-h-dvh relative overflow-hidden">
      {/* 主题指示器 */}
      <div className="theme-indicator">{getThemeIcon()}</div>

      {/* 背景渐变 */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-indigo-500/8 blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-purple-500/6 blur-[100px]" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {/* 选择大师页 */}
        {view === 'select' && (
          <>
            {/* Header */}
            <header className="mb-10 sm:mb-14 animate-fade-up text-center">
              <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight mb-4">
                🎯 投注大师<span className="text-indigo-400">模拟器</span>
              </h1>
              <p className="text-[var(--text-secondary)] text-lg max-w-2xl mx-auto mb-6">
                学习投资大师的决策思维，理解风险与收益
              </p>

              {/* 预算输入 */}
              <div className="flex items-center justify-center gap-4 mb-8">
                <span className="text-sm text-[var(--text-secondary)]">模拟预算</span>
                <input
                  type="number"
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value))}
                  className="w-32 px-4 py-2 rounded-lg glass text-center font-mono"
                  min="20"
                  max="10000"
                />
                <span className="text-sm text-[var(--text-secondary)]">元</span>
              </div>

              <p className="text-sm text-[var(--text-secondary)]">
                选择你的投资导师 👇
              </p>
            </header>

            {/* 大师卡片网格 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8 stagger">
              {masters.map((master) => (
                <MasterCard
                  key={master.id}
                  master={master}
                  onClick={() => handleSelectMaster(master)}
                />
              ))}
            </div>

            {/* 对决按钮 */}
            <div className="text-center">
              <button
                onClick={handleCompare}
                className="glass px-8 py-4 rounded-2xl font-semibold text-lg hover:scale-105 transition-transform"
              >
                🆚 大师对决 PK
              </button>
            </div>

            {/* 免责声明 */}
            <footer className="mt-16 pt-8 border-t border-[var(--border)] text-center">
              <p className="text-xs text-[var(--text-secondary)] max-w-2xl mx-auto">
                ⚠️ 本平台是投资教育工具，所有方案仅供学习参考，不构成投资建议。
                投资有风险，决策需谨慎。
              </p>
            </footer>
          </>
        )}

        {/* 推荐方案页 */}
        {view === 'recommendation' && recommendation && (
          <div className="animate-fade-up">
            <button
              onClick={handleBack}
              className="mb-6 px-4 py-2 rounded-lg glass hover:scale-105 transition-transform"
            >
              ← 返回选择
            </button>

            <div className="glass rounded-3xl p-8 max-w-4xl mx-auto">
              {/* 大师头部 */}
              <div className="text-center mb-8">
                <div className="text-7xl mb-4">{recommendation.master.emoji}</div>
                <h2 className="text-3xl font-bold mb-2">{recommendation.master.name}的方案</h2>
                <p className="text-[var(--text-secondary)] italic">
                  "{recommendation.master.quotes[0]}"
                </p>
              </div>

              {/* 统计卡片 */}
              <div className="grid grid-cols-3 gap-4 mb-8">
                <div className="glass rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-[var(--green)]">
                    ¥{recommendation.total_stake}
                  </div>
                  <div className="text-xs text-[var(--text-secondary)] mt-1">总投注</div>
                </div>
                <div className="glass rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-[var(--accent)]">
                    ¥{recommendation.max_potential_return.toFixed(0)}
                  </div>
                  <div className="text-xs text-[var(--text-secondary)] mt-1">最高回报</div>
                </div>
                <div className="glass rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-[var(--amber)]">
                    {recommendation.count}注
                  </div>
                  <div className="text-xs text-[var(--text-secondary)] mt-1">推荐数量</div>
                </div>
              </div>

              {/* 推荐列表 */}
              <div className="space-y-3 mb-8">
                {recommendation.recommendations.map((rec, i) => (
                  <div key={i} className="glass rounded-xl p-4 hover:scale-[1.02] transition-transform">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        <span className="w-8 h-8 rounded-full bg-[var(--accent)] text-white flex items-center justify-center font-bold">
                          {i + 1}
                        </span>
                        <div>
                          <div className="font-semibold">{rec.match_summary}</div>
                          <div className="text-xs text-[var(--text-secondary)]">
                            {rec.selection === 'home' ? '主胜' : rec.selection === 'draw' ? '平局' : '客胜'}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-mono text-lg">¥{rec.stake} @ {rec.odds}x</div>
                        <div className="text-xs text-[var(--green)]">→ ¥{rec.potential_return.toFixed(0)}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* 大师解释 */}
              <div className="glass rounded-xl p-6 bg-[var(--accent)]/5 border-[var(--accent)]/20">
                <div className="flex items-start gap-3">
                  <div className="text-3xl">{recommendation.master.emoji}</div>
                  <div>
                    <div className="font-semibold mb-2">{recommendation.master.name}说：</div>
                    <div className="text-sm text-[var(--text-secondary)] whitespace-pre-line leading-relaxed">
                      {recommendation.explanation}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 对决页 */}
        {view === 'compare' && comparisons && (
          <div className="animate-fade-up">
            <button
              onClick={handleBack}
              className="mb-6 px-4 py-2 rounded-lg glass hover:scale-105 transition-transform"
            >
              ← 返回选择
            </button>

            <div className="glass rounded-3xl p-8 max-w-5xl mx-auto">
              <h2 className="text-3xl font-bold text-center mb-8">
                🏆 大师对决 PK
                <span className="text-lg text-[var(--text-secondary)] block mt-2">
                  同样¥{budget}预算，6位大师会怎么投？
                </span>
              </h2>

              <div className="space-y-4">
                {comparisons.map((comp) => (
                  <div
                    key={comp.master_id}
                    className="glass rounded-xl p-6 hover:scale-[1.02] transition-transform"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="text-4xl">{comp.master.emoji}</div>
                        <div>
                          <div className="font-bold text-xl">{comp.master.name}</div>
                          <div className="text-sm text-[var(--text-secondary)]">
                            {comp.master.title}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-8">
                        <div className="text-center">
                          <div className="text-2xl font-mono">¥{comp.total_stake}</div>
                          <div className="text-xs text-[var(--text-secondary)]">{comp.bet_count}注</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-mono text-[var(--green)]">
                            ¥{comp.max_return.toFixed(0)}
                          </div>
                          <div className="text-xs text-[var(--text-secondary)]">最高回报</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-[var(--accent)]">
                            {comp.roi_percent}%
                          </div>
                          <div className="text-xs text-[var(--text-secondary)]">ROI</div>
                        </div>
                        <div className="text-center">
                          <div className="text-amber-400">{'⭐'.repeat(comp.risk_level)}</div>
                          <div className="text-xs text-[var(--text-secondary)]">风险</div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="glass rounded-2xl p-8 text-center">
              <div className="text-5xl mb-4 animate-spin">🤔</div>
              <div className="text-lg">大师思考中...</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
