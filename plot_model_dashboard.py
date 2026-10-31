"""Week 7 ETAI model plots. Run: python plot_model_dashboard.py
Requires: pandas, numpy, matplotlib, scikit-learn (only for ROC/PR curves).
Uses results/runs.csv; optional results/predictions.csv for ROC/PR curves.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'results' / 'runs.csv'
if not INPUT.exists():
    INPUT = ROOT / 'runs.csv'
OUT = ROOT / 'results' / 'plots'
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'axes.titleweight':'bold',
                     'figure.facecolor':'#f8fafc','axes.facecolor':'#ffffff',
                     'savefig.facecolor':'#f8fafc'})

def pretty(s):
    return {'dummy':'Dummy','logistic_regression':'Logistic Regression',
            'naive_bayes':'Naive Bayes','decision_tree':'Decision Tree',
            'random_forest':'Random Forest','oblique_random_forest':'Oblique Random Forest',
            'adaboost':'AdaBoost','gradient_boosting':'Gradient Boosting',
            'hist_gradient_boosting':'HistGradientBoosting'}.get(s, str(s).replace('_',' ').title())

def save(fig, name):
    path=OUT/name
    fig.savefig(path,dpi=210,bbox_inches='tight')
    plt.close(fig)
    print('Created:',path)

runs=pd.read_csv(INPUT)
runs['tuned']=runs['tuned'].astype(str).str.lower().eq('true')
runs['mean']=pd.to_numeric(runs['mean'],errors='coerce')
runs=runs.dropna(subset=['model','mean'])
runs=runs.sort_values('run').drop_duplicates(['model','tuned','metric'],keep='last')
runs=runs[runs['metric'].eq('roc_auc')].copy()
if runs.empty:
    raise ValueError('No roc_auc rows in runs.csv')
runs['label']=runs['model'].map(pretty)
pivot=runs.pivot(index='model',columns='tuned',values='mean')
pivot['best']=pivot.max(axis=1)
pivot=pivot.sort_values('best',ascending=False)
models=pivot.index.tolist()
labels=[pretty(x) for x in models]

# Figure 1: grouped comparison bars (similar to supplied example)
fig,ax=plt.subplots(figsize=(15,7.5))
x=np.arange(len(models));w=.37
for tuned,offset,color,title in [(False,-w/2,'#3b82f6','Before tuning'),(True,w/2,'#f97316','After tuning')]:
    vals=pivot[tuned] if tuned in pivot else pd.Series(index=models,dtype=float)
    for i,m in enumerate(models):
        v=vals.get(m,np.nan)
        if pd.notna(v):
            ax.bar(i+offset,v,w,color=color,label=title if i==0 else None,zorder=3,alpha=.92)
            ax.text(i+offset,v+.012,f'{v:.3f}',ha='center',va='bottom',fontsize=8,rotation=90)
ax.axhline(.5,ls='--',color='#64748b',lw=1.1,label='Random baseline (0.50)')
ax.set_xticks(x,labels,rotation=28,ha='right')
ax.set_ylim(0,.86);ax.set_ylabel('Mean ROC-AUC (5-fold CV)')
ax.set_title('Model performance | Before vs. after hyperparameter tuning',fontsize=16,pad=19)
ax.grid(axis='y',alpha=.15,zorder=0)
ax.legend(ncol=3,frameon=False,loc='upper right')
fig.tight_layout();save(fig,'model_comparison_bars.png')

# Figure 2: fold-by-fold lines (real fold values from scoreboard)
fig,ax=plt.subplots(figsize=(13,7.5))
colors=plt.cm.tab10(np.linspace(0,1,len(models)))
for color,m in zip(colors,models):
    candidates=runs[runs.model.eq(m)].sort_values(['tuned'],ascending=False)
    row=candidates.iloc[0]
    vals=[pd.to_numeric(row.get(f'fold_{i}'),errors='coerce') for i in range(1,6)]
    if np.isfinite(vals).all():
        ax.plot(range(1,6),vals,marker='o',lw=2.1,ms=5,label=f'{pretty(m)}'+(' (tuned)' if row.tuned else ''),color=color)
ax.set_xticks(range(1,6));ax.set_xlabel('Cross-validation fold')
ax.set_ylabel('ROC-AUC');ax.set_ylim(.45,.85)
ax.axhline(.5,ls='--',color='#94a3b8',lw=1)
ax.set_title('Model stability | ROC-AUC across the five folds',fontsize=16,pad=18)
ax.grid(alpha=.18)
ax.legend(loc='center left',bbox_to_anchor=(1.02,.5),frameon=False,fontsize=9)
fig.tight_layout();save(fig,'model_fold_lines.png')

# Figure 3: optional actual ROC and PR curves. These REQUIRE out-of-sample probabilities.
PRED=ROOT/'results'/'predictions.csv'
if PRED.exists():
    from sklearn.metrics import roc_curve,auc,precision_recall_curve,average_precision_score
    preds=pd.read_csv(PRED)
    required={'model','y_true','y_prob'}
    if not required.issubset(preds.columns):
        print('Skipping ROC/PR curves: predictions.csv requires model,y_true,y_prob columns')
    else:
        fig,(ax1,ax2)=plt.subplots(1,2,figsize=(15,6.5))
        for m,g in preds.groupby('model'):
            y=pd.to_numeric(g['y_true'],errors='coerce')
            p=pd.to_numeric(g['y_prob'],errors='coerce')
            ok=y.notna() & p.notna();y=y[ok].astype(int);p=p[ok]
            if y.nunique()!=2:continue
            fpr,tpr,_=roc_curve(y,p)
            prec,rec,_=precision_recall_curve(y,p)
            ax1.plot(fpr,tpr,lw=2,label=f'{pretty(m)} (AUC={auc(fpr,tpr):.3f})')
            ax2.plot(rec,prec,lw=2,label=f'{pretty(m)} (AP={average_precision_score(y,p):.3f})')
        ax1.plot([0,1],[0,1],'--',color='#94a3b8',label='Chance')
        ax1.set(xlabel='False positive rate',ylabel='True positive rate',title='ROC curves')
        ax2.set(xlabel='Recall',ylabel='Precision',title='Precision–Recall curves')
        for ax in (ax1,ax2):
            ax.set_xlim(0,1);ax.set_ylim(0,1.02);ax.grid(alpha=.16);ax.legend(fontsize=8,loc='best')
        fig.suptitle('Out-of-sample classification curves',fontsize=16,fontweight='bold')
        fig.tight_layout();save(fig,'roc_pr_curves.png')
else:
    print('ROC and PR curves require results/predictions.csv with model,y_true,y_prob from held-out/OOF predictions.')
