import torch
import torchvision.models as models
import torchvision.transforms as transforms
from ultralytics import YOLO
from PIL import Image
import numpy as np
import os

# Global Loaders for Performance
_resnet_model = None
_yolo_model = None

def get_resnet_model():
    global _resnet_model
    if _resnet_model is None:
        print("Loading ResNet50...")
        _resnet_model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        # Remove the classification layer (last fc layer)
        _resnet_model = torch.nn.Sequential(*list(_resnet_model.children())[:-1])
        _resnet_model.eval()
    return _resnet_model

def get_yolo_model():
    global _yolo_model
    if _yolo_model is None:
        print("Loading YOLOv8...")
        model_path = 'yolov8n.pt'
        if not os.path.exists(model_path):
             # Fallback to sibling directory
             possible_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'retail_audit_pgvector', 'yolov8n.pt')
             if os.path.exists(possible_path):
                 model_path = possible_path
        _yolo_model = YOLO(model_path)
    return _yolo_model

def get_image_embedding(image_path_or_pil):
    """
    Generates a 2048-dim embedding for an image using ResNet50.
    """
    model = get_resnet_model()
    
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    if isinstance(image_path_or_pil, str):
        img = Image.open(image_path_or_pil).convert('RGB')
    else:
        img = image_path_or_pil.convert('RGB')

    img_tensor = preprocess(img).unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        embedding = model(img_tensor)
        
    # Flatten: [1, 2048, 1, 1] -> [2048]
    return embedding.squeeze().numpy()

def detect_objects(image_path):
    """
    Uses YOLOv8 to detect 'bottle' (class 39).
    Returns list of dicts: {'box': [x1, y1, x2, y2], 'crop': PIL_Image}
    """
    model = get_yolo_model()
    img = Image.open(image_path)
    
    # Run inference for all classes, not just bottles
    # Using a lower confidence threshold to ensure we pick up candidates
    results = model(img, conf=0.25, verbose=False)
    
    detections = []
    
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            # Crop the object
            crop = img.crop((x1, y1, x2, y2))
            detections.append({
                'box': [x1, y1, x2, y2],
                'crop': crop
            })
            
    return detections

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
