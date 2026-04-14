import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# Path to the project database
DB_PATH = "risk_intelligence.db"

def generate_stats():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}. Run scans first!")
        return

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT build_id, risk_score, baseline_score FROM builds", conn)
    conn.close()

    if df.empty:
        print("❌ No data found in database. Run scans first!")
        return

    # Calculate Alert Reduction / Delta
    df['delta'] = df['baseline_score'] - df['risk_score']
    
    print("\n📊 --- Research Paper Statistics ---")
    print(f"Total Scans Analyzed: {len(df)}")
    print(f"Average Baseline Score (CVSS-only): {df['baseline_score'].mean():.2f}")
    print(f"Average Adaptive Risk Score (ACRIF): {df['risk_score'].mean():.2f}")
    print(f"Average Risk Reduction (Context-Aware): {df['delta'].mean():.2f} pts")
    
    # Identify 'Blocked' vs 'Allowed' shifts
    # (Assuming threshold of 70)
    baseline_blocks = len(df[df['baseline_score'] > 70])
    acrif_blocks = len(df[df['risk_score'] > 70])
    suppressed_alerts = baseline_blocks - acrif_blocks
    
    print(f"Baseline 'Critical' Blocks (>70): {baseline_blocks}")
    print(f"ACRIF 'Critical' Blocks (>70): {acrif_blocks}")
    print(f"Reduction in Alert Fatigue: {suppressed_alerts} deployments allowed due to context analysis.")

    # Generate a simple visualization comparison
    try:
        df.plot(x='build_id', y=['baseline_score', 'risk_score'], kind='bar', figsize=(10, 6))
        plt.title("CVSS Baseline vs Adaptive Risk Intelligence (ACRIF)")
        plt.ylabel("Risk Score (0-100)")
        plt.axhline(y=70, color='r', linestyle='--', label='Block Threshold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig("paper_evaluation_chart.png")
        print("\n📈 Chart saved as 'paper_evaluation_chart.png'")
    except Exception as e:
        print(f"\n⚠️ Could not generate chart (Matplotlib error): {str(e)}")

if __name__ == "__main__":
    generate_stats()
