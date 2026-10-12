"""Deterministic summaries of frozen vectors and references; no AI or tuning."""
from __future__ import annotations
import csv
import json
import math
from collections import Counter
from pathlib import Path
from scipy.stats import binomtest
from reproduce_public_statistics import ratio, METHODS, TRUTHS, STATES

TABLES = {
    'members': 'Table_S2_case_membership.tsv',
    'evidence': 'Table_S3_final_prediction_evidence.tsv',
    'predictions': 'Table_S4_sealed_predictions.tsv',
    'truth': 'Table_S5_AI_reference.tsv',
    'human': 'Table_S6_author_reference.tsv',
    'history': 'Table_S18_extractor_history.tsv',
}
GAPS = ('ownership_unmet', 'host_separation_unmet', 'physical_ion_unmet',
        'current_flux_unmet', 'catalytic_separation_unmet', 'provenance_unmet')

def read(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))

def write(path, rows, fields=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]), delimiter='\t', extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)

def gaps(vector):
    """Exactly the frozen audit predicates, not a new scientific rule."""
    o, c, w, h, cat, p = (vector[k] for k in
        ('observation','carrier_tests','ownership_tests','host_context','catalytic_context','provenance'))
    current = o['current_detected'] or o['direct_ion_flux_detected']
    physical = any(c[k] for k in ('controlled_gradient_reversal','bi_ionic_permeability',
        'direct_tracer_or_encapsulated_flux','single_channel_ion_identity')) and c['ion_identity'] not in ('UNRESOLVED','NONION_ELECTRON')
    purified = o['system'] == 'PURIFIED_RECONSTITUTED' and w['purified_target_reconstitution'] and w['protein_free_control']
    owner = purified or w['target_specific_current_loss_and_rescue'] or w['pathway_mutation_abolishes_ionic_endpoint_while_other_function_retained']
    host = o['system'] == 'PURIFIED_RECONSTITUTED' or (
        bool(h['applicable_confounders']) and set(h['excluded_confounders']) == set(h['applicable_confounders'])
        and h['ionic_endpoint_survives_controls'])
    catalytic = not cat['plausible_electrogenic_reaction'] or bool(cat['separation_methods'])
    provenance = not any(v in ('UNRESOLVED','CONFLICTING') for v in p.values())
    return dict(zip(GAPS, (int(not x) for x in (owner,host,physical,current,catalytic,provenance))))

def validate_ids(items):
    ids = [r['case_id'] for r in items]
    if len(ids) != 80 or len(set(ids)) != 80:
        raise ValueError('Expected 80 unique case IDs')
    return set(ids)

def generate(data_dir, out_dir):
    data_dir, out_dir = Path(data_dir), Path(out_dir)
    tables = {k: read(data_dir/v) for k,v in TABLES.items()}
    ids = validate_ids(tables['members'])
    if any(validate_ids(v) != ids for v in tables.values()):
        raise ValueError('Frozen input IDs differ')
    by = {k:{r['case_id']:r for r in v} for k,v in tables.items()}
    ordered = [r['case_id'] for r in tables['members']]
    human = {cid:by['human'][cid]['reviewer_label'] for cid in ordered}
    ai = {cid:by['truth'][cid]['final_truth_DIAU'] for cid in ordered}
    pred = by['predictions']
    if any(v not in TRUTHS for v in list(human.values())+list(ai.values())):
        raise ValueError('Invalid reference label')
    hc, ac = Counter(human.values()), Counter(ai.values())
    confusion = Counter((human[c],ai[c]) for c in ordered)
    agree = sum(human[c] == ai[c] for c in ordered)
    pe = sum(hc[t]*ac[t] for t in TRUTHS)/80**2
    summary = {'cases':80, 'human_AI_exact_agreement_n':agree,
        'human_AI_cohen_kappa':(agree/80-pe)/(1-pe),
        'human_counts':dict(hc), 'AI_counts':dict(ac),
        'human_reference_design':'Single project-author case-level blinded sensitivity review; not external dual-human validation'}
    summary['recruitment_strata']=dict(Counter(r['source_stratum'] for r in tables['members']))
    summary['source_access_counts']=dict(Counter(r['source_access'] for r in tables['members']))
    summary['distinct_DOI_sources']=len({r['DOI'].strip().lower() for r in tables['members']})
    h_d=sum(human[c]=='D' for c in ordered); a_d=sum(ai[c]=='D' for c in ordered)
    binary_agree=sum((human[c]=='D')==(ai[c]=='D') for c in ordered)
    binary_pe=(h_d*a_d+(80-h_d)*(80-a_d))/80**2
    summary['D_vs_non_D_agreement_n']=binary_agree
    summary['D_vs_non_D_cohen_kappa']=(binary_agree/80-binary_pe)/(1-binary_pe)
    agreement = [{'case_id':c,'human_label':human[c],
        'human_confidence':by['human'][c]['confidence'],'ai_reference_label':ai[c],
        'ai_reference_confidence':by['truth'][c]['confidence'],
        'exact_agreement':str(human[c]==ai[c]).lower(),
        'd_vs_non_d_agreement':str((human[c]=='D')==(ai[c]=='D')).lower()} for c in ordered]
    write(out_dir/'HUMAN_AI_REFERENCE_AGREEMENT.tsv', agreement)
    metrics, matrices = [], []
    for m in METHODS:
        counts = Counter((human[c],pred[c][m]) for c in ordered)
        for t in TRUTHS:
            matrices.append({'method':m,'human_truth':t,**{s:counts[t,s] for s in STATES}})
        for t in TRUTHS:
            metrics.append({'method':m,'metric':f'human_{t}_count','numerator':hc[t],
                'denominator':80,'estimate':'','ci95_lower':'','ci95_upper':'','ci_method':'count only'})
        for prefix, labels in (('D',('D',)),('I_plus_A',('I','A'))):
            for s in STATES:
                metrics.append({'method':m,'metric':f'{prefix}_to_{s}',
                    'numerator':sum(counts[t,s] for t in labels),'denominator':sum(hc[t] for t in labels),
                    'estimate':'','ci95_lower':'','ci95_upper':'','ci_method':'count only'})
        abstain = sum(counts[t,'ABSTAIN'] for t in TRUTHS)
        resolved_abstain = sum(counts[t,'ABSTAIN'] for t in ('D','I','A'))
        resolved = 80-hc['U']
        for name,k,n in (
            ('direct_recovery_D',counts['D','DIRECT_PROMOTE'],hc['D']),
            ('erroneous_direct_promotion_I_plus_A',sum(counts[t,'DIRECT_PROMOTE'] for t in ('I','A')),hc['I']+hc['A']),
            ('total_abstention_all80',abstain,80),
            ('abstention_rate_DIA_resolved',resolved_abstain,resolved),
            ('coverage_DIA_resolved_excluding_U',resolved-resolved_abstain,resolved),
            ('coverage_all80_nonabstain_manuscript_definition',80-abstain,80),
            ('direct_promotion_U',counts['U','DIRECT_PROMOTE'],hc['U'])):
            r = ratio(k,n)
            r['ci_method'] = 'two-sided Clopper-Pearson exact 95%' if n else None
            metrics.append({'method':m,'metric':name,**r})
    write(out_dir/'HUMAN_REFERENCE_METHOD_METRICS.tsv',metrics)
    write(out_dir/'HUMAN_REFERENCE_TERMINAL_MATRICES.tsv',matrices)
    pairs=[]
    for name,labels in (('human_D',('D',)),('human_I_plus_A',('I','A'))):
        subset=[c for c in ordered if human[c] in labels]
        cells=Counter((pred[c]['C2']=='DIRECT_PROMOTE',pred[c]['C4']=='DIRECT_PROMOTE') for c in subset)
        b,c=cells[True,False],cells[False,True]
        pairs.append({'stratum':name,'n':len(subset),
            'C2_direct_C4_direct':cells[True,True], 'C2_direct_C4_not_direct':b,
            'C2_not_direct_C4_direct':c,'both_not_direct':cells[False,False],
            'discordant_pairs':b+c,'exact_mcnemar_two_sided_p':float(binomtest(b,b+c,.5).pvalue) if b+c else 1.,
            'paired_direct_recovery_difference_C2_minus_C4':(b-c)/len(subset)})
    write(out_dir/'HUMAN_REFERENCE_C2_C4_PAIRED_COMPARISON.tsv',pairs)
    gate_rows=[]
    for c in ordered:
        if ai[c] != 'D': continue
        e=by['evidence'][c]
        v=json.loads(e['evidence_json'])
        g=gaps(v)
        gate_rows.append({'case_id':c,'target':by['members'][c]['target'],'DOI':by['members'][c]['DOI'],
            'C2':pred[c]['C2'],'C4':pred[c]['C4'],'historical_state':pred[c]['historical_state'],**g,
            'unmet_evidence_dimensions':';'.join(k for k in GAPS if g[k]) or 'NONE',
            'source_locations':e.get('field_provenance') or e.get('source_spans') or 'UNKNOWN'})
    write(out_dir/'AI_D_GATE_GAP_CASE_MATRIX.tsv',gate_rows)
    write(out_dir/'Fig4_gate_gaps_source_data.tsv',gate_rows, ['case_id',*GAPS])
    patterns=Counter(tuple(r[k] for k in GAPS) for r in gate_rows)
    gate_summary=[{'record_kind':'MARGINAL','dimension_or_pattern':k,'count':sum(r[k] for r in gate_rows),
        'denominator':len(gate_rows),**{g:'' for g in GAPS}} for k in GAPS]
    gate_summary += [{'record_kind':'EXACT_COMBINATION','dimension_or_pattern':';'.join(k for k,x in zip(GAPS,t) if x) or 'NONE',
        'count':n,'denominator':len(gate_rows),**dict(zip(GAPS,t))}
        for t,n in sorted(patterns.items(),key=lambda item:(-item[1],item[0]))]
    write(out_dir/'GATE_GAP_MARGINALS_AND_COMBINATIONS.tsv',gate_summary)
    summary['AI_D_gate_gap_counts']={k:sum(r[k] for r in gate_rows) for k in GAPS}
    # Recruitment provenance is the fixed case-ID boundary, not inferred access class.
    groups=[('existing_41',[c for c in ordered if int(c.split('-')[-1])<=41]),
        ('new_39',[c for c in ordered if int(c.split('-')[-1])>41])]
    if len(groups[0][1])!=41 or len(groups[1][1])!=39:
        raise ValueError('Unexpected frozen recruitment-history boundary')
    for c in groups[1][1]:
        if not by['members'][c]['source_access'].startswith('NEW_FREE'):
            raise ValueError('New-case history disagrees with membership source record')
    groups += [(m,[c for c in ordered if by['history'][c]['primary_model_id']==m])
        for m in ('gpt-6-astra','gpt-6-luna')]
    posthoc=[]
    for group,selected in groups:
        tc=Counter(ai[c] for c in selected)
        for m in ('C2','C4'):
            for metric,k,n in (
                ('promotion_in_AI_D',sum(ai[c]=='D' and pred[c][m]=='DIRECT_PROMOTE' for c in selected),tc['D']),
                ('promotion_in_AI_I_plus_A',sum(ai[c] in ('I','A') and pred[c][m]=='DIRECT_PROMOTE' for c in selected),tc['I']+tc['A']),
                ('abstention_all',sum(pred[c][m]=='ABSTAIN' for c in selected),len(selected)),
                ('nonabstention_all',sum(pred[c][m]!='ABSTAIN' for c in selected),len(selected)),
                ('promotion_in_AI_U',sum(ai[c]=='U' and pred[c][m]=='DIRECT_PROMOTE' for c in selected),tc['U'])):
                posthoc.append({'stratum':group,'stratum_n':len(selected),'reference':'AI', 'method':m,
                    'metric':metric,'numerator':k,'denominator':n,'estimate':k/n if n else '',
                    'analysis_status':'POST_HOC_DESCRIPTIVE_NONRANDOM_HISTORY_SPLIT'})
    write(out_dir/'POSTHOC_RECRUITMENT_EXTRACTOR_SENSITIVITY.tsv',posthoc)
    summary['history_stratum_counts']={g:len(s) for g,s in groups}
    summary['disagreement_case_ids']=[c for c in ordered if human[c]!=ai[c]]
    (out_dir/'FINAL_REPRODUCTION_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Figure source files are explicit projections of the reported tables.
    from reproduce_public_statistics import read_tsv
    aimetrics=read_tsv(data_dir/'Table_S13_AI_method_metrics.tsv')
    fig2=[]
    for reference,source in (('AI',aimetrics),('Author',metrics)):
        for m in ('C2','C4'):
            for shown,old in (('promotion_in_D','direct_recovery_D'),('promotion_in_I_plus_A','erroneous_direct_promotion_I_plus_A'),
                ('abstention_all80','total_abstention' if reference=='AI' else 'total_abstention_all80')):
                r=next(r for r in source if r['method']==m and r['metric']==old)
                fig2.append({'reference':reference,'method':m,'figure_metric':shown,
                    **{k:r[k] for k in ('numerator','denominator','estimate','ci95_lower','ci95_upper')}})
    write(out_dir/'Fig2_promotion_abstention_source_data.tsv',fig2)
    write(out_dir/'Fig3a_human_AI_confusion_source_data.tsv',[
        {'human_label':h,'AI_label':a,'count':confusion[h,a]} for h in TRUTHS for a in TRUTHS])
    write(out_dir/'Fig3b_human_D_paired_source_data.tsv',[
        {'C2_direct':x,'C4_direct':y,'count':sum(human[c]=='D' and (pred[c]['C2']=='DIRECT_PROMOTE')==x and
            (pred[c]['C4']=='DIRECT_PROMOTE')==y for c in ordered)} for x in (True,False) for y in (True,False)])
    challenge_fields=['case_id','target','apparent_direct_DOI','apparent_direct_evidence','apparent_direct_location',
        'confound_type','confounding_DOI','confounding_evidence','confounding_location','why_this_is_hard_negative']
    write(out_dir/'Fig5_attribution_challenge_source_data.tsv',read(data_dir/'Table_S1_attribution_challenge_details.tsv'),challenge_fields)
    return summary

def compare(actual,expected):
    """Compare semantic cells, allowing only numeric rendering differences."""
    a,b=read(actual),read(expected)
    if len(a)!=len(b) or set(a[0])!=set(b[0]):
        raise AssertionError(f'Table shape mismatch: {Path(expected).name}')
    for i,(ra,rb) in enumerate(zip(a,b)):
        for k in rb:
            x,y=ra[k],rb[k]
            if x==y: continue
            try: equal=math.isclose(float(x),float(y),rel_tol=1e-12,abs_tol=1e-12)
            except (ValueError,TypeError): equal=False
            if not equal: raise AssertionError(f'{Path(expected).name} row {i+1} field {k}: {x!r} != {y!r}')
