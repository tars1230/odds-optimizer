import type { BetRecommendation } from '../lib/api';

interface PlanCardProps {
  recommendations: BetRecommendation[];
  totalStake: number;
  maxReturn: number;
}

export function PlanCard({ recommendations, totalStake, maxReturn }: PlanCardProps) {
  if (recommendations.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">最优投注方案</h2>
      
      <div className="grid grid-cols-3 gap-4 mb-6 text-center">
        <div className="bg-green-50 rounded-lg p-3">
          <div className="text-2xl font-bold text-green-600">
            ¥{totalStake.toFixed(0)}
          </div>
          <div className="text-xs text-gray-500">总投注</div>
        </div>
        <div className="bg-blue-50 rounded-lg p-3">
          <div className="text-2xl font-bold text-blue-600">
            ¥{maxReturn.toFixed(0)}
          </div>
          <div className="text-xs text-gray-500">最高回报</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-3">
          <div className="text-2xl font-bold text-purple-600">
            {totalStake > 0 ? ((maxReturn / totalStake - 1) * 100).toFixed(0) : '0'}%
          </div>
          <div className="text-xs text-gray-500">潜在收益率</div>
        </div>
      </div>

      <div className="space-y-3">
        {recommendations.map((rec, index) => (
          <div
            key={`${rec.match_id}-${rec.selection}`}
            className="border rounded-lg p-4 hover:border-blue-300 transition-colors"
          >
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  {index + 1}
                </span>
                <span className="font-medium">{rec.match_summary}</span>
              </div>
              <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                {rec.selection === 'home' ? '主胜' : rec.selection === 'draw' ? '平' : '客胜'}
              </span>
            </div>
            
            <div className="grid grid-cols-4 gap-2 text-sm">
              <div>
                <div className="text-gray-500">赔率</div>
                <div className="font-mono font-bold text-blue-600">{rec.odds.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-gray-500">投注</div>
                <div className="font-mono">¥{rec.stake.toFixed(0)}</div>
              </div>
              <div>
                <div className="text-gray-500">潜在回报</div>
                <div className="font-mono text-green-600">¥{rec.potential_return.toFixed(0)}</div>
              </div>
              <div>
                <div className="text-gray-500">EV评分</div>
                <div className="font-mono">{rec.ev_score.toFixed(2)}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
