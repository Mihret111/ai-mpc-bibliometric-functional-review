"""AI family x application domain matrix to show the landscape heatmap"""
from common import load, body_text
import pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
exec(open('03_technique_eras.py').read().split('df, c = load()')[0])  # reuse FAM dict
DOM = {
 'Process / chemical': r'chemical|distillation|reactor|polymeriz|crystalliz|fermentat|process control|ph control|bioreactor|refin',
 'Power electronics / drives': r'pmsm|induction motor|inverter|converter|rectifier|motor drive|torque control|current control|power electronic',
 'Energy systems / microgrid': r'microgrid|smart grid|energy management|power system|wind turbine|photovoltaic|solar|battery energy|hydrogen|fuel cell',
 'Buildings / HVAC': r'hvac|building|air conditioning|heating|thermal comfort',
 'Automotive / AD': r'autonomous driving|autonomous vehicle|vehicle|automotive|engine|powertrain|adaptive cruise|lane',
 'Robotics / UAV': r'robot|manipulator|quadrotor|uav|unmanned|drone|legged|exoskeleton',
 'Aerospace': r'aircraft|spacecraft|satellite|aerospace|flight control|missile',
 'Water / environment': r'water treatment|wastewater|irrigation|water distribution|sewer',
 'Biomedical': r'glucose|insulin|diabete|anesthes|anaesthes|drug delivery|artificial pancrea|biomedical|neuromuscular',
 'Marine / ships': r'ship|vessel|marine|underwater|auv\b'}
df, c = load(); body = body_text(c)
for f,p in FAM.items(): c[f] = body.str.contains(p, regex=True)
for d,p in DOM.items(): c[d] = body.str.contains(p, regex=True)
M = pd.DataFrame({d:[c[c[d]][f].sum() for f in FAM] for d in DOM}, index=list(FAM))
fig, ax = plt.subplots(figsize=(10,4.8), dpi=150)
im = ax.imshow(M.values, cmap='YlGnBu', aspect='auto')
# ax.set_title('AI Family – Application Domain Heatmap')
ax.set_xticks(range(len(DOM))); ax.set_xticklabels(DOM, rotation=35, ha='right', fontsize=8)
ax.set_yticks(range(len(FAM))); ax.set_yticklabels(FAM, fontsize=8)
for i in range(len(FAM)):
    for j in range(len(DOM)):
        ax.text(j,i,int(M.iloc[i,j]),ha='center',va='center',fontsize=7,
                color='white' if M.iloc[i,j]>M.values.max()*.55 else 'black')
plt.colorbar(im, label='records'); plt.tight_layout()
plt.savefig('outputs/fig_technique_domain_heatmap.png'); M.to_csv('outputs/table_technique_domain.csv')
print('-> outputs/fig_technique_domain_heatmap.png')
