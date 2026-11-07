'''
Builds the AGENT-P website pages (index.html, getting-started.html, example.html, full-run.html) from the content below.
Every page gets the same left sidebar: the page list, the sections of the current page, and links.

Write code blocks as plain text between <<<Python (or <<<Terminal) and >>>: they are escaped and
highlighted here. %CLONE%, %COLAB%, %MODELS%, %REPO%, %BRANCH% are replaced by the values below.

usage: python3 make_site.py
'''

import html
import re

BRANCH = 'agentp-update-20261105'   # change to 'main' after the branch is merged
REPO = 'https://github.com/nhunghoang/agentp'
COLAB = f'https://colab.research.google.com/github/nhunghoang/agentp/blob/{BRANCH}/example/colab_example.ipynb'
MODELS = 'https://drive.google.com/file/d/1llysnSFOut3E_g1omlgQfi-N5fptuuLa/view?usp=sharing'
CLONE = f'git clone -b {BRANCH} {REPO}.git' if BRANCH != 'main' else f'git clone {REPO}.git'


def highlight_line(line, lang):
    ## split off a trailing comment (a "#" outside quotes)
    code, comment, quote = line, '', None
    for i, ch in enumerate(line):
        if ch in '\'"' and quote is None: quote = ch
        elif ch == quote: quote = None
        elif ch == '#' and quote is None and (lang == 'Python' or i == 0 or line[i - 1] == ' '):
            code, comment = line[:i], line[i:]
            break
    out = html.escape(code)
    if lang == 'Python':
        out = re.sub(r'(&#x27;.*?&#x27;)', r'<span class="s">\1</span>', out)
        out = re.sub(r'\b(from|import)\b', r'<span class="k">\1</span>', out)
    if comment:
        out += f'<span class="c">{html.escape(comment)}</span>'
    return out


def code(lang, text):
    body = '\n'.join(highlight_line(l, lang) for l in text.strip('\n').split('\n'))
    return (f'<div class="code"><div class="code-header"><span>{lang}</span></div>'
            f'<pre tabindex="0">{body}</pre></div>')




def render(text):
    """fill in %NAME% links and turn <<<Lang ... >>> markers into code blocks"""
    for name, value in [('CLONE', CLONE), ('COLAB', COLAB), ('MODELS', MODELS), ('REPO', REPO), ('BRANCH', BRANCH)]:
        text = text.replace('%' + name + '%', value)
    return re.sub(r'<<<(\w+)\n(.*?)\n>>>', lambda m: code(m.group(1), m.group(2)), text, flags=re.S)

## ---------------------------------------------------------------------------------------------
## Getting started: requirements, installation, models
## ---------------------------------------------------------------------------------------------
GETTING_STARTED = [
('requirements', 'Requirements', r'''
<p>AGENT-P runs on <strong>Linux</strong> and <strong>macOS</strong>. It is a Python package that calls a few genetics programs, all of which are installed together with conda in the next step:</p>
<div class="table-scroll"><table>
  <thead><tr><th scope="col">Software</th><th scope="col">Version</th><th scope="col">Used for</th></tr></thead>
  <tbody>
    <tr><td>Python</td><td>3.10</td><td>AGENT-P itself, with numpy (&lt; 2), pandas, SciPy (&ge; 1.11), statsmodels, h5py, matplotlib, and bgen-reader</td></tr>
    <tr><td><a href="https://www.cog-genomics.org/plink/2.0/">PLINK 2</a></td><td>2.00a5.12</td><td>quality control of genotypes, and preparing genotypes for the models</td></tr>
    <tr><td><a href="https://enkre.net/cgi-bin/code/bgen/doc/trunk/doc/wiki/bgenix.md">bgenix</a></td><td>1.1.7</td><td>reading genotypes in BGEN format</td></tr>
    <tr><td><a href="https://rgcgithub.github.io/regenie">REGENIE</a></td><td>3.6</td><td>GWAS (optional)</td></tr>
    <tr><td>R</td><td>4.2</td><td>FUSION models (with optparse, RColorBrewer, and plink2R, which comes with AGENT-P)</td></tr>
  </tbody>
</table></div>
<ul class="list">
  <li><strong>Disk space:</strong> about 2 GB for the expression models.</li>
  <li><strong>Memory:</strong> a laptop with 8 GB is enough for the example. For large cohorts (tens of thousands of subjects), use a computing cluster.</li>
  <li><strong>Windows:</strong> use <a href="https://learn.microsoft.com/en-us/windows/wsl/install">WSL</a> (Windows Subsystem for Linux) and follow the Linux instructions.</li>
</ul>
'''),

('install', 'Install', r'''
<p>The easiest way to install AGENT-P and everything it needs is with conda (if you do not have conda, install <a href="https://github.com/conda-forge/miniforge">Miniforge</a> first). Open a terminal and run:</p>
<<<Terminal
%CLONE%
cd agentp
conda env create -f environment.yml      # takes 5-15 minutes
conda activate agentp
pip install --no-deps -e .
R CMD INSTALL agentp/external/plink2R/plink2R
>>>
<p>The commands on this page are run from this <code>agentp</code> folder.</p>
<p><strong>On a Mac with an Apple chip (M1&ndash;M4)</strong>, create the environment with the line below instead (the genetics programs are only available for Intel Macs, and run through Rosetta), and run <code>conda config --env --set subdir osx-64</code> after <code>conda activate agentp</code>:</p>
<<<Terminal
CONDA_SUBDIR=osx-64 conda env create -f environment.yml
>>>
<p class="note">Each time you open a new terminal, run <code>conda activate agentp</code> before using AGENT-P.</p>

<h3>Install with pip (PyPI)</h3>
<p>AGENT-P is also on <a href="https://pypi.org/project/agentp/">PyPI</a> (Python 3.9 or later):</p>
<<<Terminal
pip install agentp
>>>
<p>This installs AGENT-P and its Python packages only. PLINK 2, bgenix, REGENIE, and R (with plink2R, for FUSION) must be installed separately. Download the expression models (<code>models.tar.gz</code>, about 2 GB: the models of the four TWAS methods for the eight brain regions; see <a href="#models">Download the models</a>), and tell AGENT-P where they are at the start of each script:</p>
<<<Python
from agentp import set_models_dir
set_models_dir('/path/to/models')
>>>

'''),

('models', 'Download the models', r'''
<p>The expression models (about 2 GB) are not included in the GitHub repository. Download <a href="%MODELS%"><code>models.tar.gz</code></a> and extract it into the <code>agentp</code> folder inside the repository:</p>
<<<Terminal
cd agentp                                # the "agentp" folder inside the downloaded repository
tar -xzf ~/Downloads/models.tar.gz       # change the path if you saved the file elsewhere
cd ..
>>>
<p>The models are now in <code>agentp/models</code>: models from four TWAS methods for eight brain regions (GTEx v8). In AGENT-P, each method and region has a short code, and any method can be combined with any region, e.g. <code>SummaryTWAS(project, 'FUS', 'hippocampus')</code>:</p>
<div class="table-scroll"><table class="codes">
  <thead><tr><th scope="col">Method</th><th scope="col">Code</th></tr></thead>
  <tbody>
    <tr><td><a href="https://github.com/hakyimlab/MetaXcan">PrediXcan</a></td><td><code>PDX</code></td></tr>
    <tr><td><a href="https://github.com/Joker-Jerome/UTMOST">UTMOST</a></td><td><code>UTM</code></td></tr>
    <tr><td><a href="https://github.com/gamazonlab/MR-JTI">JTI (Joint-Tissue Imputation)</a></td><td><code>JTI</code></td></tr>
    <tr><td><a href="http://gusevlab.org/projects/fusion">FUSION</a></td><td><code>FUS</code></td></tr>
  </tbody>
</table></div>
<div class="table-scroll"><table class="codes">
  <thead><tr><th scope="col">Brain region</th><th scope="col">Code</th></tr></thead>
  <tbody>
    <tr><td>Dorsolateral prefrontal cortex</td><td><code>dlpfc</code></td></tr>
    <tr><td>Anterior cingulate cortex</td><td><code>ant-cingulate</code></td></tr>
    <tr><td>Amygdala</td><td><code>amygdala</code></td></tr>
    <tr><td>Hippocampus</td><td><code>hippocampus</code></td></tr>
    <tr><td>Caudate</td><td><code>caudate</code></td></tr>
    <tr><td>Putamen</td><td><code>putamen</code></td></tr>
    <tr><td>Nucleus accumbens</td><td><code>nuc-accumbens</code></td></tr>
    <tr><td>Cerebellar hemisphere</td><td><code>cerebellar-hemi</code></td></tr>
  </tbody>
</table></div>
<p class="note">The example does not need this download: it uses a small set of example models that comes with AGENT-P.</p>
'''),

('check', 'Check the installation', r'''
<p>Each of these commands should print a version or a message, without errors:</p>
<<<Terminal
python -c "import agentp; print('AGENT-P is ready')"
plink2 --version
bgenix -help | head -1
regenie --version
Rscript -e "suppressMessages(library(plink2R)); cat('plink2R is ready\n')"
>>>
<p>Then you can either:</p>
<ol class="list">
  <li>run the <a href="example.html#local">example on your computer</a>, which uses the small example models; or</li>
  <li>use the full models: test the pipeline with <code>python tests/test_pipeline.py</code>, which runs every step of AGENT-P (add <code>--fusion</code> to include FUSION), then analyze your own data with the <a href="full-run.html">Full run</a>.</li>
</ol>
'''),

('troubleshooting', 'Troubleshooting', r'''
<ul class="list">
  <li><strong><code>git clone</code> fails with an error about "LFS" or "smudge filter".</strong> Clone without the large files (the models come from the download above anyway): <code>GIT_LFS_SKIP_SMUDGE=1 %CLONE%</code>.</li>
  <li><strong><code>conda env create</code> is very slow or runs out of memory.</strong> Use <a href="https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html">micromamba</a> with the same file: <code>micromamba create -f environment.yml</code>.</li>
  <li><strong><code>numpy</code> or <code>h5py</code> errors after installing.</strong> AGENT-P was installed without <code>--no-deps</code>, and pip replaced conda's packages. Remove the environment (<code>conda env remove -n agentp</code>) and install again.</li>
  <li><strong>On a Mac: "incompatible architecture".</strong> The environment was created without <code>CONDA_SUBDIR=osx-64</code>. Remove it and create it again as above. The first run on a Mac can take a few extra minutes while Rosetta translates the programs.</li>
</ul>
'''),
]

## ---------------------------------------------------------------------------------------------
## Example: the Google Colab notebook, and the same example on your computer
## ---------------------------------------------------------------------------------------------
EXAMPLE = [
('colab', 'Run it in Google Colab', r'''
<p>The example notebook runs in Google Colab, with nothing to install on your computer. <a href="%COLAB%">Open the example in Colab</a>, then choose <strong>Runtime &rarr; Run all</strong>. The run takes about 20 minutes and needs a Google account.</p>
<p>The example uses data that comes with AGENT-P:</p>
<ul class="list">
  <li><strong>Subjects:</strong> 2,000 example subjects, with genotypes (chromosomes 1&ndash;22), covariates (age, sex, and 3 genetic principal components), and four brain volumes</li>
  <li><strong>GWAS:</strong> a GWAS of amygdala volume in the same subjects, for the summary-level TWAS</li>
  <li><strong>Models:</strong> a small set of caudate models</li>
</ul>
<p>It tests predicted gene expression in the <strong>caudate</strong> (JTI models) for association with <strong>amygdala volume</strong>.</p>
'''),

('steps', 'What the notebook does', r'''
<div class="table-scroll"><table>
  <thead><tr><th scope="col">Step</th><th scope="col">What it does</th></tr></thead>
  <tbody>
    <tr><td>1. Install</td><td>downloads AGENT-P from GitHub and installs it with the programs it needs (about 5&ndash;8 minutes)</td></tr>
    <tr><td>2. Create the project</td><td>loads the example subjects, and quality-controls their genotypes</td></tr>
    <tr><td>3. Summary-level TWAS</td><td>combines the GWAS of amygdala volume with the JTI caudate models</td></tr>
    <tr><td>4. Genotype-level TWAS</td><td>predicts caudate gene expression for each subject, then tests it for association with amygdala volume (the longest step)</td></tr>
    <tr><td>5. Results</td><td>shows how many genes were tested and the top genes of both TWAS</td></tr>
    <tr><td>6. Plots</td><td>a Manhattan plot of the genotype-level TWAS, and a Miami plot comparing both TWAS</td></tr>
  </tbody>
</table></div>
<p class="note">With only 2,000 subjects, no gene passes the significance threshold; the example shows how AGENT-P works.</p>
'''),

('change', 'Try other models or traits', r'''
<p><strong>Another model set:</strong> in the TWAS cells of the notebook, replace <code>'JTI'</code> with <code>'PDX'</code> (PrediXcan), <code>'UTM'</code> (UTMOST), or <code>'FUS'</code> (FUSION), and replace <code>JTI_caudate</code> in the results and plot cells with the matching folder name (e.g. <code>PDX_caudate</code>).</p>
<p><strong>Another trait:</strong> the genotype-level TWAS can test any of the four example volumes (<code>putamen_volume</code>, <code>amygdala_volume</code>, <code>hippocampus_volume</code>, <code>caudate_volume</code>). The predicted gene expression is reused, so only the association test runs again:</p>
<<<Python
itwas = IndividualTWAS(project, 'JTI', 'caudate')
itwas.run_twas('hippocampus_volume')
>>>
<p>The summary-level TWAS needs a GWAS of the trait; the example includes one for amygdala volume only.</p>
'''),

('local', 'Run the example on your computer', r'''
<p>After <a href="getting-started.html">installing AGENT-P</a> (the full models are not needed), run the same example from the <code>agentp</code> folder:</p>
<<<Terminal
cd example
python run_example.py
>>>
<p>It takes about 10 minutes. The results are saved in <code>example/example_run/</code>, and the plots in <code>example/example_run/figures/</code>. To analyze your own data, see <a href="full-run.html">Full run</a>.</p>
'''),
]

## ---------------------------------------------------------------------------------------------
## Full run: your own data
## ---------------------------------------------------------------------------------------------
FULL_RUN = [
('inputs', 'Input data', r'''
<p>What you need depends on the TWAS you run. Summary-level TWAS needs only a GWAS; genotype-level TWAS (and GWAS) needs the data of individual subjects. Both use the full models (see <a href="getting-started.html#models">Getting started</a>), and all data must use rsIDs for SNPs.</p>
<div class="table-scroll"><table>
  <thead><tr><th scope="col">Input</th><th scope="col">Format</th><th scope="col">Added with</th></tr></thead>
  <tbody>
    <tr><th scope="row" colspan="3" class="group">Summary-level TWAS</th></tr>
    <tr><td>GWAS summary statistics</td><td>one file per trait, one row per SNP: SNP ID (rsID), the two alleles, and the effect size (beta) with its standard error or a p-value (see <a href="#summary">column names</a>)</td><td><code>stwas.add_gwas</code></td></tr>
    <tr><th scope="row" colspan="3" class="group">Genotype-level TWAS and GWAS</th></tr>
    <tr><td>Subject IDs</td><td>one ID per line, no header</td><td><code>project.set_subjects</code></td></tr>
    <tr><td>Covariates</td><td>a table with an <code>id</code> column and one column per covariate, e.g. age, sex, and genetic principal components (numbers only, e.g. sex as 0/1)</td><td><code>project.add_covariates</code></td></tr>
    <tr><td>Phenotypes</td><td>a table with an <code>id</code> column and one column per trait; the column names are the trait names</td><td><code>project.add_phenotypes</code></td></tr>
    <tr><td>Genotypes</td><td>one BGEN file per chromosome (1&ndash;22), each with a matching <code>.sample</code> file</td><td><code>project.add_genotypes</code></td></tr>
  </tbody>
</table></div>
<ul class="list">
  <li>The subject IDs must be the same in all files (in the <code>.sample</code> files, both ID columns).</li>
  <li>Tables are tab-separated by default; for comma-separated tables, add <code>sep=','</code>. To use only some columns, add <code>covar_cols=[...]</code> or <code>phen_cols=[...]</code>.</li>
  <li>AGENT-P cleans the genotypes before use: it keeps SNPs with less than 5% missing calls, a minor allele frequency of at least 1%, and a Hardy&ndash;Weinberg equilibrium p-value above 1e-5.</li>
  <li>Genotypes in VCF format can be converted to BGEN with <code>plink2</code> (see <a href="#troubleshooting">Troubleshooting</a>).</li>
  <li>Example files of every kind are in <code>example/example_data</code>.</li>
</ul>
'''),

('project', 'Create a project', r'''
<p>Write the steps on this page in a Python script (for example <code>my_analysis.py</code>), and run it with <code>python my_analysis.py</code>.</p>
<p>A project is a folder that keeps the inputs and results of one cohort together.</p>
<<<Python
from agentp import Project
project = Project('my_project')     # creates the folder "my_project"
>>>
'''),

('summary', 'Summary-level TWAS', r'''
<p>From GWAS summary statistics of a trait:</p>
<<<Python
from agentp import SummaryTWAS

stwas = SummaryTWAS(project, 'JTI', 'caudate')                  # model method and brain region
stwas.add_gwas('putamen_volume', 'putamen_volume_gwas.txt')     # trait name and GWAS file
stwas.run_twas('putamen_volume')
>>>
<p><strong>Column names.</strong> GWAS files made with AGENT-P's <code>GWAS</code> (see <a href="#options">More options</a>) are read without any extra settings. For other files, including REGENIE's own output, tell AGENT-P the column names:</p>
<<<Python
stwas.add_gwas('putamen_volume', 'putamen_volume_gwas.txt', sep='\t',
               snp_col='rsid', alt_col='a2', ref_col='a1',
               beta_col='beta', beta_se_col='se', pval_col='pval')
>>>
<ul class="list">
  <li><code>alt_col</code> is the <strong>effect allele</strong>: the allele that the beta refers to. <code>ref_col</code> is the other allele.</li>
  <li>If your file has a z-score or odds ratio instead of a beta, use <code>zscore_col</code> or <code>or_col</code>.</li>
  <li>FUSION models need the beta and p-value columns. REGENIE's own output has no p-value column: use <code>sep=' ', snp_col='ID', alt_col='ALLELE1', ref_col='ALLELE0', beta_col='BETA', beta_se_col='SE'</code> (every method except FUSION), or run the GWAS with AGENT-P's <code>GWAS</code>.</li>
</ul>
'''),

('genotype', 'Genotype-level TWAS', r'''
<p>From individual-level data. First add the subject data to the project (only once per project; see <a href="#inputs">Input data</a> for the file formats):</p>
<<<Python
project.set_subjects('subjects.txt')             # subject IDs
project.add_covariates('covariates.txt')         # e.g. age, sex, genetic principal components
project.add_phenotypes('phenotypes.txt')         # one or more traits
project.add_genotypes('genotypes', 'chr*.bgen')  # folder, and file names with * for the chromosome number
>>>
<p>Then predict gene expression and test the traits:</p>
<<<Python
from agentp import IndividualTWAS

itwas = IndividualTWAS(project, 'JTI', 'caudate')
itwas.predict_grex()                         # predict gene expression (once per method and region)
itwas.run_twas('putamen_volume')             # or a list: ['putamen_volume', 'caudate_volume']
>>>
'''),

('results', 'Results and plots', r'''
<p>Each TWAS saves one table per trait (tab-separated, one row per gene):</p>
<div class="table-scroll"><table>
  <thead><tr><th scope="col">TWAS</th><th scope="col">Results file</th></tr></thead>
  <tbody>
    <tr><td>Summary-level</td><td><code>my_project/sTWAS/JTI_caudate/putamen_volume.csv</code></td></tr>
    <tr><td>Genotype-level</td><td><code>my_project/iTWAS/JTI_caudate/putamen_volume.csv</code></td></tr>
  </tbody>
</table></div>
<p>The most important columns are <code>gene</code> (Ensembl gene ID), <code>zscore</code> (direction and strength of the association: positive means that higher expression goes with a larger trait value), and <code>pvalue</code>. A common threshold for significance is a Bonferroni correction: p &lt; 0.05 / (number of genes tested).</p>
<p><strong>Plots</strong> (saved as image files):</p>
<<<Python
from agentp import load_pvalues, manhattan_plot, miami_plot, scatter_plot

s = load_pvalues('my_project/sTWAS/JTI_caudate/putamen_volume.csv')
g = load_pvalues('my_project/iTWAS/JTI_caudate/putamen_volume.csv')

manhattan_plot(g, label='Genotype-level TWAS', out_file='manhattan.png')        # one set of results
miami_plot(s, g, top_label='Summary-level TWAS', bottom_label='Genotype-level TWAS',
           out_file='miami.png')                                                # two sets, mirrored
scatter_plot(s, g, x_label='Summary-level TWAS', y_label='Genotype-level TWAS',
             out_file='scatter.png')                                            # two sets, gene by gene
>>>
<p>Significant genes (Bonferroni) are colored, and the dashed lines show the significance thresholds.</p>
'''),

('acat', 'Meta-analysis TWAS with ACAT', r'''
<p><code>run_all_twas</code> runs TWAS with every model (4 methods &times; 8 brain regions = 32 model sets), then combines the p-values of each gene into one p-value with ACAT (Aggregated Cauchy Association Test):</p>
<<<Python
from agentp import run_all_twas

# summary-level TWAS
run_all_twas(project, 'putamen_volume', twas_type='stwas',
             gwas_files={'putamen_volume': 'putamen_volume_gwas.txt'})

# genotype-level TWAS (after adding the subject data)
run_all_twas(project, 'putamen_volume', twas_type='itwas')
>>>
<p>The combined results are saved to <code>my_project/sTWAS/ACAT/putamen_volume.csv</code> (or <code>iTWAS/ACAT/</code>). This table has one p-value column per model set, <code>n_models</code> (how many models tested the gene), and the combined p-value (<code>sTWAS_ACAT</code> or <code>iTWAS_ACAT</code>). Genes tested by fewer than 4 models get no combined p-value.</p>
<p>If your GWAS file is not in REGENIE format, give the column names once for all files: <code>gwas_params={'sep': '\t', 'snp_col': 'rsid', 'alt_col': 'a2', ...}</code>. To combine results that you already ran one model at a time, use <code>collect_twas(project, 'putamen_volume')</code>.</p>
'''),

('options', 'More options', r'''
<ul class="list">
  <li><strong>Run a GWAS</strong> (needs the subject data):
<<<Python
from agentp import GWAS
GWAS(project).run(['putamen_volume', 'caudate_volume'])    # saved to my_project/GWAS/
>>></li>
  <li><strong>Add other models.</strong> Models in PredictDB format (a <code>.db</code> weights file and a <code>.txt.gz</code> covariance file, e.g. other GTEx tissues) can be added and then used like the built-in ones:
<<<Python
project.add_model('PDX', 'hypothalamus', weights='en_Brain_Hypothalamus.db',
                  covariance='en_Brain_Hypothalamus.txt.gz')
stwas = SummaryTWAS(project, 'PDX', 'hypothalamus')
>>></li>
  <li><strong>Run again and replace old results:</strong> add <code>overwrite=True</code>, e.g. <code>stwas.run_twas('putamen_volume', overwrite=True)</code>. Without it, AGENT-P skips results that already exist.</li>
  <li><strong>Several traits in parallel:</strong> <code>run_twas([...], num_threads=4)</code> runs 4 traits at the same time.</li>
</ul>
'''),

('troubleshooting', 'Troubleshooting', r'''
<ul class="list">
  <li><strong>My genotypes are in VCF format.</strong> Convert them to BGEN, one file per chromosome:
<<<Terminal
for c in $(seq 1 22); do
    plink2 --vcf chr${c}.dose.vcf.gz dosage=DS --double-id --export bgen-1.2 bits=8 --out genotypes/chr${c}
done
>>>
  SNP IDs must be rsIDs. If your VCF uses other IDs (e.g. <code>chr1:12345:A:G</code>), add rsIDs first (e.g. with <code>bcftools annotate</code> and a dbSNP file).</li>
  <li><strong>Very few genes are tested.</strong> The SNP IDs in your GWAS or genotypes do not match the models: check that they are rsIDs.</li>
  <li><strong>Problems with the installation:</strong> see <a href="getting-started.html#troubleshooting">Getting started</a>.</li>
</ul>
'''),
]

## ---------------------------------------------------------------------------------------------
## Functions: the important functions, each with its input and output.
## Not on the site for now; to add the page back, add this entry to PAGES:
##     ('functions.html', 'Functions', 'Functions · AGENT-P',
##      'The important functions of AGENT-P, with their input and output.',
##      page_intro('Functions', FUNCTIONS_INTRO_TEXT),
##      FUNCTIONS, False, {}),
## ---------------------------------------------------------------------------------------------
def io(fid, title, what, inputs, output, code_lines=None):
    """one function: what it does, then its input and its output"""
    head = f'<h3 id="{fid}" class="fn">{title}</h3>'
    call = f'\n<<<Python\n{code_lines}\n>>>' if code_lines else ''
    return (f'{head}\n<p>{what}</p>{call}\n'
            f'<dl class="io">\n  <dt>Input</dt>\n  <dd>{inputs}</dd>\n  <dt>Output</dt>\n  <dd>{output}</dd>\n</dl>')

def cols(rows):
    body = '\n'.join(f'    <tr><td><code>{c}</code></td><td>{d}</td></tr>' for c, d in rows)
    return ('<div class="table-scroll"><table>\n  <thead><tr><th scope="col">Column</th><th scope="col">Meaning</th></tr></thead>\n'
            f'  <tbody>\n{body}\n  </tbody>\n</table></div>')

def c(x):
    return f'<code>{html.escape(x)}</code>'

FUNCTIONS = [
('subject-data', 'Subject data', io('fn-subject-data', 'Add the subject data',
  'Adds the data of a cohort to a project, for genotype-level TWAS and GWAS. Each of these is needed once per project.',
  r'''<div class="table-scroll"><table>
    <thead><tr><th scope="col">Function</th><th scope="col">File</th></tr></thead>
    <tbody>
      <tr><td><code>set_subjects</code></td><td>subject IDs, one per line, no header</td></tr>
      <tr><td><code>add_covariates</code></td><td>a table with an <code>id</code> column and one column per covariate (numbers only, e.g. sex as 0/1)</td></tr>
      <tr><td><code>add_phenotypes</code></td><td>a table with an <code>id</code> column and one column per trait; the column names are the trait names</td></tr>
      <tr><td><code>add_genotypes</code></td><td>a folder with one BGEN file per chromosome (1&ndash;22), each with a <code>.sample</code> file; SNP IDs as rsIDs</td></tr>
    </tbody>
  </table></div>
  Tables are tab-separated by default; for comma-separated tables, add <code>sep=','</code>.''',
  r'''copies in <code>my_project/input_data/</code>, for the subjects in the subject list. The genotypes are cleaned first: SNPs with less than 5% missing calls, a minor allele frequency of at least 1%, and a Hardy&ndash;Weinberg equilibrium p-value above 1e-5 are kept.''',
  """project = Project('my_project')
project.set_subjects('subjects.txt')
project.add_covariates('covariates.txt')
project.add_phenotypes('phenotypes.txt')
project.add_genotypes('genotypes', 'chr*.bgen')""")),

('summary', 'Summary-level TWAS', '\n\n'.join([
  io('fn-add-gwas', c('stwas.add_gwas(trait, gwas_file)'),
     "Adds the GWAS summary statistics of a trait, for <code>SummaryTWAS(project, 'JTI', 'caudate')</code>.",
     r'''a GWAS file with one row per SNP (may be gzipped). Files made with AGENT-P's <code>GWAS</code> are read as they are (comma-separated, columns <code>SNP</code>, <code>ALLELE0</code>, <code>ALLELE1</code>, <code>BETA</code>, <code>SE</code>, <code>PVAL</code>). For other files, give the column names:
  <div class="table-scroll"><table>
    <thead><tr><th scope="col">Option</th><th scope="col">Column</th></tr></thead>
    <tbody>
      <tr><td><code>sep</code></td><td>column separator, e.g. <code>'\t'</code>, <code>','</code>, or <code>' '</code></td></tr>
      <tr><td><code>snp_col</code></td><td>SNP IDs (rsIDs)</td></tr>
      <tr><td><code>alt_col</code></td><td><strong>effect allele</strong>: the allele that the beta refers to</td></tr>
      <tr><td><code>ref_col</code></td><td>the other allele</td></tr>
      <tr><td><code>beta_col</code>, <code>beta_se_col</code></td><td>effect size and its standard error</td></tr>
      <tr><td><code>pval_col</code></td><td>p-value (needed for FUSION)</td></tr>
      <tr><td><code>zscore_col</code>, <code>or_col</code></td><td>z-score or odds ratio, instead of a beta</td></tr>
    </tbody>
  </table></div>
  REGENIE's own output has no p-value column: use <code>sep=' ', snp_col='ID', alt_col='ALLELE1', ref_col='ALLELE0', beta_col='BETA', beta_se_col='SE'</code> (every method except FUSION).''',
     'nothing yet: the GWAS is used by <code>run_twas</code>.'),
  io('fn-run-stwas', c('stwas.run_twas(trait)'),
     'Runs summary-level TWAS for a trait (or a list of traits) with the model set of <code>SummaryTWAS</code>.',
     'the names of traits whose GWAS was added with <code>add_gwas</code>.',
     'one table per trait, tab-separated, one row per gene: <code>my_project/sTWAS/JTI_caudate/putamen_volume.csv</code>' + cols([
       ('gene', 'Ensembl gene ID'),
       ('gene_name', 'gene symbol (not for FUSION)'),
       ('zscore', 'direction and strength of the association: positive means that higher expression goes with a larger trait value'),
       ('pvalue', 'p-value'),
       ('effect_size', 'effect size (not for FUSION)'),
       ('n_snps_used', 'number of SNPs of the gene model found in the GWAS (not for FUSION); FUSION reports the model used in <code>best_model</code>'),
     ])),
])),

('genotype', 'Genotype-level TWAS', '\n\n'.join([
  io('fn-predict-grex', c('itwas.predict_grex()'),
     "Predicts the gene expression of every subject in the brain region of <code>IndividualTWAS(project, 'JTI', 'caudate')</code>. Needed once per method and region; the result is reused for every trait.",
     'the genotypes of the project (added with <code>add_genotypes</code>).',
     'the predicted expression of every gene for every subject: <code>my_project/GREX/JTI/caudate.hdf5</code> (HDF5 file with the gene IDs in <code>genes</code> and a genes &times; subjects matrix in <code>pred_expr</code>).'),
  io('fn-run-itwas', c('itwas.run_twas(trait)'),
     'Tests the predicted gene expression for association with a trait (or a list of traits), adjusting for the covariates.',
     'the names of traits added with <code>add_phenotypes</code>; the predicted expression from <code>predict_grex</code>; the covariates of the project.',
     'one table per trait, tab-separated, one row per gene: <code>my_project/iTWAS/JTI_caudate/putamen_volume.csv</code>' + cols([
       ('gene', 'Ensembl gene ID'),
       ('effect', 'change in the trait per unit of predicted expression'),
       ('se', 'standard error of the effect'),
       ('zscore', 'effect / standard error'),
       ('pvalue', 'p-value'),
       ('n_samples', 'number of subjects in the test'),
     ])),
])),

('meta', 'Meta-analysis TWAS', '\n\n'.join([
  io('fn-run-all-twas', c("run_all_twas(project, trait, twas_type='stwas', gwas_files={...})"),
     'Runs TWAS with every model set (4 methods &times; 8 brain regions), then combines the results of each trait with <code>collect_twas</code>.',
     "the names of the traits; <code>twas_type='stwas'</code> (summary-level, with <code>gwas_files={trait: GWAS file}</code>) or <code>'itwas'</code> (genotype-level, with the subject data in the project). <code>approaches</code> and <code>regions</code> (lists of codes) limit the model sets.",
     'the results table of every model set (as for <code>run_twas</code>), and the combined table of each trait (as for <code>collect_twas</code>).'),
  io('fn-collect-twas', c('collect_twas(project, trait)'),
     'Combines the TWAS results of a trait from all model sets that were run into one p-value per gene, with ACAT (Aggregated Cauchy Association Test).',
     "the name of a trait whose TWAS results are in the project; <code>twas_type='itwas'</code> for genotype-level TWAS.",
     'one table, comma-separated, one row per gene: <code>my_project/sTWAS/ACAT/putamen_volume.csv</code> (or <code>iTWAS/ACAT/</code>)' + cols([
       ('gene', 'Ensembl gene ID'),
       ('sTWAS_JTI_caudate, ...', 'p-value from each model set'),
       ('n_models', 'number of model sets that tested the gene'),
       ('sTWAS_ACAT', 'combined p-value (<code>iTWAS_ACAT</code> for genotype-level TWAS); only for genes tested by at least 4 model sets'),
     ])),
])),

('plots', 'Plots', '\n\n'.join([
  io('fn-load-pvalues', c('load_pvalues(results_file)'),
     'Reads the p-values of a results file, for the plots.',
     "a TWAS results table of AGENT-P. For other files, give the column names: <code>gene_col</code>, <code>pval_col</code>, and <code>sep</code> (e.g. <code>sep=','</code> for a <code>collect_twas</code> table, with <code>pval_col='sTWAS_ACAT'</code>).",
     'the p-values, indexed by gene ID.'),
  io('fn-plots', 'Manhattan, Miami, and scatter plots',
     'Plot one or two sets of results. Significant genes are colored, and dashed lines show the Bonferroni thresholds.',
     r'''p-values from <code>load_pvalues</code>:
  <div class="table-scroll"><table>
    <thead><tr><th scope="col">Function</th><th scope="col">Shows</th></tr></thead>
    <tbody>
      <tr><td><code>manhattan_plot(pvals)</code></td><td>one set of results, by gene position</td></tr>
      <tr><td><code>miami_plot(top, bottom)</code></td><td>two sets, one above and one below the axis</td></tr>
      <tr><td><code>scatter_plot(x, y)</code></td><td>two sets, gene by gene, with their correlation</td></tr>
    </tbody>
  </table></div>''',
     "an image file, given with <code>out_file</code> (e.g. <code>out_file='miami.png'</code>; also <code>.pdf</code>). Labels: <code>label</code>, <code>top_label</code> / <code>bottom_label</code>, <code>x_label</code> / <code>y_label</code>, and <code>title</code>."),
])),

('gwas', 'GWAS', io('fn-gwas', c('GWAS(project).run(trait)'),
  'Runs a GWAS with REGENIE for a trait (or a list of traits).',
  'the names of traits added with <code>add_phenotypes</code>, and the subject data of the project.',
  'one file per trait, comma-separated, one row per SNP: <code>my_project/GWAS/putamen_volume.regenie</code>, ready for <code>add_gwas</code>' + cols([
    ('CHROM, GENPOS, SNP', 'chromosome, position, and rsID'),
    ('ALLELE0, ALLELE1', 'the two alleles; ALLELE1 is the effect allele'),
    ('A1FREQ', 'frequency of ALLELE1'),
    ('BETA, SE', 'effect of each copy of ALLELE1, and its standard error'),
    ('PVAL, LOG10P', 'p-value, and &minus;log10 of it'),
  ]))),
]

FUNCTIONS_INTRO_TEXT = ('The important functions of AGENT-P, with what each one needs and what it makes. For complete examples, see <a href="full-run.html">Full run</a>. '
    'In every TWAS and GWAS function, <code>overwrite=True</code> runs again and replaces existing results, which are otherwise skipped.')

## ---------------------------------------------------------------------------------------------
## Classes: what each class needs, what it does, and what it makes.
## Not on the site for now; to add the page back, add this entry to PAGES:
##     ('classes.html', 'Classes', 'Classes · AGENT-P',
##      'The classes of AGENT-P: what each one needs, what it does, and what it makes.',
##      page_intro('Classes', CLASSES_INTRO_TEXT),
##      CLASSES, False, {}),
## ---------------------------------------------------------------------------------------------
def klass(create, inputs, does, outputs, intro=''):
    """one class: how it is created, then its input, what it does, and its output"""
    call = f'<<<Python\n{create}\n>>>\n' if create else ''
    lead = f'<p>{intro}</p>\n' if intro else ''
    return (f'{lead}{call}<dl class="io">\n'
            f'  <dt>Input</dt>\n  <dd>{inputs}</dd>\n'
            f'  <dt>What it does</dt>\n  <dd>{does}</dd>\n'
            f'  <dt>Output</dt>\n  <dd>{outputs}</dd>\n</dl>')

CLASSES = [
('class-project', 'Project', klass(
  """project = Project('my_project')
project.set_subjects('subjects.txt')
project.add_covariates('covariates.txt')
project.add_phenotypes('phenotypes.txt')
project.add_genotypes('genotypes', 'chr*.bgen')""",
  r'''a folder name, then the data of one cohort:
  <ul class="list">
    <li>subject IDs, one per line (<code>set_subjects</code>)</li>
    <li>covariates, e.g. age, sex, and genetic principal components (<code>add_covariates</code>)</li>
    <li>traits (<code>add_phenotypes</code>)</li>
    <li>genotypes: one BGEN file per chromosome (1&ndash;22) with rsIDs (<code>add_genotypes</code>)</li>
    <li>optionally, other expression models in PredictDB format (<code>add_model</code>)</li>
  </ul>
  The subject data are needed for genotype-level TWAS and GWAS, not for summary-level TWAS.''',
  r'''creates the project folder and keeps the data of the listed subjects. The genotypes are cleaned with <a href="#class-bgen"><code>BGEN</code></a>.''',
  r'''the project folder, which holds the inputs and every result:
  <div class="table-scroll"><table>
    <thead><tr><th scope="col">Folder</th><th scope="col">Contents</th></tr></thead>
    <tbody>
      <tr><td><code>input_data/</code></td><td>subject IDs, covariates, traits, and cleaned genotypes</td></tr>
      <tr><td><code>sTWAS/</code>, <code>iTWAS/</code></td><td>results of summary-level and genotype-level TWAS</td></tr>
      <tr><td><code>GREX/</code></td><td>predicted gene expression</td></tr>
      <tr><td><code>GWAS/</code></td><td>GWAS results</td></tr>
    </tbody>
  </table></div>''',
  'A project keeps the inputs and results of one cohort together. Every analysis starts with one.')),

('class-summarytwas', 'SummaryTWAS', klass(
  """stwas = SummaryTWAS(project, 'JTI', 'caudate')
stwas.add_gwas('putamen_volume', 'putamen_volume_gwas.txt')
stwas.run_twas('putamen_volume')""",
  r'''a project, a model set (method and brain region, see <a href="getting-started.html#models">model codes</a>), and the GWAS summary statistics of one or more traits (<code>add_gwas</code>). The GWAS file needs the SNP ID (rsID), both alleles, and the effect size with its standard error or a p-value; see <a href="full-run.html#summary">Full run</a> for the column names.''',
  r'''matches the GWAS SNPs to the SNPs of each gene model by rsID, and combines the GWAS effects with the model weights and the correlations between the SNPs, to test each gene for association with the trait (<code>run_twas</code>). PrediXcan, UTMOST, and JTI models are applied with S-PrediXcan, and FUSION models with FUSION.''',
  r'''one table per trait, one row per gene: <code>my_project/sTWAS/JTI_caudate/putamen_volume.csv</code>, with the gene ID (<code>gene</code>), the direction and strength of the association (<code>zscore</code>), and the <code>pvalue</code>.''',
  'TWAS from GWAS summary statistics: no individual-level data are needed.')),

('class-individualtwas', 'IndividualTWAS', klass(
  """itwas = IndividualTWAS(project, 'JTI', 'caudate')
itwas.predict_grex()
itwas.run_twas('putamen_volume')""",
  r'''a project with the subject data (subjects, covariates, traits, and genotypes), and a model set (method and brain region).''',
  r'''<ol class="list">
    <li><code>predict_grex</code>: predicts the gene expression of every subject in the brain region from their genotypes, with <a href="#class-grex"><code>GREX</code></a>. Needed once per model set; the result is reused for every trait.</li>
    <li><code>run_twas</code>: tests the predicted expression of each gene for association with a trait, with a linear regression that adjusts for the covariates.</li>
  </ol>''',
  r'''<ul class="list">
    <li>predicted expression (genes &times; subjects): <code>my_project/GREX/JTI/caudate.hdf5</code></li>
    <li>one table per trait, one row per gene: <code>my_project/iTWAS/JTI_caudate/putamen_volume.csv</code>, with <code>gene</code>, <code>effect</code> (change in the trait per unit of predicted expression), <code>se</code>, <code>zscore</code>, <code>pvalue</code>, and <code>n_samples</code></li>
  </ul>''',
  'TWAS from individual-level data: genotypes, covariates, and traits of each subject.')),

('class-gwas', 'GWAS', klass(
  """gwas = GWAS(project)
gwas.run(['putamen_volume', 'caudate_volume'])""",
  r'''a project with the subject data, and the names of one or more traits.''',
  r'''runs a GWAS with <a href="https://rgcgithub.github.io/regenie">REGENIE</a> (steps 1 and 2, one chromosome at a time), adjusting for the covariates, then combines the chromosomes into one file per trait and adds a p-value column.''',
  r'''one file per trait, one row per SNP: <code>my_project/GWAS/putamen_volume.regenie</code> (comma-separated, with <code>SNP</code>, <code>ALLELE0</code>, <code>ALLELE1</code> as the effect allele, <code>BETA</code>, <code>SE</code>, and <code>PVAL</code>). It can be used directly in <code>SummaryTWAS.add_gwas</code>.''',
  'Genome-wide association study, for example to make the GWAS for a summary-level TWAS.')),

('class-bgen', 'BGEN', klass(
  '',
  r'''the BGEN files of the cohort (one per chromosome, with <code>.sample</code> files) and the subject list, from <code>Project.add_genotypes</code>.''',
  r'''cleans the genotypes with PLINK 2: keeps the listed subjects and single-nucleotide variants, sets genotypes with a probability below 0.9 to missing, and keeps SNPs with less than 5% missing calls, a minor allele frequency of at least 1%, no duplicate IDs, and a Hardy&ndash;Weinberg equilibrium p-value above 1e-5.''',
  r'''cleaned genotypes, one BGEN file per chromosome: <code>my_project/input_data/genotypes/</code>.''',
  'Used inside <code>Project.add_genotypes</code>; you do not create it yourself.')),

('class-grex', 'GREX', klass(
  '',
  r'''the cleaned genotypes of the project and the weights of one model set, from <code>IndividualTWAS.predict_grex</code>.''',
  r'''keeps the SNPs of the gene models, then predicts the expression of each gene for each subject as a weighted sum of their genotypes: with PrediXcan for PrediXcan, UTMOST, and JTI models, and with PLINK 2 gene scores for FUSION models.''',
  r'''predicted expression (genes &times; subjects): <code>my_project/GREX/JTI/caudate.hdf5</code>.''',
  'Used inside <code>IndividualTWAS.predict_grex</code>; you do not create it yourself.')),
]

CLASSES_INTRO_TEXT = ('The classes of AGENT-P, each with what it needs, what it does, and what it makes. '
    'Combining models with ACAT (<code>run_all_twas</code>, <code>collect_twas</code>) is described in <a href="full-run.html">Full run</a>.')

## ---------------------------------------------------------------------------------------------
## Home
## ---------------------------------------------------------------------------------------------
HOME = [
('try', 'Try it online', r'''
<p>The example notebook runs in Google Colab, with nothing to install. It runs summary-level and genotype-level TWAS on 2,000 example subjects with the JTI caudate models and amygdala volume, then shows the top genes and Manhattan and Miami plots.</p>
<p><a href="%COLAB%">Open the example in Colab</a>, then choose <strong>Runtime &rarr; Run all</strong>. The <a href="example.html">Example</a> page explains each step.</p>
'''),

('cite', 'Citation', r'''
<!-- TODO: add the journal, year and DOI once the paper is published. -->
<p class="citation">Tang K.*, Hoang N.*, Sardaripour N., Capra T., Rubinov M. <em>Associations of estimated gene expression with neuroimaging phenotypes across people and brain regions with AGENT-P.</em> Manuscript in preparation.</p>
<p class="note">* Equal contribution.</p>
<h3 id="contact">Contact</h3>
<div class="contact"><a href="mailto:mika.rubinov@vanderbilt.edu">Mikail Rubinov</a><a href="mailto:keyi.tang@vanderbilt.edu">Keyi Tang</a><a href="mailto:nhung.t.hoang@outlook.com">Nhung Hoang</a></div>
<p class="note">For bug reports and usage questions, <a href="%REPO%/issues">open an issue on GitHub</a>.</p>
'''),
]

HOME_INTRO = r'''
<div class="intro" id="overview">
  <h1>AGENT-P</h1>
  <p class="full-name">Association of Gene Expression to Neuroimaging Traits Pipeline</p>
  <p>A Python package for transcriptome-wide association studies (TWAS) of brain traits. AGENT-P predicts how much each gene is expressed in the brain from a person's genotypes (genetically regulated gene expression, or GREx), and tests whether this predicted expression is associated with a trait, such as the volume of a brain region.</p>
  <p>It includes ready-to-use expression models from four TWAS methods in eight brain regions, and runs TWAS in two ways:</p>
  <div class="table-scroll"><table>
    <thead><tr><th scope="col">TWAS</th><th scope="col">Input</th><th scope="col">AGENT-P class</th></tr></thead>
    <tbody>
      <tr><td>Summary-level</td><td>GWAS summary statistics of the trait</td><td><code>SummaryTWAS</code></td></tr>
      <tr><td>Genotype-level</td><td>genotypes, covariates, and trait values of individual subjects</td><td><code>IndividualTWAS</code></td></tr>
    </tbody>
  </table></div>
  <p>AGENT-P can also separately run a GWAS with REGENIE, combine the results of all models into one p-value per gene as meta-analysis TWAS (ACAT), and make Manhattan and Miami plots.</p>
  <p class="buttons" aria-label="Project resources">
    <a class="button" href="%COLAB%">Google Colab</a>
    <a class="button" href="https://pypi.org/project/agentp/">PyPI</a>
    <a class="button" href="%MODELS%">Models (2 GB)</a>
    <a class="button dark" href="%REPO%/tree/%BRANCH%">GitHub</a>
  </p>
  <span id="install"></span><span id="quickstart"></span><span id="models"></span><span id="api"></span>
</div>
'''

def page_intro(title, text):
    return f'<div class="page-intro">\n  <h1>{title}</h1>\n  <p>{text}</p>\n</div>'

## (file, sidebar label, <title>, description, intro, sections, numbered sections, legacy anchors)
PAGES = [
    ('index.html', 'Home', 'AGENT-P',
     'AGENT-P: the Association of Gene Expression to Neuroimaging Traits Pipeline. A Python package for transcriptome-wide association studies (TWAS) of brain traits.',
     HOME_INTRO, HOME, False, {}),
    ('getting-started.html', 'Getting started', 'Getting started · AGENT-P',
     'Requirements, installation, and the expression models of AGENT-P.',
     page_intro('Getting started', 'What AGENT-P needs, how to install it, and how to download the expression models.'),
     GETTING_STARTED, True, {}),
    ('example.html', 'Example', 'Example · AGENT-P',
     'Run the AGENT-P example in Google Colab or on your computer.',
     page_intro('Example', 'Try AGENT-P on example data in Google Colab, without installing anything, or run the same example on your computer.'),
     EXAMPLE, True, {'colab': ['quickstart']}),
    ('full-run.html', 'Full run', 'Full run · AGENT-P',
     'Run TWAS on your own data with AGENT-P: summary-level and genotype-level TWAS, results, plots, and meta-analysis TWAS with ACAT.',
     page_intro('Full run', 'Run TWAS on your own data: the input data you need, summary-level and genotype-level TWAS, results and plots, and meta-analysis TWAS with ACAT.'),
     FULL_RUN, True, {'project': ['api']}),
]


ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%23245b85'/%3E"
        "%3Ctext x='16' y='22' font-family='Arial,sans-serif' font-size='15' font-weight='700' fill='white' text-anchor='middle'%3EAP%3C/text%3E%3C/svg%3E")


def sidebar(current):
    items = []
    for fname, label, _, _, _, sections, numbered, _ in PAGES:
        here = fname == current
        link = f'<a href="{fname}"' + (' aria-current="page"' if here else '') + f'>{label}</a>'
        sub = ''
        if here:   ## the sections of the current page
            subs = '\n'.join(f'          <li><a href="#{sid}">{title}</a></li>' for sid, title, _ in sections)
            tag = 'ol' if numbered else 'ul'
            sub = f'\n        <{tag} class="sub">\n{subs}\n        </{tag}>\n      '
        items.append(f'      <li>{link}{sub}</li>')
    return f"""  <aside class="sidebar">
    <a class="brand" href="index.html">AGENT-P</a>
    <nav aria-label="Site">
      <ul class="pages">
{chr(10).join(items)}
      </ul>
    </nav>
    <ul class="ext" aria-label="Project resources">
      <li><a href="%COLAB%">Try it in Colab</a></li>
      <li><a href="%REPO%/tree/%BRANCH%">GitHub</a></li>
      <li><a href="https://pypi.org/project/agentp/">PyPI</a></li>
      <li><a href="%MODELS%">Models (2 GB)</a></li>
    </ul>
  </aside>"""


for fname, label, title, desc, intro, sections, numbered, legacy in PAGES:
    body = '\n\n'.join(
        f'    <section id="{sid}" aria-labelledby="{sid}-title">\n'
        + ''.join(f'      <span id="{a}"></span>\n' for a in legacy.get(sid, []))
        + f'      <h2 id="{sid}-title">' + (f'<span class="num">{k}.</span>' if numbered else '') + f'{stitle}</h2>\n'
        + render(sbody.strip()) + '\n    </section>'
        for k, (sid, stitle, sbody) in enumerate(sections, 1))
    has_code = 'class="code"' in body
    canonical = 'https://agentp.rubinovlab.net/' + ('' if fname == 'index.html' else fname)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<link rel="icon" href="{ICON}">
<link rel="stylesheet" href="style.css">
</head>
<body>

<a class="skip" href="#main">Skip to content</a>
<div class="layout" id="top">
{render(sidebar(fname))}
  <div class="content">
  <main id="main">
{render(intro.strip())}

{body}
""" + ("""
    <div class="status" role="status" aria-live="polite" id="copy-status"></div>""" if has_code else "") + f"""
  </main>
  <footer><a href="https://rubinovlab.net">Rubinov Lab</a>, Vanderbilt University · <a href="{REPO}/blob/main/LICENSE">MIT License</a></footer>
  </div>
</div>
<script src="site.js"></script>
</body>
</html>
"""
    with open(fname, 'w') as f:
        f.write(page)
    print('wrote', fname)


## previews: copies with style.css and site.js inlined, so that a single file shows the full design
## (e.g. in an app preview). Not needed on the server.
import os
os.makedirs('preview', exist_ok=True)
css, js = open('style.css').read(), open('site.js').read()
for fname, *_ in PAGES:
    s = open(fname).read()
    s = s.replace('<link rel="stylesheet" href="style.css">', '<style>\n' + css + '\n</style>')
    s = s.replace('<script src="site.js"></script>', '<script>\n' + js + '\n</script>')
    for other, *_ in PAGES:
        s = s.replace(f'href="{other}', f'href="preview_{other}')
    with open(f'preview/preview_{fname}', 'w') as f:
        f.write(s)
print('wrote previews in preview/')
