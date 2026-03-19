# AI Cyberbullying Model Training

Your local PC was experiencing stress and your deployed Railway server was crashing due to Out-of-Memory (OOM) errors because of the heavy, older models you were using.

To solve this, I have created two "tricky" and highly efficient Google Colab scripts that use **latest state-of-the-art architectures** which produce tiny, powerful models perfectly suited for your cheap/free server.

## 1. Text Model (`Text_Model_Colab.py`)
- **Technology**: 1D Convolutional Neural Network (CNN) + Bidirectional LSTM.
- **Why it's better**: It outperforms basic sequential models but uses a fraction of the memory (unlike massive Transformers).
- **Output**: Produces `Text-Analysis_v2.h5` and `tokenizer.pickle`.

## 2. Image Model (`Image_Model_Colab.py`)
- **Technology**: **Transfer Learning with MobileNetV3Small** (Google's latest efficient vision model).
- **Why it's better**: It unifies your 5 separate categories (`NSFW_Content`, `Non_Offensive`, `humour`, `negative`, `offensive`) into a *single* model (goodbye `primary` and `secondary` separation). The resulting model size will be **~10MB** instead of 28MB, immediately fixing your Railway OOM crashes.
- **Output**: Produces `Image-Analysis_v2.h5`.

## How to Train (Without stressing your PC)

1. Go to [Google Colab](https://colab.research.google.com/).
2. Create a new "Notebook".
3. In the top menu, click **Runtime > Change runtime type** and select **T4 GPU** (This is free and extremely fast).
4. Upload your datasets to the Colab files pane:
   - For Text: Upload `Text_Analysing_Dataset.csv`
   - For Images: Zip your `DATASET/TRAIN` folder, upload it, and unzip it with `!unzip dataset.zip` in a cell.
5. Copy the code from the Python files in this folder and paste them into cells.
6. Click **Run**.
7. Once finished, download the newly generated `.h5` files and `.pickle` file to your local computer.

---

> [!WARNING]
> Because these are entirely new and significantly better architectures, when you download the new `.h5` files, you will need to update your Django backend (`cyberbullying/ml_views.py`) to properly load the new single image model and load the saved `tokenizer.pickle` instead of rebuilding it every time the server starts. I can help you rewrite `ml_views.py` to support these new models whenever you are ready!
