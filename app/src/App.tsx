import React, { useState } from 'react';

export default function App() {
  const [copperWeight, setCopperWeight] = useState<number>(10);
  const copperRate = 720;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', display: 'flex', justifyContent: 'center', padding: '16px', fontFamily: 'sans-serif' }}>
      <div style={{ width: '100%', maxWidth: '380px', backgroundColor: '#1e293b', color: '#fff', borderRadius: '24px', border: '1px solid #334155', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        
        {/* Top Header */}
        <div style={{ padding: '16px', backgroundColor: '#047857', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>Kabadiwala Connect</h1>
            <p style={{ margin: 0, fontSize: '12px', color: '#a7f3d0' }}>Ministry of Mines • Collector Portal</p>
          </div>
          <span style={{ fontSize: '11px', backgroundColor: '#064e3b', padding: '4px 8px', borderRadius: '12px', border: '1px solid #10b981' }}>
            🇮🇳 EN | हिं
          </span>
        </div>

        {/* Content Body */}
        <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          
          {/* Daily Metric Card */}
          <div style={{ backgroundColor: '#334155', padding: '14px', borderRadius: '16px', border: '1px solid #475569' }}>
            <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Today's Inwarded Scrap</span>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginTop: '4px' }}>
              <span style={{ fontSize: '28px', fontWeight: '800', color: '#34d399' }}>2,840 kg</span>
              <span style={{ fontSize: '13px', fontWeight: '600', color: '#cbd5e1' }}>₹18,450 Earned</span>
            </div>
          </div>

          {/* Benchmark Rates */}
          <div style={{ backgroundColor: '#1e293b', padding: '14px', borderRadius: '16px', border: '1px solid #334155' }}>
            <h2 style={{ fontSize: '13px', margin: '0 0 10px 0', color: '#e2e8f0' }}>Live Scrap Benchmark Rates</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #334155', paddingBottom: '4px' }}>
                <span style={{ color: '#cbd5e1' }}>Copper (Grade A)</span>
                <span style={{ fontWeight: 'bold', color: '#fbbf24' }}>₹720 / kg</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #334155', paddingBottom: '4px' }}>
                <span style={{ color: '#cbd5e1' }}>Brass Clean</span>
                <span style={{ fontWeight: 'bold', color: '#facc15' }}>₹480 / kg</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#cbd5e1' }}>Aluminum Cast</span>
                <span style={{ fontWeight: 'bold', color: '#cbd5e1' }}>₹180 / kg</span>
              </div>
            </div>
          </div>

          {/* Payout Calculator */}
          <div style={{ backgroundColor: 'rgba(6, 78, 59, 0.3)', padding: '14px', borderRadius: '16px', border: '1px solid rgba(16, 185, 129, 0.4)' }}>
            <h2 style={{ fontSize: '13px', margin: '0 0 8px 0', color: '#6ee7b7' }}>Quick Weigh & Calculate</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input 
                type="number" 
                value={copperWeight} 
                onChange={(e) => setCopperWeight(Number(e.target.value))}
                style={{ width: '80px', padding: '6px 8px', backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', border: '1px solid #475569' }}
              />
              <span style={{ fontSize: '12px', color: '#94a3b8' }}>kg of Copper</span>
            </div>
            <div style={{ marginTop: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', color: '#cbd5e1' }}>Estimated Total:</span>
              <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#34d399' }}>₹{copperWeight * copperRate}</span>
            </div>
            <button style={{ width: '100%', marginTop: '10px', backgroundColor: '#059669', color: '#fff', border: 'none', padding: '10px', borderRadius: '12px', fontWeight: 'bold', cursor: 'pointer' }}>
              Initiate UPI Settlement
            </button>
          </div>

        </div>

        {/* Bottom Nav */}
        <div style={{ borderTop: '1px solid #334155', backgroundColor: '#0f172a', padding: '12px', display: 'flex', justifyContent: 'space-around', fontSize: '11px', color: '#94a3b8' }}>
          <span style={{ color: '#34d399', fontWeight: 'bold' }}>🏠 Home</span>
          <span>📦 Pickups</span>
          <span>📈 Rates</span>
          <span>👤 Profile</span>
        </div>

      </div>
    </div>
  );
}