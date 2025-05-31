# 🧑‍🏫 RAG Tutor API — Retrieval-Augmented Generation Chatbot

Welcome to your advanced **AI Tutor platform**, powered by Retrieval-Augmented Generation (RAG).  
This system delivers answers **grounded in real data**, not just language model guesses—and explains and grades them too!

---

- 🔙 [Backend: RAG Chat API](https://github.com/para0107/enhanced-llm-with-rag)
- 🖼️ [Frontend: Chat Interface](https://github.com/para0107/rag-llm-frontend)

---

## 🚀 What Is This?

This project is a **multi-dataset, retrieval-augmented chatbot and auto-grader**.  
It combines:

- FastAPI for modern web APIs
- LangChain for composable LLM and retrieval chains
- Hugging Face models for embeddings and generation
- FAISS for lightning-fast semantic search
- BLEU/ROUGE metrics and LLM-based judge for instant, actionable answer evaluation

**Key Features:**
- **Chatbot answers are based on real knowledge, not just “made up” by an LLM.**
- **Toxic or hallucinated answers are filtered out for safety.**
- **BLEU/ROUGE scores show how close each answer is to “gold standard” references.**
- **LLM-Judge endpoint instantly grades answers for correctness and reasoning quality.**

---

## 🧠 How the System Works

### 1. Data Collection & Preparation

- Loads and preprocesses **multiple datasets**:
  - Conversational logs (`chat-history.json`)
  - Intent classification pairs (`intents.json`)
  - Coding problems (MBPP)
  - Math problems (GSM8K)
- **All data is unified** into “input/target” pairs for easy retrieval.

### 2. Chunking & Embedding

- **Splits data into overlapping chunks** (e.g., 1000 tokens, 200 overlap) to allow focused retrieval and avoid context loss.
- **Each chunk is embedded** using a sentence-transformer model, turning text into a dense vector that “captures its meaning.”

### 3. Fast Semantic Search (FAISS)

- All vectors are stored in a **FAISS index**, a high-speed search engine for semantic similarity.
- When a question comes in, it’s embedded and **the system finds the most relevant chunks of info** (top-k) from the knowledge base.

### 4. Retrieval-Augmented Answer Generation (RAG)

- The question and retrieved context are **passed to a large language model (LLM)** (e.g., Llama 3.1-8B via LM Studio).
- **LLM generates the answer based only on the supporting evidence**—never “just from memory.”
- Prompting is fully customizable for your preferred answer style.

### 5. API Layer

#### `/rag_chat` — Main Chatbot Endpoint

- Receives user question and conversation history
- **Sanitizes old messages:** Removes LLM hallucinated or wrong math answers
- **If a math question:** Directly evaluates and replies (bypasses LLM)
- Otherwise:
  - Retrieves relevant knowledge chunks
  - Passes them to the LLM for a grounded answer
- **Safety Filters:**
  - Blocks unsafe/toxic responses
  - Warns if the answer is not supported by the retrieved content (“hallucination filter”)
- **Metrics:** Optionally computes BLEU/ROUGE scores vs. reference answers
- **All chat history is saved and returned**

#### `/evaluate` — LLM-Judge Endpoint

- Receives a question + answer (from user, model, or student)
- Uses a separate LLM “judge” to grade the answer for **correctness and reasoning**
- Returns a verdict, score (0–1), and brief comments

---

## 🛡️ Safety & Reliability

- Arithmetic answers are **double-checked by code**, not just the LLM
- **Toxicity filter** blocks unsafe or inappropriate language
- **Hallucination filter** ensures answers are actually grounded in the context

---

## 📊 Metrics: BLEU & ROUGE

- **BLEU**: How much does the answer look like the official answer (phrases/wording)?
- **ROUGE**: Did the answer include all the important points/content?
- Both scores are included if reference data exists—so you always know “how good was this answer?”

---

## 📑 Example Usage

### Start the API
```bash
uvicorn your_script_name:app --reload
```json
POST /evaluate
{
  "question": "What is 2+2?",
  "answer": "It is 4 because 2 plus 2 is 4."
}
```
## 🧩 Code Structure — Main Components

| File/Section            | Purpose                                                    |
|-------------------------|------------------------------------------------------------|
| `chat-history.json`     | Conversational data for retrieval and context              |
| `intents.json`          | Intent pairs for classification and question answering     |
| **Data Preparation**    | Loads and formats all data into (input, target) pairs      |
| **Chunking**            | Splits data for efficient retrieval (RAG chunking logic)   |
| **FAISS Index**         | Enables fast semantic search over all knowledge            |
| **RetrievalQA (`qa_chain`)** | Core RAG pipeline — retrieves context, generates answers |
| **FastAPI Endpoints**   | `/rag_chat` and `/evaluate` for chat and LLM-based grading|
| **Safety Filters**      | Checks for hallucinated, toxic, or incorrect answers       |
| **BLEU/ROUGE Metrics**  | Real-time answer scoring versus ground truth               |
| **LLM-Judge (`/evaluate`)** | Automated grading with structured feedback          |

---

## 🌟 Why RAG? Why This Project?

- **Retrieval-Augmented Generation** means the AI is never “just making things up”—it finds and uses real information to answer.
- **Trustworthy answers:** Every LLM response is based on actual, retrievable knowledge, not just language model “imagination.”
- **Continuous self-evaluation:** BLEU/ROUGE metrics and LLM-judge grading provide actionable feedback on every answer.
- **Extensible:** Add more datasets, plug in new LLMs, or refine prompts and retrieval strategies as needed.

---

## 🧠 How Answers Are Generated: LLM + RAG “Chain of Thought”

Retrieval-Augmented Generation (RAG) changes the way a language model “thinks” about your questions.  
Instead of guessing from memory, it **actively looks up knowledge**, then reasons and answers using those real facts.

### Step-by-Step: The RAG Chain of Thought

1. **User Asks a Question**
    - The user sends a query (e.g., *“Explain binary search”*) to the API.

2. **Retrieve Relevant Knowledge**
    - The system **embeds the user’s question** as a vector.
    - It then **searches the FAISS index** for the most similar document chunks from its curated knowledge base (these come from textbooks, tutorials, code, solved examples, etc.).
    - *Example:* For “binary search”, it might pull up a Python code example, a step-by-step explanation, and a textbook definition.

3. **Builds a Rich Context**
    - The retrieved chunks are **concatenated into a “context window.”**
    - This context is paired with the user’s question.
    - *Result:* The LLM sees not just the question, but also high-quality supporting evidence.

4. **LLM “Reads” and Reasons**
    - The LLM **reads both the user’s question and the retrieved context.**
    - Using its language understanding and reasoning abilities, it **chains together facts and explanations** from the context to build its answer.
    - If prompted for chain-of-thought, it may break the answer into clear, logical steps, citing evidence from the retrieved material.

5. **Answer Generation**
    - The LLM **generates an answer**—ideally:
        - Using the relevant terminology, code, or facts it found in the retrieval step
        - Explaining step-by-step if the prompt encourages “chain of thought”
        - Avoiding hallucinations, since it grounds each statement in evidence

6. **Safety & Evaluation**
    - Before the answer is returned, it goes through:
        - **Toxicity and hallucination filters**: To block unsafe or unsupported answers.
        - **(Optional) Metrics**: BLEU/ROUGE scores or LLM-Judge grading if enabled.

7. **Final Answer + Evidence**
    - The user receives:
        - The answer (reasoned and well-grounded)
        - (If enabled) The sources or context that supported the answer
        - (If enabled) An evaluation of answer quality

---

### 📈 Why This “Chain of Thought” Matters

- **Transparency:** Users can see *where the answer came from*.
- **Trustworthiness:** Every statement is grounded in real, retrieved knowledge, not just “AI imagination.”
- **Better Reasoning:** The LLM can connect multiple relevant facts, leading to more logical, step-by-step explanations.
- **Continuous Improvement:** Evaluation metrics let you spot when the chain of thought breaks down—so you can refine retrieval, prompts, or model settings.

---

### 📝 Example (Pseudo-Transcript)

**User:**  
“How does binary search work?”

**RAG Process:**  
1. *Retrieves* textbook chunk: “Binary search splits the sorted array, checking the middle element...”
2. *Retrieves* code example: “def binary_search(arr, target): ...”
3. *LLM reads context, generates:*  
   - “To perform binary search:
       1. Start with the middle of the sorted list.
       2. If the target is less, repeat with the left half; if more, with the right half.
       3. Repeat until found or interval is empty.
    

---


## 🔧 Extending & Customizing

- **Add new datasets:** Preprocess them and include them in the data merge step for richer knowledge.
- **Change embedding models or chunk sizes:** Improve retrieval precision or context as needed.
- **Swap LLMs:** Use OpenAI, local LM Studio, or any OpenAI-compatible provider.
- **Refine prompts:** Adjust the answer style, reasoning, or response logic for your needs.

---

## 🤝 Credits

- [LangChain](https://python.langchain.com/)
- [HuggingFace Transformers](https://huggingface.co/)
- [FAISS](https://faiss.ai/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

**This RAG Tutor API is a robust foundation for building reliable, explainable, and evaluative AI tutors—ideal for education, research, or next-gen AI products.**

