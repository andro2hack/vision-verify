import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import io

# Load pre-trained model (MobileNetV2 is fast and good enough)
# We use it in eval mode for feature extraction
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
model.eval()

# Remove the classifier layer to get the embeddings
# MobileNetV2 features are in model.features, but we need the pooling too.
# A commmon way is to use a forward hook or just wrap it.
class FeatureExtractor(torch.nn.Module):
    def __init__(self, original_model):
        super(FeatureExtractor, self).__init__()
        self.features = original_model.features
        self.pooling = torch.nn.AdaptiveAvgPool2d((1, 1))
        
    def forward(self, x):
        x = self.features(x)
        x = self.pooling(x)
        return torch.flatten(x, 1)

feature_extractor = FeatureExtractor(model)

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def get_embedding(image_bytes: bytes) -> np.ndarray:
    """Computes the embedding vector for an image."""
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        input_tensor = preprocess(image)
        input_batch = input_tensor.unsqueeze(0)  # Add batch dimension

        with torch.no_grad():
            output = feature_extractor(input_batch)
        
        return output.numpy().flatten()
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def cosine_similarity(embedding1, embedding2):
    """Calculates cosine similarity between two embeddings."""
    if embedding1 is None or embedding2 is None:
        return 0.0
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.dot(embedding1, embedding2) / (norm1 * norm2)
