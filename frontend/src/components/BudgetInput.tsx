import { useState } from 'react';

interface BudgetInputProps {
  onOptimize: (budget: number, riskLevel: string) => void;
  onChange: (budget: number, riskLevel: string) => void;
  loading: boolean;
}

const RISK_LEVELS = [
  { value: 'conservative', label: '保守', desc: '10注均分', icon: '🛡️', color: 'green' },
  { value: 'moderate', label: '适中', desc: '6注加权', icon: '⚖️', color: 'indigo' },
  { value: 'aggressive', label: '激进', desc: '3注集中', icon: '🎯', color: 'red' },
];

export function BudgetInput({ onOptimize, onChange, loading }: BudgetInputProps) {
  const [budget, setBudget] = useState(500);
  const [riskLevel, setRiskLevel] = useState('moderate');

  function handleBudgetChange(value: number) {
    setBudget(value);
    onChange(value, riskLevel);
  }

  function handleRiskChange(level: string) {
    setRiskLevel(level);
    onChange(budget, level);
  }

  return (
    <div className="glass-strong rounded-3xl p-6 glow-indigo">
      <div className="flex items-center gap-2 mb-6">
        <div className="w-8 h-8 rounded-xl bg-indigo-500/10 flex items-center justify-center">
          <svg className="w-4 h-4 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" />
          </svg>
        </div>
        <h2 className="text-base font-bold">预算设置</h2>
      </div>

      {/* Budget display */}
      <div className="text-center mb-6">
        <div className="text-5xl font-extrabold tracking-tight mb-1">
          ¥<span className="tabular-nums">{budget.toLocaleString()}</span>
        </div>
        <div className="text-xs text-[var(--text-secondary)]">投注金额（元）</div>
      </div>

      {/* Slider */}
      <div className="mb-8">
        <input
          type="range"
          min={100}
          max={10000}
          step={100}
          value={budget}
          onChange={(e) => handleBudgetChange(Number(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-[10px] text-[var(--text-secondary)] mt-2 px-1">
          <span>¥100</span>
          <span>¥5,000</span>
          <span>¥10,000</span>
        </div>
      </div>

      {/* Risk levels */}
      <div className="mb-6">
        <label className="text-xs font-medium text-[var(--text-secondary)] tracking-wider uppercase mb-3 block">风险偏好</label>
        <div className="grid grid-cols-3 gap-2">
          {RISK_LEVELS.map((level) => (
            <button
              key={level.value}
              onClick={() => handleRiskChange(level.value)}
              className={`relative p-3 rounded-2xl text-center transition-all duration-300 ${
                riskLevel === level.value
                  ? level.color === 'green'
                    ? 'bg-green-500/10 border border-green-500/30 text-green-400'
                    : level.color === 'red'
                    ? 'bg-red-500/10 border border-red-500/30 text-red-400'
                    : 'bg-indigo-500/10 border border-indigo-500/30 text-indigo-400'
                  : 'glass hover:bg-white/[0.04]'
              }`}
            >
              <div className="text-lg mb-1">{level.icon}</div>
              <div className="text-xs font-bold">{level.label}</div>
              <div className="text-[10px] text-[var(--text-secondary)] mt-0.5">{level.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* CTA Button */}
      <button
        onClick={() => onOptimize(budget, riskLevel)}
        disabled={loading}
        className="w-full py-3.5 rounded-2xl bg-indigo-500 hover:bg-indigo-400 text-white font-bold text-sm transition-all duration-300 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            计算中
          </>
        ) : (
          <>
            生成最优方案
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </>
        )}
      </button>
    </div>
  );
}
