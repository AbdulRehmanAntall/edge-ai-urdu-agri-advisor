# Edge AI for Agriculture: A Lightweight Voice-Interactive Agriculture Advisory System

This repository contains the research code, data and evaluation material for an offline agricultural advisory system for Pakistani farmers. A farmer asks a question in spoken Urdu and hears the answer in Urdu. Speech recognition, answer generation and speech synthesis all run on a low-end Android smartphone, so the system needs no internet connection and costs the farmer nothing in data charges.

The project is a Faculty Research Support Program project in the Department of AI & Data Science, FAST School of Computing, National University of Computer and Emerging Sciences (FAST-NUCES), Lahore.

> **Status:** Early development (Q1 to Q2). Code, data and results will be added as the milestones below are completed.

---

## Contents

- [Motivation](#motivation)
- [Research objectives](#research-objectives)
- [System overview](#system-overview)
- [Baseline model benchmark](#baseline-model-benchmark)
- [Evaluation](#evaluation)
- [Project timeline](#project-timeline)
- [Related work](#related-work)
- [Data and ethics](#data-and-ethics)
- [Team](#team)
- [Citation](#citation)
- [License](#license)

---

## Motivation

Agriculture accounts for roughly 23% of Pakistan's GDP and employs a large share of the rural population. Many farmers have limited literacy and unreliable internet access, and they often lack timely, locally relevant advice on sowing, fertiliser, irrigation and pest control.

Existing digital services do not fully address these constraints. Telenor Pakistan's Urdu voice bot, Kissan Dost Bashir, shows that voice-based advisory services meet a real demand, but it depends on a mobile network connection. General-purpose large language models such as ChatGPT and Claude run in the cloud, are unavailable offline, and have been found unreliable for region-specific farming decisions (Woodard, 2023). No existing system offers fully offline, Urdu, voice-based agricultural advice that runs on an inexpensive phone. This project aims to fill that gap.

## Research objectives

1. **Offline language model.** Develop a compact transformer-based language model (on the order of 100M to 500M parameters) that answers crop and livestock questions in Urdu without network access. Support for regional languages is an optional extension.
2. **On-device speech interface.** Integrate an offline speech-to-text engine and an Urdu text-to-speech module so that farmers can interact with the system entirely by voice.
3. **Model compression.** Reduce model size and inference cost through knowledge distillation, pruning and 8-bit integer quantization, so that the model fits within the memory of a low-end smartphone and, where available, uses the device's neural processing unit.
4. **Localized knowledge base.** Build a curated corpus of Pakistani agricultural information covering crop management, livestock care, pest control, weather guidance and market information, validated by domain experts.
5. **Evaluation in the field.** Deploy a working prototype in rural districts and evaluate it with farmers on answer accuracy, latency and user satisfaction.
6. **Dissemination.** Report the model design, compression approach and field evaluation in peer-reviewed journal and conference publications.

## System overview

The system is a pipeline of three on-device components. Each stage runs locally on the phone; no stage calls a remote server.

```
 Spoken Urdu question
          |
          v
 +-----------------------+
 |  Offline ASR          |   Urdu speech  ->  Urdu text
 |  (Whisper / VOSK)     |
 +-----------------------+
          |
          v
 +-----------------------+
 |  Compressed SLM       |   Urdu question  ->  Urdu answer
 |  (llama.cpp, int8)    |   grounded in the agricultural knowledge base
 +-----------------------+
          |
          v
 +-----------------------+
 |  Offline Urdu TTS     |   Urdu text  ->  Urdu speech
 +-----------------------+
          |
          v
 Spoken Urdu answer
```

| Component | Role | Candidate approaches |
|---|---|---|
| Speech recognition | Transcribe spoken Urdu queries | Lightweight Whisper models (Tiny, Base, Small); VOSK / Kaldi models |
| Language model | Generate the answer | Small open models with Urdu coverage, fine-tuned on agricultural Q&A and compressed for mobile inference |
| Compression | Fit the model on low-end devices | Knowledge distillation (e.g., MiniLLM), pruning, 8-bit quantization (e.g., MobileQuant) |
| Knowledge base | Ground answers in local practice | Expert-validated Urdu Q&A on Pakistani crops, livestock, pests, weather and markets |
| Speech synthesis | Speak the answer back | Offline Urdu TTS models |
| Application | User interface | Minimal Android app with voice-first interaction |

## Baseline model benchmark

The first experiment compares small open language models that support Urdu on a set of 50 common farmer questions about wheat and cotton, written in Urdu. The questions cover four topics: sowing, fertiliser, irrigation and pest management. This question set also seeds the knowledge base and serves as an initial test set.

**Candidate models**

| Model | Parameters | Licence | Urdu coverage |
|---|---|---|---|
| Qwen2.5-0.5B-Instruct | 0.5B | To be recorded | To be recorded |
| Qwen2.5-1.5B-Instruct | 1.5B | To be recorded | To be recorded |
| Llama 3.2 1B Instruct | 1B | To be recorded | To be recorded |
| Gemma 3 1B | 1B | To be recorded | To be recorded |

The licence and language coverage of each model are taken from its official model card and added once verified.

**Protocol**

Each model is run in quantized form with llama.cpp on the same hardware and with the same prompt and decoding settings. For every model, the following are recorded:

- **Answer quality:** agronomic correctness and relevance of each answer, rated against a reference answer
- **Urdu fluency:** grammaticality, script correctness and naturalness of the Urdu output
- **Memory use:** peak resident memory during inference
- **Response time:** time to first token and total generation time per answer

The best-performing quantized model is used for the first prototype demonstration.

## Evaluation

The system is evaluated at two levels.

**Laboratory evaluation**
- Inference latency of under 500 ms on target devices for the 8-bit quantized model
- Retention of about 95% of the full-precision model's accuracy after compression
- Speech recognition word error rate (WER) and character error rate (CER) on Urdu test audio

**Field evaluation**
- Answer accuracy on real farmer queries collected during pilot testing
- End-to-end response latency on farmers' devices
- User satisfaction and comprehension, together with qualitative feedback on usability

## Project timeline

| Phase | Period | Main work |
|---|---|---|
| Q1 | Aug to Oct 2026 | Literature review; collection of Urdu agronomic Q&A; development environment; selection of baseline models |
| Q2 | Nov 2026 to Jan 2027 | First prototype; distillation, pruning and integer quantization; integration of offline speech-to-text and text-to-speech; laboratory evaluation |
| Q3 | Feb to Apr 2027 | Field deployment and pilot testing; collection of real farmer queries and feedback; iterative refinement; drafting of research papers |
| Q4 | May to Jul 2027 | System finalization; larger demonstration for farmers; impact analysis; final report and publications |

## Related work

The project builds on the following works.

- **Agricultural advisory systems.** Telenor Pakistan's Kissan Dost Bashir voice service; Ali et al. (2026), *Kissan-Dost: Bridging the Last Mile in Smallholder Precision Agriculture with Conversational IoT*; Singh et al. (2024), *Farmer.Chat: Scaling AI-Powered Agricultural Services for Smallholder Farmers*; Woodard (2023), *ChatGPT vs. Claude as Generative AI Agricultural Extension Agents in Pakistan*.
- **Small domain models.** KissanAI, *Dhenu2-In-Llama3.2-1B-Instruct* (2024).
- **Compression for on-device inference.** Tan et al., *MobileQuant: Mobile-friendly Quantization for On-device Language Models*, Findings of EMNLP 2024; Gu et al., *MiniLLM: Knowledge Distillation of Large Language Models*, ICLR 2024.
- **Offline Urdu speech recognition.** Antall and Akhtar (2025), *Assessing the Feasibility of Lightweight Whisper Models for Low-Resource Urdu Transcription*; the VOSK offline speech recognition toolkit, built on Kaldi (Povey et al., IEEE ASRU 2011).

## Data and ethics

- Agricultural content in the knowledge base is reviewed by domain experts before it is used for training or evaluation.
- Field trials collect farmer queries and feedback only with informed consent. Audio recordings and any personally identifying information are stored securely, are not committed to this repository, and are anonymized before analysis.
- The system provides general agricultural guidance. It does not replace advice from agricultural extension officers, particularly for decisions on pesticide use and dosage.

## Team

- **Principal investigator:** Dr. Maryam Bashir, Professor, Department of AI & Data Science, FAST-NUCES Lahore
- **Research team:** Abdul Rehman Antall

## Citation

A citation entry will be added once the first paper from this project is published. Until then, please cite this repository as:

```bibtex
@misc{edge_ai_urdu_agri_advisor,
  title        = {Edge AI for Agriculture: A Lightweight Voice-Interactive Agriculture Advisory System},
  author       = {Bashir, Maryam and Antall, Abdul Rehman},
  year         = {2026},
  institution  = {National University of Computer and Emerging Sciences (FAST-NUCES), Lahore},
  howpublished = {\url{https://github.com/<organization-or-user>/edge-ai-urdu-agri-advisor}}
}
```

## License

The licence for this repository has not yet been decided. Until a licence is added, all rights are reserved by the project team. Third-party models, toolkits and datasets used in this project remain subject to their own licences.
