"""One-command reproduction of frozen predictions and all current summaries."""
from pathlib import Path
import argparse
import subprocess
import sys
from final_result_tables import generate, compare

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.output_dir.exists(): raise SystemExit('Choose a new output directory; existing results are never overwritten.')
    root=args.bundle.resolve(); data=root/'Supplementary_Tables'; code=root/'Code'
    args.output_dir.mkdir(parents=True)
    def run(name,*params): subprocess.run([sys.executable,str(code/name),*map(str,params)],check=True)
    run('reproduce_public_vectors.py','--evidence',data/'Table_S3_final_prediction_evidence.tsv',
        '--expected',data/'Table_S4_sealed_predictions.tsv','--method-dir',code/'92_confirmatory_validation_v2/method',
        '--output-dir',args.output_dir/'vectors')
    run('reproduce_public_statistics.py','--membership',data/'Table_S2_case_membership.tsv',
        '--predictions',args.output_dir/'vectors/reproduced_predictions.tsv','--truth',data/'Table_S5_AI_reference.tsv',
        '--output-dir',args.output_dir/'AI_statistics')
    for original,new in [('Table_S13_AI_method_metrics.tsv','V3_METHOD_METRICS.tsv'),
        ('Table_S14_AI_terminal_matrices.tsv','V3_TERMINAL_MATRICES.tsv'),
        ('Table_S15_DOI_access_sensitivity.tsv','V3_C4_SOURCE_SENSITIVITY.tsv')]:
        compare(args.output_dir/'AI_statistics'/new,data/original)
    summary=generate(data,args.output_dir/'current_results')
    for original,new in [('Table_S7_human_AI_agreement.tsv','HUMAN_AI_REFERENCE_AGREEMENT.tsv'),
        ('Table_S9_human_method_metrics.tsv','HUMAN_REFERENCE_METHOD_METRICS.tsv'),
        ('Table_S10_human_paired_comparison.tsv','HUMAN_REFERENCE_C2_C4_PAIRED_COMPARISON.tsv'),
        ('Table_S11_AI_D_gate_gap_case_matrix.tsv','AI_D_GATE_GAP_CASE_MATRIX.tsv'),
        ('Table_S12_gate_gap_marginals_combinations.tsv','GATE_GAP_MARGINALS_AND_COMBINATIONS.tsv'),
        ('Table_S16_posthoc_history_sensitivity.tsv','POSTHOC_RECRUITMENT_EXTRACTOR_SENSITIVITY.tsv'),
        ('Table_S17_human_terminal_matrices.tsv','HUMAN_REFERENCE_TERMINAL_MATRICES.tsv')]:
        compare(args.output_dir/'current_results'/new,data/original)
    for path in (root/'Source_Data').glob('Fig[2345]*.tsv'):
        name='GATE_GAP_MARGINALS_AND_COMBINATIONS.tsv' if path.name=='Fig4_gate_gap_marginals_combinations.tsv' else path.name
        compare(args.output_dir/'current_results'/name,path)
    print('PASS: 80 cases; 8 frozen methods; AI and author summaries; paired transitions; gate gaps; history sensitivity; Fig2-5 source data.')
    print(f"Human-AI agreement {summary['human_AI_exact_agreement_n']}/80; kappa={summary['human_AI_cohen_kappa']:.6f}")

if __name__=='__main__': main()
