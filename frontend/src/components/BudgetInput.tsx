import { useState } from 'react';

interface BudgetInputProps {
  onOptimize: (budget: number, riskLevel: string) => void;
  loading: boolean;
}

const RISK_LEVELS = [
  { value: 'conservative', label: '保守', desc: '分散投注' },
  { value: 'moderate', label: '适中', desc: '均衡分配' },
  { value: 'aggressive', label: '激进', desc: '集中押注' },
];

export function BudgetInput({ onOptimize, loading }: BudgetInputProps) {
  const [budget, setBudget] = useState(500);
  const [riskLevel, setRiskLevel] = useState('moderate');

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">预算设置</h2>

      <div className="mb-5">
        <div className="flex justify-between items-baseline mb-2">
          <label className="text-sm text-gray-600">投注金额</label>
          <span className="text-2xl font-bold text-blue-600">¥{budget}</span>
        </div>
        <input
          type="range"
          min={100}
          max={10000}
          step={100}
          value={budget}
          onChange={(e) => setBudget(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>¥100</span>
          <span>¥10,000</span>
        </div>
      </div>

      <div className="mb-5">
        <label className="block text-sm text-gray-600 mb-2">风险偏好</label>
        <div className="grid grid-cols-3 gap-2">
          {RISK_LEVELS.map((level) => (
            <button
              key={level.value}
              onClick={() => setRiskLevel(level.value)}
              className={`p-3 rounded-lg text-center transition-colors ${
                riskLevel === level.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <div className="font-medium">{level.label}</div>
              <div className="text-xs opacity-75">{level.desc}</div>
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={() => onOptimize(budget, riskLevel)}
        disabled={loading}
        className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? '计算中...' : '生成最优方案'}
      </button>
    </div>
  );
}
