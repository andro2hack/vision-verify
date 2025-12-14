# Product Requirements Document (PRD): Vision Verify

## 1. Problem Statement & Objective
**The Challenge:** E-commerce fraud is escalating, with bad actors increasingly using manipulated media to deceive platforms and customers. Common schemes include:
- **Identity Fraud:** Using stolen or AI-generated faces to bypass verification.
- **Listing Fraud:** Using stock images or stolen photos to list non-existent products.
- **Deepfake Scams:** Creating realistic AI-generated images to fake evidence or product quality.

**The Objective:** To build **Vision Verify**, a centralized image forensics engine that restores trust in digital transactions. By analyzing image origin, authenticity, and consistency, we aim to drastically reduce fraud losses and manual review time for e-commerce platforms.

---

## 2. Solution Breakdown
Vision Verify tackles this problem through three distinct forensic pillars.

### Pillar 1: Identity Match (Database Verification)
**Layman Explanation:**
Think of this as a digital ID check. When a seller or user submits a photo (like a selfie or ID card), the system compares it against a private list of "trusted" or "banned" faces. It confirms if this person is who they say they are, or if they’ve been flagged before.

**Technical Explanation:**
- **Mechanism:** Vector Similarity Search.
- **Process:**
    1. The uploaded image is passed through a **Convolutional Neural Network (MobileNetV2)**.
    2. The network extracts a high-dimensional feature vector (embedding).
    3. This vector is compared against stored vectors in the database using **Cosine Similarity**.
    4. If the similarity score exceeds a threshold (e.g., 0.8), a match event is triggered.

### Pillar 2: Internet Check (Source Tracing)
**Layman Explanation:**
This checks if an image is "fresh" or recycled. If a seller claims to be selling a unique vintage watch, but our system finds that exact photo on 50 other websites or stock photo libraries, we know the listing is likely fake.

**Technical Explanation:**
- **Mechanism:** Reverse Image Search / Web Detection.
- **Process:**
    1. The image is hashed and sent to the **Google Cloud Vision API**.
    2. The API performs web entity detection and full/partial image matching across the indexed web.
    3. The backend parses the returned JSON to identify "Full Matching Images" (duplicates) and "Pages with Matching Images" (context).
    4. A heuristic score is calculated: High presence on public URLs = Low Uniqueness Score.

### Pillar 3: AI Detection (Deepfake Analysis)
**Layman Explanation:**
This tool acts like a microscope for digital forgery. It looks for invisible signs that an image was created by a computer program (like Midjourney or DALL-E) rather than a camera sensor, helping to spot fake product photos or generated profiles.

**Technical Explanation:**
- **Mechanism:** Frequency Analysis / Artifact Detection (CNN Binary Classifier).
- **Process:**
    1. The image is analyzed for specific GAN (Generative Adversarial Network) fingerprints, such as upsampling artifacts or irregular pixel correlations in the Fourier domain.
    2. A probabilistic score (0-100%) is returned indicating the likelihood of the image being synthetic.

---

## 3. Technical Architecture & Process Flow
**How it Works Under the Hood:**

1.  **Frontend (React/Vite):** The user interface where officers upload images. It handles file validation and displays visual results (charts, match confidence).
2.  **API Layer (FastAPI):**
    - Acts as the traffic controller.
    - Receives images → Converts to Bytes → Routes to specific forensic modules.
3.  **Forensic Modules:**
    - `image_utils.py`: Runs local PyTorch models for embedding generation.
    - `main.py`: Orchestrates calls to external APIs (Google Cloud).
4.  **Data Flow:**
    - Images are processed in-memory for speed and privacy.
    - Only mathematical representations (vectors) or metadata needs to be stored long-term.

---

## 4. Cost Analysis (Full Scale)
*Estimates based on processing 100,000 images/month.*

### 1. Infrastructure (Compute)
-   **Service:** GPU-accelerated instances (e.g., AWS g4dn.xlarge) are needed for fast AI/Deepfake detection at scale.
-   **Cost:** ~$500 - $800 / month.
-   *Note: For lower volume, CPU-only instances (t3.xlarge) at ~$150/month are sufficient.*

### 2. External APIs (Google Cloud Vision)
-   **Service:** Web Detection feature.
-   **Pricing:** First 1,000 free. ~$1.50 per 1,000 images thereafter.
-   **Cost:** 99k images * ($1.50/1k) ≈ **$148.50 / month**.

### 3. Bandwidth & Storage
-   **Service:** S3 Storage + Data Transfer.
-   **Cost:** ~$50 / month (assuming images are archived for audit trails).

### **Total Estimated Monthly Cost:** ~$350 - $1,000
*(Depending on whether dedicated GPUs are used or serverless CPU functions).*

---

## 5. ROI & Business Value
-   **Fraud Prevention:** Stopping just **one** major bulk-fraud ring (e.g., 50 fake iPhone listings) can save platforms over $50,000 in chargebacks and reputation damage.
-   **Operational Efficiency:** Automating image review reduces manual moderation team size or allows them to focus on complex cases.

---

## 6. How to Deploy (Deployment Guide)

### Prerequisites
-   **Python 3.9+** and **Node.js 18+**.
-   **Google Cloud Account** with `Cloud Vision API` enabled.
-   **Service Account JSON** file for authentication.

### Step 1: Backend Setup
1.  Navigate to the `backend` folder.
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Place your Google Cloud credentials file as `service_account.json` in the `backend/` directory.
4.  Start the server (runs on port 8001):
    ```bash
    python main.py
    ```

### Step 2: Frontend Setup
1.  Navigate to the `frontend` folder.
2.  Install Node dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    *Note: If you encounter policy errors on Windows, use `cmd /c "npm run dev"`.*

### Step 3: Usage
1.  Open your browser to `http://localhost:5173`.
2.  Upload images to test against the database, check internet sources, or analyze for AI generation.
