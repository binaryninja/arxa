# arxa/arxa/prompts.py

PROMPT_PREFIX = """\
You are a research assistant tasked with generating comprehensive research notes...
<pdf_content>
"""

PROMPT_SUFFIX = """\
{paper_info}
</paper_info>
...
Begin your response with <research_notes> and end with </research_notes>.

Always extract the authors github url if they are releasing code.

Use the following template:

## 1. Paper Information
- **Title:**
- **Authors:**
- **ArXiv Link:**
- **Date of Submission:**
- **Field of Study:**
- **Keywords:**
- **Code Repository:**

## 2. Summary
- **Problem Statement:**
- **Main Contributions:**
- **Key Findings:**
- **Methodology Overview:**
- **Conclusion:**

## 3. Background & Related Work
- **Prior Work Referenced:**
- **How It Differs from Existing Research:**
- **Gaps It Addresses:**

## 4. Methodology
- **Approach Taken:**
- **Key Techniques Used:**
- **Datasets / Benchmarks Used:**
- **Implementation Details:**
- **Reproducibility:** (Is there a code repository? Are experiments well-documented?)

## 5. Experimental Evaluation
- **Evaluation Metrics:**
- **Results Summary:**
- **Baseline Comparisons:**
- **Ablation Studies:**
- **Limitations Noted by Authors:**

## 6. Strengths
- **Novelty & Innovation:**
- **Technical Soundness:**
- **Clarity & Organization:**
- **Impact & Potential Applications:**

## 7. Weaknesses & Critiques
- **Unaddressed Assumptions / Flaws:**
- **Possible Biases or Limitations:**
- **Reproducibility Concerns:**
- **Presentation Issues:**

## 8. Future Work & Open Questions
- **Suggested Improvements by Authors:**
- **Potential Extensions / Further Research Directions:**
- **Open Problems in the Field:**

## 9. Personal Review & Rating
- **Overall Impression:** (1-5)
- **Significance of Contributions:** (1-5)
- **Clarity & Organization:** (1-5)
- **Methodological Rigor:** (1-5)
- **Reproducibility:** (1-5)

## 10. Additional Notes
- **Key Takeaways:**
- **Interesting Insights:**
- **Personal Thoughts & Comments:**
"""
