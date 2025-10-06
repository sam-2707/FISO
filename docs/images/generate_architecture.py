import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# IEEE-standard system architecture block diagram
fig, ax = plt.subplots(1, 1, figsize=(14, 10))

# Define colors for IEEE standard
colors = {
    'user': '#E6F3FF',
    'frontend': '#CCE5FF', 
    'backend': '#99CCFF',
    'ai': '#66B2FF',
    'data': '#3399FF',
    'cloud': '#0080FF'
}

# Helper function to create rounded rectangles
def add_block(ax, x, y, width, height, text, color, fontsize=10):
    rect = patches.FancyBboxPatch((x, y), width, height,
                                boxstyle="round,pad=0.1",
                                facecolor=color, edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(x + width/2, y + height/2, text, ha='center', va='center',
            fontsize=fontsize, fontweight='bold', wrap=True)

# Helper function to draw arrows
def add_arrow(ax, x1, y1, x2, y2, label='', offset_label=0.1):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2 + offset_label
        ax.text(mid_x, mid_y, label, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                fontsize=8)

# User layer
add_block(ax, 1, 8.5, 2, 1, 'Enterprise\nUser', colors['user'], 12)

# Frontend layer
add_block(ax, 5, 8.5, 2.5, 1, 'React Dashboard\n(Frontend)', colors['frontend'], 11)
add_block(ax, 8, 8.5, 2, 1, 'WebSocket\nClient', colors['frontend'], 10)

# Backend layer
add_block(ax, 4, 6.5, 2, 1, 'API Gateway\n(Security)', colors['backend'], 10)
add_block(ax, 7, 6.5, 2, 1, 'Production\nServer', colors['backend'], 10)
add_block(ax, 10, 6.5, 2, 1, 'Real-Time\nServer', colors['backend'], 10)

# AI Engine layer
add_block(ax, 2, 4.5, 2, 1, 'Cost Prediction\n(Prophet)', colors['ai'], 9)
add_block(ax, 5, 4.5, 2, 1, 'Anomaly Detection\n(Isolation Forest)', colors['ai'], 9)
add_block(ax, 8, 4.5, 2, 1, 'Optimization\nEngine', colors['ai'], 9)
add_block(ax, 11, 4.5, 2, 1, 'NLP\nProcessor', colors['ai'], 9)

# Data layer
add_block(ax, 3, 2.5, 2, 1, 'Production DB\n(SQLite)', colors['data'], 10)
add_block(ax, 6, 2.5, 2, 1, 'Analytics DB\n(SQLite)', colors['data'], 10)
add_block(ax, 9, 2.5, 2, 1, 'Cache\n(Redis)', colors['data'], 10)

# Cloud providers
add_block(ax, 2, 0.5, 1.5, 1, 'AWS', colors['cloud'], 10)
add_block(ax, 4, 0.5, 1.5, 1, 'Azure', colors['cloud'], 10)
add_block(ax, 6, 0.5, 1.5, 1, 'GCP', colors['cloud'], 10)

# Add connections with labels
add_arrow(ax, 3, 8.5, 5, 8.8, 'HTTP/HTTPS')
add_arrow(ax, 6.2, 8.5, 5, 7.5, 'REST API')
add_arrow(ax, 9, 8.5, 11, 7.5, 'WebSocket')
add_arrow(ax, 8, 6.5, 6, 5.5, 'ML Models')
add_arrow(ax, 11, 6.5, 12, 5.5, 'NLP')
add_arrow(ax, 8, 4.5, 7, 3.5, 'Data')
add_arrow(ax, 4, 2.5, 3.5, 1.5, '2-min\nInterval')

# Layer labels
ax.text(0.5, 9, 'User Layer', rotation=90, va='center', fontsize=12, fontweight='bold')
ax.text(0.5, 7, 'Presentation\nLayer', rotation=90, va='center', fontsize=12, fontweight='bold')
ax.text(0.5, 5, 'AI/ML Layer', rotation=90, va='center', fontsize=12, fontweight='bold')
ax.text(0.5, 3, 'Data Layer', rotation=90, va='center', fontsize=12, fontweight='bold')
ax.text(0.5, 1, 'Cloud Layer', rotation=90, va='center', fontsize=12, fontweight='bold')

# Title and formatting
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.set_title('FISO Enterprise AI Platform - System Architecture', fontsize=16, fontweight='bold', pad=20)
ax.axis('off')

plt.tight_layout()
plt.savefig('docs/images/system_architecture.png', dpi=300, bbox_inches='tight')
plt.close()

print("Generated: system_architecture.png")