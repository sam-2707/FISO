"""
Atharman Logo Generator
Creates a professional SVG logo for the Atharman platform
"""

def create_atharman_logo():
    """Generate professional Atharman logo in SVG format"""
    
    logo_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="240" height="70" viewBox="0 0 240 70" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Advanced gradient definitions -->
    <linearGradient id="primaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4f46e5;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#7c3aed;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#ec4899;stop-opacity:1" />
    </linearGradient>
    
    <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#06b6d4;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" />
    </linearGradient>
    
    <radialGradient id="glowGradient" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
    </radialGradient>
    
    <!-- Advanced filters -->
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge> 
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    
    <filter id="dropshadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="3" dy="3" stdDeviation="3" flood-color="rgba(0,0,0,0.3)"/>
    </filter>
  </defs>
  
  <!-- Main logo container -->
  <g transform="translate(15, 10)">
    <!-- Sophisticated "A" with neural network styling -->
    <g filter="url(#glow)">
      <!-- Main A structure -->
      <path d="M 20 45 L 30 15 L 40 45 M 24 35 L 36 35" 
            stroke="url(#primaryGradient)" 
            stroke-width="4" 
            fill="none" 
            stroke-linecap="round" 
            stroke-linejoin="round"/>
      
      <!-- Neural network nodes -->
      <circle cx="30" cy="20" r="3" fill="url(#primaryGradient)" opacity="0.9"/>
      <circle cx="25" cy="30" r="2" fill="url(#accentGradient)" opacity="0.8"/>
      <circle cx="35" cy="30" r="2" fill="url(#accentGradient)" opacity="0.8"/>
      <circle cx="30" cy="40" r="2.5" fill="url(#primaryGradient)" opacity="0.7"/>
      
      <!-- Connecting lines (neural pathways) -->
      <line x1="28" y1="22" x2="25" y2="28" stroke="url(#accentGradient)" stroke-width="1" opacity="0.6"/>
      <line x1="32" y1="22" x2="35" y2="28" stroke="url(#accentGradient)" stroke-width="1" opacity="0.6"/>
      <line x1="25" y1="32" x2="28" y2="38" stroke="url(#accentGradient)" stroke-width="1" opacity="0.5"/>
      <line x1="35" y1="32" x2="32" y2="38" stroke="url(#accentGradient)" stroke-width="1" opacity="0.5"/>
    </g>
    
    <!-- Advanced data visualization -->
    <g transform="translate(50, 15)">
      <!-- 3D-style bars -->
      <rect x="0" y="25" width="3" height="10" fill="url(#accentGradient)" opacity="0.9"/>
      <polygon points="0,25 2,23 5,23 3,25" fill="url(#primaryGradient)" opacity="0.7"/>
      <polygon points="3,25 5,23 5,33 3,35" fill="url(#primaryGradient)" opacity="0.5"/>
      
      <rect x="6" y="20" width="3" height="15" fill="url(#accentGradient)" opacity="0.8"/>
      <polygon points="6,20 8,18 11,18 9,20" fill="url(#primaryGradient)" opacity="0.7"/>
      <polygon points="9,20 11,18 11,33 9,35" fill="url(#primaryGradient)" opacity="0.5"/>
      
      <rect x="12" y="18" width="3" height="17" fill="url(#accentGradient)" opacity="0.95"/>
      <polygon points="12,18 14,16 17,16 15,18" fill="url(#primaryGradient)" opacity="0.7"/>
      <polygon points="15,18 17,16 17,33 15,35" fill="url(#primaryGradient)" opacity="0.5"/>
      
      <rect x="18" y="22" width="3" height="13" fill="url(#accentGradient)" opacity="0.85"/>
      <polygon points="18,22 20,20 23,20 21,22" fill="url(#primaryGradient)" opacity="0.7"/>
      <polygon points="21,22 23,20 23,33 21,35" fill="url(#primaryGradient)" opacity="0.5"/>
      
      <!-- Floating data points -->
      <circle cx="26" cy="18" r="1.5" fill="url(#primaryGradient)" opacity="0.9">
        <animate attributeName="opacity" values="0.9;0.4;0.9" dur="2s" repeatCount="indefinite"/>
      </circle>
      <circle cx="29" cy="24" r="1" fill="url(#accentGradient)" opacity="0.8">
        <animate attributeName="opacity" values="0.8;0.3;0.8" dur="1.5s" repeatCount="indefinite"/>
      </circle>
      <circle cx="27" cy="30" r="1.2" fill="url(#primaryGradient)" opacity="0.7">
        <animate attributeName="opacity" values="0.7;0.2;0.7" dur="1.8s" repeatCount="indefinite"/>
      </circle>
    </g>
  </g>
  
  <!-- Company name with advanced typography -->
  <text x="85" y="30" 
        font-family="'Inter', 'SF Pro', -apple-system, sans-serif" 
        font-size="22" 
        font-weight="800" 
        fill="url(#primaryGradient)"
        filter="url(#dropshadow)">Atharman</text>
  
  <!-- Enhanced tagline -->
  <text x="85" y="45" 
        font-family="'Inter', 'SF Pro', -apple-system, sans-serif" 
        font-size="10" 
        font-weight="500" 
        fill="#475569" 
        opacity="0.9">AI-Powered Cloud Intelligence</text>
  
  <!-- Decorative elements -->
  <circle cx="220" cy="20" r="8" fill="url(#glowGradient)" opacity="0.3"/>
  <circle cx="215" cy="35" r="5" fill="url(#accentGradient)" opacity="0.2"/>
  <circle cx="225" cy="42" r="3" fill="url(#primaryGradient)" opacity="0.4"/>
  
  <!-- Subtle connecting line -->
  <path d="M 85 50 Q 150 52 210 48" 
        stroke="url(#accentGradient)" 
        stroke-width="1" 
        fill="none" 
        opacity="0.3"/>
</svg>"""
    
    return logo_svg

def create_favicon():
    """Generate favicon version of the logo"""
    
    favicon_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="faviconGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4f46e5;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#7c3aed;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#ec4899;stop-opacity:1" />
    </linearGradient>
    
    <filter id="miniGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="1" result="coloredBlur"/>
      <feMerge> 
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- Background with subtle border -->
  <circle cx="16" cy="16" r="15" fill="url(#faviconGradient)" opacity="0.95"/>
  <circle cx="16" cy="16" r="14" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
  
  <!-- Enhanced "A" with glow -->
  <g filter="url(#miniGlow)">
    <path d="M 9 23 L 16 9 L 23 23 M 12 19 L 20 19" 
          stroke="white" 
          stroke-width="2.5" 
          fill="none" 
          stroke-linecap="round" 
          stroke-linejoin="round"/>
    
    <!-- Neural nodes -->
    <circle cx="16" cy="12" r="1.5" fill="white" opacity="0.9"/>
    <circle cx="13.5" cy="17" r="1" fill="rgba(255,255,255,0.8)"/>
    <circle cx="18.5" cy="17" r="1" fill="rgba(255,255,255,0.8)"/>
  </g>
  
  <!-- Micro data visualization -->
  <g opacity="0.8">
    <rect x="25" y="19" width="1.5" height="4" fill="white" rx="0.5"/>
    <rect x="27" y="17" width="1.5" height="6" fill="white" opacity="0.7" rx="0.5"/>
    <circle cx="26.5" cy="14" r="0.8" fill="white" opacity="0.6"/>
  </g>
</svg>"""
    
    return favicon_svg

if __name__ == "__main__":
    # Generate and save logos
    logo = create_atharman_logo()
    favicon = create_favicon()
    
    with open("atharman_logo.svg", "w") as f:
        f.write(logo)
    
    with open("atharman_favicon.svg", "w") as f:
        f.write(favicon)
    
    print("✅ Atharman logos generated successfully!")
    print("📁 Files created:")
    print("   • atharman_logo.svg (200x60)")
    print("   • atharman_favicon.svg (32x32)")