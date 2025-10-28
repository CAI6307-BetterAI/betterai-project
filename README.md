# betterai-project

## Prerequisites

- UV: <https://docs.astral.sh/uv/getting-started/installation/>

## Setup

1. Sync submodules

   ```sh
   git submodule update --init --remote
   ```

2. Install dependencies

   ```sh
   uv sync
   ```

## Helpful Commands

Installing new dependencies (ex: requests)

```sh
uv add requests
```

Run main.py

```sh
uv run main.py
```

## Datasets Used

Below are the datasets used for evaluation and benchmarking hallucination reduction in RDF-grounded LMs.

**PubMedDQ** - [Link](https://drive.google.com/drive/folders/1rOM_Y0FbmqsuJqjqcu7bntM1cB9QoKRn?usp=sharing)



---

### Notes

- `pubmedqa.jsonl` → Main evaluation benchmark (factual accuracy, hallucination rate). - Biomedical yes/no QA dataset with verified human labels (1k samples). 
- `pubmedqa_artificial.jsonl` → Optional training/calibration dataset. - Automatically labeled synthetic QA pairs (211k). Used for model calibration or pre-training.
- `pubmedqa_unlabeled.jsonl` → Retrieval stress-testing for RDF graph coverage. - Questions and contexts without gold labels (61k). Used for retrieval evaluation. 
- `medqa.jsonl` → Complex reasoning benchmark (clinical multi-choice).  
- `medhalt.jsonl` → Hallucination stress test for medical text generation.

---

