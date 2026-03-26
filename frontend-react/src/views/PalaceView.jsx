import React, { useMemo } from 'react';
import { Building2, Lock } from 'lucide-react';
import { getThemeColors } from '../components/CommonUI';

const PalaceView = ({ analytics, theme }) => {
  const colors = getThemeColors(theme);
  const vaults = useMemo(() => Object.entries(analytics?.category_distribution || {}).map(([name, count]) => ({ name, count })), [analytics]);
  return (
    <div className="p-4 sm:p-6 w-full max-w-7xl mx-auto animate-in fade-in duration-500">
      <div className="mb-6 sm:mb-8">
        <h2 className={`text-xl sm:text-2xl font-light flex items-center ${colors.textMain}`}>
          <Building2 className="w-5 h-5 sm:w-6 sm:h-6 mr-3 text-amber-500" /> Memory Palace
        </h2>
        <p className="text-stone-500 text-xs sm:text-sm mt-1">Structured visualization of your neural vaults.</p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
        {vaults.length > 0 ? vaults.map((vault, i) => (
          <div key={i} className={`aspect-square rounded-xl border relative overflow-hidden group cursor-pointer transition-all shadow-sm hover:shadow-md ${colors.panel} ${colors.panelBorder} hover:border-amber-500`}>
            <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent"></div>
            <div className="absolute inset-0 flex flex-col items-center justify-center p-2 text-center">
              <Lock className="w-6 h-6 text-amber-500/40 mb-3 group-hover:text-amber-500 transition-colors" />
              <h3 className={`font-medium tracking-wide text-xs sm:text-sm capitalize ${colors.textMain}`}>{vault.name}</h3>
              <span className="text-[10px] text-stone-400 mt-1 font-mono">{vault.count} items</span>
            </div>
          </div>
        )) : <div className="col-span-full p-12 text-center text-stone-400 border border-dashed border-stone-200 rounded-xl">No categorized vaults detected yet.</div>}
      </div>
    </div>
  );
};

export default PalaceView;
