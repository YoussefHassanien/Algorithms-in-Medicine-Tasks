import gradio as gr
import numpy as np

# Divide and Conquer algorithm for sequence alignment
def divide_and_conquer_alignment(seq1, seq2, gap_penalty=-1, match_score=1, mismatch_penalty=-1):
    def align(s1, s2):
        if len(s1) == 0:
            return '-' * len(s2), s2
        elif len(s2) == 0:
            return s1, '-' * len(s1)
        elif len(s1) == 1 or len(s2) == 1:
            return simple_alignment(s1, s2, gap_penalty, match_score, mismatch_penalty)
        else:
            mid1 = len(s1) // 2
            score_l = nw_score(s1[:mid1], s2)
            score_r = nw_score(s1[mid1:][::-1], s2[::-1])[::-1]
            partition = np.argmax(score_l + score_r)
            left_s1, left_s2 = align(s1[:mid1], s2[:partition])
            right_s1, right_s2 = align(s1[mid1:], s2[partition:])
            return left_s1 + right_s1, left_s2 + right_s2

    def nw_score(s1, s2):
        m, n = len(s1), len(s2)
        dp = np.zeros((2, n + 1))
        for j in range(n + 1):
            dp[0][j] = j * gap_penalty
        for i in range(1, m + 1):
            dp[1][0] = i * gap_penalty
            for j in range(1, n + 1):
                match = dp[0][j - 1] + (match_score if s1[i - 1] == s2[j - 1] else mismatch_penalty)
                delete = dp[0][j] + gap_penalty
                insert = dp[1][j - 1] + gap_penalty
                dp[1][j] = max(match, delete, insert)
            dp[0] = dp[1].copy()
        return dp[1]

    def simple_alignment(s1, s2, gap_penalty, match_score, mismatch_penalty):
        m, n = len(s1), len(s2)
        dp = np.zeros((m + 1, n + 1))
        for i in range(m + 1):
            dp[i][0] = i * gap_penalty
        for j in range(n + 1):
            dp[0][j] = j * gap_penalty
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                match = dp[i - 1][j - 1] + (match_score if s1[i - 1] == s2[j - 1] else mismatch_penalty)
                delete = dp[i - 1][j] + gap_penalty
                insert = dp[i][j - 1] + gap_penalty
                dp[i][j] = max(match, delete, insert)
        aligned_s1, aligned_s2 = [], []
        i, j = m, n
        while i > 0 or j > 0:
            current_score = dp[i][j]
            if i > 0 and dp[i - 1][j] + gap_penalty == current_score:
                aligned_s1.append(s1[i - 1])
                aligned_s2.append('-')
                i -= 1
            elif j > 0 and dp[i][j - 1] + gap_penalty == current_score:
                aligned_s1.append('-')
                aligned_s2.append(s2[j - 1])
                j -= 1
            else:
                aligned_s1.append(s1[i - 1])
                aligned_s2.append(s2[j - 1])
                i -= 1
                j -= 1
        return ''.join(aligned_s1[::-1]), ''.join(aligned_s2[::-1])

    aligned_seq1, aligned_seq2 = align(seq1, seq2)
    return aligned_seq1, aligned_seq2

# Function to calculate similarity and variation percentages
def calculate_similarity(aligned_seq1, aligned_seq2):
    matches = sum(1 for a, b in zip(aligned_seq1, aligned_seq2) if a == b and a != '-')
    mismatches = sum(1 for a, b in zip(aligned_seq1, aligned_seq2) if a != b and a != '-' and b != '-')
    gaps = sum(1 for a, b in zip(aligned_seq1, aligned_seq2) if a == '-' or b == '-')
    
    total_length = len(aligned_seq1)
    similarity_percentage = (matches / total_length) * 100
    variation_percentage = ((mismatches + gaps) / total_length) * 100
    
    return similarity_percentage, variation_percentage

# Main function for alignment
def align_sequences(seq1, seq2):
    aligned_seq1, aligned_seq2 = divide_and_conquer_alignment(seq1, seq2)
    similarity, variation = calculate_similarity(aligned_seq1, aligned_seq2)
    
    # Prepare data for DataFrame output
    data = [
        ["Aligned Sequence 1", aligned_seq1],
        ["Aligned Sequence 2", aligned_seq2],
        ["Similarity (%)", f"{similarity:.2f}"],
        ["Variation (%)", f"{variation:.2f}"]
    ]
    return data

# Create the Gradio interface
with gr.Blocks(css=".gradio-container { font-family: 'Arial'; color: #333; }") as interface:
    gr.Markdown(
        """
        # 🔬 **Genomic Sequence Alignment Tool**
        Compare and align two genomic sequences to identify similarities and variations.  
        This tool uses a divide and conquer algorithm to compute optimal alignments.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            seq1_input = gr.Textbox(
                label="Input Sequence 1",
                placeholder="Enter the first genomic sequence...",
                lines=5,
            )
            seq2_input = gr.Textbox(
                label="Input Sequence 2",
                placeholder="Enter the second genomic sequence...",
                lines=5,
            )
            align_button = gr.Button("Align Sequences", variant="primary")

        with gr.Column(scale=1):
            output = gr.Dataframe(
                headers=["Metric", "Value"],
                datatype=["str", "str"],
                label="Results",
                interactive=False,
            )

    # Bind the button to the function
    align_button.click(
        fn=align_sequences,
        inputs=[seq1_input, seq2_input],
        outputs=output,
    )

    gr.Examples(
        examples=[
            ["ACGTAG", "ACCTAG"],
            ["AGTACGCA", "TATGC"],
            ["GATTACA", "GCATGCU"],
            ["AGCT", "AGCT"]
        ],
        inputs=[seq1_input, seq2_input],
        label="Example Sequences",
    )

# Launch the app
if __name__ == "__main__":
    interface.launch()