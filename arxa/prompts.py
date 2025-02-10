# arxa/arxa/prompts.py

PROMPT_PREFIX = """\
You are a research assistant tasked with generating comprehensive research notes...
<pdf_content>
"""

PROMPT_SUFFIX = """\
{paper_info}
</paper_info>
...
Always extract the authors github url if they are releasing code.

Use the following template:

Paper Information Section:
Look for the title at the top of the paper, typically in large or bold font. Collect author names from the byline, typically listed below the title. The arXiv link will be in the paper's metadata or header. Find the submission date in the paper metadata or footer. The field of study is often mentioned in keywords, abstract, or introduction. Keywords are typically listed explicitly after the abstract. Look for code repository links in footnotes, acknowledgments, or implementation sections.
Summary Section:
The problem statement is typically found in the introduction, often within the first few paragraphs. Main contributions are usually explicitly stated in the introduction, often as bullet points or numbered lists. Key findings appear in the abstract and conclusion sections. The methodology overview is typically summarized in the abstract and detailed in the introduction. The conclusion is found in the final section of the paper.
Background and Related Work Section:
Prior work is typically discussed in a dedicated "Related Work" or "Background" section. Look for explicit comparisons or statements about how the current work differs from previous approaches. Gaps addressed are usually stated in the introduction or related work section, often prefaced with phrases like "however" or "nevertheless."
Methodology Section:
The approach is detailed in the methods or methodology section. Key techniques are described in the methodology section, often with mathematical notations or algorithms. Dataset information is typically in a dedicated "Experiments" or "Evaluation" section. Implementation details are found in the methodology or experiments section. Reproducibility information is often in implementation details or supplementary materials.
Experimental Evaluation Section:
Evaluation metrics are defined in the experiments section. Results summary appears in results/evaluation section, often with tables and figures. Baseline comparisons are in the results section, usually in tables. Ablation studies have their own subsection in results. Limitations are typically discussed near the end of results or in discussion.
Strengths Section:
Look for novel contributions highlighted in introduction and conclusion. Technical soundness is assessed through methodology and evaluation sections. Clarity is evaluated through overall paper structure. Impact and applications are typically discussed in introduction and conclusion.
Weaknesses and Critiques Section:
Look for assumptions stated in methodology section. Limitations are typically acknowledged in discussion or limitations section. Reproducibility concerns can be assessed from methodology and implementation details. Presentation issues relate to overall paper organization and clarity.
Future Work Section:
Future work is typically discussed in conclusion or in a dedicated section. Look for phrases like "in future work" or "could be extended." Open problems are often mentioned in discussion or conclusion.
Personal Review Section:
This requires synthesizing information from the entire paper to assess overall quality, significance, clarity, methodology, and reproducibility.
Additional Notes Section:
Key takeaways are main points emphasized throughout the paper. Interesting insights might be novel findings or unexpected results. Personal thoughts should be based on critical analysis of the paper's strengths and weaknesses.
Focus on these key phrases and sections to extract relevant information efficiently. Pay special attention to the abstract, introduction, and conclusion as they often contain condensed versions of key information.
"""
