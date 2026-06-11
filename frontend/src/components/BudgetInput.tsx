import { useState } from 'react';

interface BudgetInputProps {
  onOptimize: (budget: number, riskLevel: string) => void;
  loading: boolean;
}

const PRESETS = [100, 200, 500, 1000, 2000];
const RISK_LEVELS = [
  { value: 'conservative', label: '保守', desc: '四分之一凯利' },
  { value: 'moderate', label: '适中', desc: '半凯利' },
  { value: 'aggressive', label: '激进', desc: '四分之三凯利' },
];

export function BudgetInput({ onOptimize, loading }: BudgetInputProps) {
  const [budget, setBudget] = useState(500);
  const [riskLevel, setRiskLevel] = useState('moderate');

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">预算设置</h2>
      
      <div className="mb-4">
        <label className="block text-sm text-gray-600 mb-2">投注金额 (元)</label>
        <div className="flex gap-2 mb-2">
          {PRESETS.map((preset) => (
            <button
              key={preset}
              onClick={() => setBudget(preset)}
              className={`px-3 py-1 rounded text-sm ${
                budget === preset
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {preset}
            </button>
          ))}
        </div>
        <input
          type="number"
          value={budget}
          onChange={(e) => setBudget(Number(e.target.value))}
          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          min={1}
          max={100000}
        />
      </div>

      <div className="mb-4">
        <label className="block text-sm text-gray-600 mb-2">风险偏好</label>
        <div className="grid grid-cols-3 gap-2">
          {RISK_LEVELS.map((level) => (
            <button
              key={level.value}
              onClick={() => setRiskLevel(level.value)}
              className={`p-3 rounded-lg text-center ${
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
        className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? '计算中...' : '生成最优方案'}
      </button>
    </div>
  );
}
