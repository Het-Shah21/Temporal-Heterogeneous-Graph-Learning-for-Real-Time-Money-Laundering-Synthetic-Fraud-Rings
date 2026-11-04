"use client";

import React from "react";
import { Shield, Activity } from "lucide-react";

export function Header() {
  return (
    <header className="border-b border-slate-800/60 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3.5">
        <div className="flex items-center justify-between">
          
          {/* Minimal Brand */}
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Shield className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm tracking-tight text-white">
                  AEGIS
                </span>
                <span className="text-slate-500 text-xs font-normal">/</span>
                <span className="text-xs text-slate-400 font-normal">
                  AML Graph Intelligence
                </span>
              </div>
            </div>
          </div>

          {/* Clean Status Indicator */}
          <div className="flex items-center gap-2 text-xs">
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-300">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="font-mono text-[11px] text-slate-400">Model Active</span>
              <span className="text-slate-600">•</span>
              <span className="font-mono text-[11px] text-emerald-400 font-medium">7.4ms</span>
            </div>
          </div>

        </div>
      </div>
    </header>
  );
}
