import type { BetRecommendation } from '../lib/api';

interface PlanCardProps {
  recommendations: BetRecommendation[];
  totalStake: number;
  maxReturn: number;
}

export function PlanCard({ recommendations, totalStake, maxReturn }: PlanCardProps) {
  if (recommendations.length === 0) return null;

  const profit = maxReturn - totalStake;

  return (
    <div className="glass-strong rounded-3xl p-6 animate-fade-up">
      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="text-center p-3 rounded-2xl bg-white/[0.02]">
          <div className="text-2xl font-extrabold text-[var(--text-primary)] tabular-nums">
            ¥{totalStake.toFixed(0)}
          </div>
          <div className="text-[10px] text-[var(--text-secondary)] mt-1">总投注</div>
        </div>
        <div className="text-center p-3 rounded-2xl bg-indigo-500/5">
          <div className="text-2xl font-extrabold text-indigo-400 tabular-nums">
            ¥{maxReturn.toFixed(0)}
          </div>
          <div className="text-[10px] text-[var(--text-secondary)] mt-1">全中回报</div>
        </div>
        <div className="text-center p-3 rounded-2xl bg-green-500/5">
          <div className="text-2xl font-extrabold text-green-400 tabular-nums">
            +¥{profit.toFixed(0)}
          </div>
          <div className="text-[10px] text-[var(--text-secondary)] mt-1">潜在利润</div>
        </div>
      </div>

      {/* Bet list */}
      <div className="space-y-2">
        {recommendations.map((rec, index) => (
          <div
            key={`${rec.match_id}-${rec.selection}`}
            className="glass rounded-2xl p-4 hover:bg-white/[0.04] transition-all duration-300 group"
          >
            <div className="flex items-center gap-3">
              {/* Rank badge */}
              <div className="w-7 h-7 rounded-full bg-indigo-500/10 flex items-center justify-center shrink-0">
                <span className="text-xs font-bold text-indigo-400">{index + 1}</span>
              </div>

              {/* Match info */}
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold truncate">{rec.match_summary}</div>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-[var(--text-secondary)]">
                    {rec.selection === 'home' ? '主胜' : rec.selection === 'draw' ? '平' : '客胜'}
                  </span>
                  <span className="text-[10px] text-[var(--text-secondary)]">
                    赔率 {rec.odds.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Amount */}
              <div className="text-right shrink-0">
                <div className="text-sm font-bold tabular-nums">¥{rec.stake.toFixed(0)}</div>
                <div className="text-[10px] text-green-400 tabular-nums">→ ¥{rec.potential_return.toFixed(0)}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Disclaimer */}
      <div className="mt-4 pt-4 border-t border-white/5 text-center">
        <p className="text-[10px] text-[var(--text-secondary)]">
          方案基于赔率排序，仅供参考
        </p>
      </div>
    </div>
  );
}
