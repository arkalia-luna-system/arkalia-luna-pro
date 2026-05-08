import React from 'react';

const ArkaliaLunaHomepage = () => {
  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Fond fractal animé */}
      <div className="absolute inset-0 w-full h-full z-0">
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 1920 1080"
          preserveAspectRatio="none"
          className="w-full h-full"
        >
          <defs>
            <radialGradient id="glow" cx="50%" cy="50%" r="60%">
              <stop offset="0%" stopColor="#7ecbff" stopOpacity="0.18"/>
              <stop offset="100%" stopColor="#090c12" stopOpacity="0"/>
            </radialGradient>
            <filter id="glowFilter" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="18" result="glow"/>
              <feMerge>
                <feMergeNode in="glow"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          <rect width="1920" height="1080" fill="url(#glow)"/>
          <polyline
            points="200,200 400,300 600,180 900,400 1200,200 1500,350 1700,180"
            stroke="#7ecbff"
            strokeWidth="2.5"
            fill="none"
            opacity="0.18"
            filter="url(#glowFilter)"
            className="animate-pulse"
          />
          <polyline
            points="300,800 600,700 900,900 1200,700 1500,900 1700,700"
            stroke="#7ecbff"
            strokeWidth="2.5"
            fill="none"
            opacity="0.13"
            filter="url(#glowFilter)"
            className="animate-pulse"
            style={{animationDelay: '-2s'}}
          />
          <polyline
            points="100,500 400,600 800,500 1200,600 1600,500"
            stroke="#7ecbff"
            strokeWidth="1.5"
            fill="none"
            opacity="0.10"
            filter="url(#glowFilter)"
            className="animate-pulse"
            style={{animationDelay: '-4s'}}
          />
        </svg>
      </div>

      {/* Status bar */}
      <div className="absolute top-6 right-12 text-cyan-400 text-sm font-mono z-10">
        Reflexia active. 92% system integrity
      </div>

      {/* Header avec navigation */}
      <header className="relative z-10 pt-10 pb-6">
        <nav className="flex items-center justify-start gap-10 ml-16">
          <span className="text-white text-xl font-bold tracking-widest uppercase mr-10">
            Arkalia
          </span>
          <ul className="flex gap-10 list-none m-0 p-0">
            {['Modules', 'API', 'Usage', 'Architecture', 'Logs', 'Mind'].map((item) => (
              <li key={item}>
                <a
                  href={`#${item.toLowerCase()}`}
                  className="text-slate-200 text-lg font-bold tracking-wider uppercase no-underline transition-colors duration-200 px-2 py-1 rounded hover:text-cyan-400 hover:bg-cyan-400/10"
                >
                  {item}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </header>

      {/* Lune centrale */}
      <div className="absolute top-0 left-1/2 transform -translate-x-1/2 z-10 mt-20">
        <svg width="120" height="120" viewBox="0 0 120 120" className="drop-shadow-[0_0_60px_rgba(126,203,255,0.5)]">
          <defs>
            <radialGradient id="moonGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#fff" stopOpacity="1"/>
              <stop offset="80%" stopColor="#7ecbff" stopOpacity="0.7"/>
              <stop offset="100%" stopColor="#0ff" stopOpacity="0"/>
            </radialGradient>
          </defs>
          <circle
            cx="60"
            cy="60"
            r="40"
            fill="url(#moonGlow)"
            className="animate-pulse"
          >
            <animate
              attributeName="r"
              values="38;42;38"
              dur="3s"
              repeatCount="indefinite"
            />
          </circle>
          <circle
            cx="60"
            cy="60"
            r="32"
            fill="#fff"
            fillOpacity="0.95"
          />
        </svg>
      </div>

      {/* Contenu principal */}
      <main className="relative z-10 pt-32 pb-16 px-8">
        {/* Titre et sous-titre */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-black tracking-[0.32em] text-white mb-4 uppercase drop-shadow-[0_0_32px_rgba(126,203,255,0.4)]">
            ARKALIA-LUNA
          </h1>
          <h2 className="text-2xl font-normal text-slate-300 tracking-wider">
            Cognitive Autonomy System
          </h2>
        </div>

        {/* Grille 3 colonnes */}
        <div className="grid grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* Colonne 1: Overview */}
          <div className="space-y-6">
            <h3 className="text-xl font-black text-white tracking-wider drop-shadow-[0_0_8px_rgba(126,203,255,0.3)]">
              Overview
            </h3>
            <div className="space-y-4">
              <div>
                <h4 className="text-slate-200 font-semibold mb-2">Cognitive Architecture</h4>
                <ul className="space-y-1 ml-4">
                  {['Reflexia', 'Zeroia', 'Sandozia', 'Cognitive Reactor'].map((item) => (
                    <li key={item} className="flex items-center">
                      <div className="w-2 h-2 bg-cyan-400 rounded-full mr-3 drop-shadow-[0_0_8px_rgba(126,203,255,0.6)]"></div>
                      <a
                        href={`#${item.toLowerCase()}`}
                        className="text-cyan-400 hover:text-white transition-colors duration-200"
                      >
                        {item}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-slate-200 font-semibold mb-2">API Reference</h4>
                <ul className="space-y-1 ml-4">
                  {['Reflexia', 'Zeroia'].map((item) => (
                    <li key={item} className="flex items-center">
                      <div className="w-2 h-2 bg-blue-300 rounded-full mr-3"></div>
                      <a
                        href={`#${item.toLowerCase()}`}
                        className="text-cyan-400 hover:text-white transition-colors duration-200"
                      >
                        {item}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Colonne 2: API Reference */}
          <div className="space-y-6">
            <h3 className="text-xl font-black text-white tracking-wider drop-shadow-[0_0_8px_rgba(126,203,255,0.3)]">
              API Reference
            </h3>
            <div className="space-y-4">
              <ul className="space-y-1 ml-4">
                {['Arkalla API', 'Endpoints'].map((item) => (
                  <li key={item} className="flex items-center">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full mr-3 drop-shadow-[0_0_8px_rgba(126,203,255,0.6)]"></div>
                    <a
                      href={`#${item.toLowerCase().replace(' ', '-')}`}
                      className="text-cyan-400 hover:text-white transition-colors duration-200"
                    >
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <h3 className="text-xl font-black text-white tracking-wider drop-shadow-[0_0_8px_rgba(126,203,255,0.3)]">
              Testing
            </h3>
            <ul className="space-y-1 ml-4">
              {['Monitoring & Logs', 'Prometheus', 'Grafana'].map((item) => (
                <li key={item} className="flex items-center">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full mr-3 drop-shadow-[0_0_8px_rgba(126,203,255,0.6)]"></div>
                  <a
                    href={`#${item.toLowerCase().replace(' & ', '-').replace(' ', '-')}`}
                    className="text-cyan-400 hover:text-white transition-colors duration-200"
                  >
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Colonne 3: Testing & Security */}
          <div className="space-y-6">
            <h3 className="text-xl font-black text-white tracking-wider drop-shadow-[0_0_8px_rgba(126,203,255,0.3)]">
              Testing & Security
            </h3>
            <ul className="space-y-1 ml-4">
              {['Prometheus', 'Grafana', 'Vault Manager', 'Anti-Hallucination'].map((item) => (
                <li key={item} className="flex items-center">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full mr-3 drop-shadow-[0_0_8px_rgba(126,203,255,0.6)]"></div>
                  <a
                    href={`#${item.toLowerCase().replace(' ', '-')}`}
                    className="text-cyan-400 hover:text-white transition-colors duration-200"
                  >
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Roadmap */}
        <div className="text-center mt-16">
          <div className="text-cyan-400 text-xl font-bold tracking-widest drop-shadow-[0_0_8px_rgba(126,203,255,0.6)]">
            Roadmap
          </div>
        </div>
        {/* Bouton Documentation */}
        <div className="flex justify-center mt-8">
          <a
            href="/site/index.html"
            className="inline-block text-lg px-8 py-4 rounded-full bg-gradient-to-r from-cyan-500/20 to-blue-900/30 text-cyan-200 font-bold tracking-widest shadow-lg hover:bg-cyan-400/20 hover:text-white transition-all duration-300 border border-cyan-400/30"
            target="_blank"
            rel="noopener noreferrer"
          >
            Voir la documentation complète
          </a>
        </div>
      </main>
    </div>
  );
};

export default ArkaliaLunaHomepage;
